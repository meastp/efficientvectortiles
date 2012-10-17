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
    
    minx, maxx, miny, maxy = msg
    #print minx,maxx,miny,maxy
    
    self.cursor = self.connection.cursor()
    
    #tables = {'map_annen_bygning_tiles' : 'ANNENBYG', 'map_areal_ressurs_flate_tiles' : 'AREALREF', 'map_bygning_tiles' : 'BYGNINGT', 'map_dek_teig_tiles' : 'DELTEIGT', 'map_kant_utsnitt_tiles' : 'KANTUTSN', 'map_veg_tiles' : 'VEGTILES'}
    
    tables = {'map_annen_bygning_tiles' : 'ANNENBYG', 'map_bygning_tiles' : 'BYGNINGT', 'map_veg_tiles' : 'VEGTILES'}
    #tables = {'map_annen_bygning_tiles_simple1' : 'ANNENBYG', 'map_bygning_tiles_simple1' : 'BYGNINGT', 'map_veg_tiles_simple1' : 'VEGTILES'}
    
    for table_name, short_table_name in tables.items() :
        
        print short_table_name
        assert(len(short_table_name)==8)
        
        self.cursor.execute("select ST_AsBinary(tile_box), ST_AsBinary(tile) from "+table_name+" where tile_box && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")')),25832)")
        
        results = self.cursor.fetchall()
        size = len(results)
        
        #print results 
        #print size
        
        
        
        table_name_header = array.array('c', short_table_name)
        header = array.array('L', [size, 0]) # contains the number of tiles in the data packet
        tile_headers = array.array('d') # contains the number of geometry objects in the tile and bounds
        geometry_headers_nocoordinates = array.array('H') # contains the number of coordinates in the geometry (up to 65536)
        geometry_headers_type = array.array('B') # contains the geometry type
        data = array.array('B') # contains the coordinates
        
        for tile in results:
            
            
            bbox = loads(array.array('c',tile[0]).tostring())
            bboxminx,bboxminy,bboxmaxx,bboxmaxy = bbox.bounds
            
            geometry_collection = loads(array.array('c',tile[1]).tostring())
            
            
            num_geometries = 0
            
            for geom in geometry_collection.geoms:
                
                if geom.geom_type == "LineString": #type 1
                    
                    geometry_headers_nocoordinates.extend(array.array('H', [len(geom.coords)]))
                    geometry_headers_type.append(1)
                    
                    num_geometries += 1
                    
                    for x,y in geom.coords:
                        data.append(int(x-bboxminx))
                        data.append(int(y-bboxminy))
                    
                elif geom.geom_type == "Polygon" : #type 2
                    
                    geometry_headers_nocoordinates.extend(array.array('H', [len(geom.exterior.coords)-1]))
                    geometry_headers_type.append(2)
                    
                    num_geometries += 1
                    
                    for x,y in list(geom.exterior.coords)[:-1]:
                        data.append(int(x-bboxminx))
                        data.append(int(y-bboxminy))
                    
                    for interior in geom.interiors :
                        geometry_headers_nocoordinates.extend(array.array('H', [len(interior.coords)-1]))
                        geometry_headers_type.append(3)
                        
                        num_geometries += 1
                        
                        for x,y in list(interior.coords)[:-1] :
                            data.append(int(x-bboxminx))
                            data.append(int(y-bboxminy))
                    
                elif geom.geom_type == "MultiLineString":
                    
                    for geometry in geom.geoms:
                        
                        geometry_headers_nocoordinates.extend(array.array('H', [len(geometry.coords)]))
                        geometry_headers_type.append(1)
                        
                        num_geometries += 1
                        
                        for x,y in geometry.coords:
                            data.append(int(x-bboxminx))
                            data.append(int(y-bboxminy))
                
                elif geom.geom_type == "MultiPolygon":
                
                    for geometry in geom.geoms :
                        
                        geometry_headers_nocoordinates.extend(array.array('H', [len(geometry.exterior.coords)-1]))
                        geometry_headers_type.append(2)
                        
                        num_geometries += 1
                        
                        for x,y in list(geometry.exterior.coords)[:-1]:
                            data.append(int(x-bboxminx))
                            data.append(int(y-bboxminy))
                        
                        for interior in geometry.interiors :
                            geometry_headers_nocoordinates.extend(array.array('H', [len(interior.coords)-1]))
                            geometry_headers_type.append(3)
                            
                            num_geometries += 1
                            
                            for x,y in list(interior.coords)[:-1] :
                                data.append(int(x-bboxminx))
                                data.append(int(y-bboxminy))
                
                    
                else:
                    #print geom.geom_type
                    if geom.geom_type=="Point":
                        pass
                    elif geom.geom_type=="GeometryCollection" and geom.geoms == []:
                        pass
                    else:
                        assert False
            
            
            tile_headers.extend(array.array('d',[num_geometries, bboxminx, bboxminy]))
        
        print "Tiles: ", size
        
        #print header, tile_headers, geometry_headers_type, geometry_headers_nocoordinates
        #print len(header), len(tile_headers), len(geometry_headers_type), len(geometry_headers_nocoordinates)
        #print data[:20], data[-20:]
        #print data
        
        result_data = table_name_header.tostring()+header.tostring()+tile_headers.tostring()+geometry_headers_nocoordinates.tostring()+geometry_headers_type.tostring()+data.tostring()
        
        print "Conversion finished"
        
        self.sendMessage(result_data, binary=True)
        
        print "Message sent"
    
    print "All layers sent"

if __name__ == '__main__':

   factory = WebSocketServerFactory("ws://localhost:9090")
   factory.protocol = VectorServerProtocol
   listenWS(factory)
   reactor.run()
