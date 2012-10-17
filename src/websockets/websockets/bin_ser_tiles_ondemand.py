from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from shapely.wkb import loads

import psycopg2

import json

import array

class VectorServerProtocol(WebSocketServerProtocol):
  
  def onOpen(self):
    print "New connection"
    
    self.connection = psycopg2.connect("dbname='vectordata' user='postgres' host='localhost' password='pass'")
    self.connection.set_session(readonly=True)
    
    
  def onMessage(self, data, is_binary):
    
    assert is_binary
    
    msg = array.array('d', data)
    
    minx, maxx, miny, maxy = [long(no) for no in msg]
    #print minx,maxx,miny,maxy
    
    self.cursor = self.connection.cursor()
    
    xr = range(minx, maxx, 255)
    yr = range(miny, maxy, 255)
    
    tiles = []
    
    for x in xr :
        for y in yr :
            
            
            query = """WITH 
                          box_extent as (
                            select st_setsrid(box2d(ST_GeomFromText('LINESTRING("""+str(x)+""" """+str(y)+""", """+str(x+255)+""" """+str(y+255)+""")')),25832) as box
                            ),
                          matches AS (
                            select intersection(geom, box) as geom, box from "VEG", box_extent
                              where not ST_IsEmpty(intersection(geom, box))
                            ),
                          geocollection AS (
                            SELECT ST_Collect(geom) as geom from matches
                            )
                            select ST_AsBinary(box), ST_AsBinary(geom) from geocollection, box_extent where not ST_IsEmpty(geom)
            """
            
            self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            
            boundingbox, tile = results[0]
            
            if len(results) > 0 :
                tiles.append([loads(array.array('c',boundingbox).tostring()), loads(array.array('c',tile).tostring())])
            
            print "Tile (",x,y,x+255,y+255,") Finished"
            
    
    
    
    size = len(tiles)
    
    header = array.array('L', [size, 0]) # contains the number of tiles in the data packet
    tile_headers = array.array('d') # contains the number of geometry objects in the tile and bounds
    geometry_headers = array.array('H') # contains the number of coordinates in the geometry (up to 65536)
    data = array.array('B') # contains the coordinates
    
    for tile in tiles:
        
        
        bbox = tile[0]
        bboxminx,bboxminy,bboxmaxx,bboxmaxy = bbox.bounds
        
        geometry_collection = tile[1]
        
        
        num_geometries = 0
        
        for geom in geometry_collection.geoms:
            
            if geom.geom_type == "LineString": #type 1
                
                geometry_headers.extend(array.array('H', [len(geom.coords)]))
                
                num_geometries += 1
                
                for x,y in geom.coords:
                    #print x-bboxminx
                    data.append(int(x-bboxminx))
                    data.append(int(y-bboxminy))
                
                
            elif geom.geom_type == "MultiLineString":
                
                num_geometries += len(geom.geoms)
                
                for geometry in geom.geoms:
                    
                    geometry_headers.extend(array.array('H', [len(geometry.coords)]))
                    
                    for x,y in geometry.coords:
                        #print x-bboxminx
                        data.append(int(x-bboxminx))
                        data.append(int(y-bboxminy))
                
                
            else:
                print geom.geom_type
                assert False
        
        
        tile_headers.extend(array.array('d',[num_geometries, bboxminx, bboxminy]))
    
    print "Tiles: ", size
    
    #print header, tile_headers, geometry_headers
    #print len(header), len(tile_headers), len(geometry_headers)
    #print data[:20], data[-20:]
    #print data
    
    result_data = header.tostring()+tile_headers.tostring()+geometry_headers.tostring()+data.tostring()
    
    print "Conversion finished"
    
    self.sendMessage(result_data, binary=True)
    
    print "Message sent"

if __name__ == '__main__':

   factory = WebSocketServerFactory("ws://localhost:9090")
   factory.protocol = VectorServerProtocol
   listenWS(factory)
   reactor.run()
