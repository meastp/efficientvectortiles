from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from shapely.wkb import loads

import psycopg2

import json

import array

def create_vector_tile(minx, miny, maxx, maxy, fromtablename, totablename, options=None):
    connection = psycopg2.connect("dbname='vectordata' user='postgres' host='localhost' password='pass'")
    #connection.set_session(readonly=True)
    cursor = connection.cursor()
    
    geometry = "geom"
    
    if options != None :
        if options['simplify'] == True and options['simplify_amount'] :
            geometry = "st_simplify(geom,"+str(options['simplify_amount'])+")"
    
    query = """WITH 
                  box_extent as (
                    select st_setsrid(box2d(ST_GeomFromText('LINESTRING("""+str(minx)+""" """+str(miny)+""", """+str(maxx)+""" """+str(maxy)+""")')),25832) as box
                    ),
                  matches AS (
                    select intersection("""+geometry+""", box) as geom, box from """+fromtablename+""", box_extent
                      where ST_IsValid("""+geometry+""") and ST_IsValid(intersection("""+geometry+""", box)) and not ST_IsEmpty(intersection("""+geometry+""", box))
                    ),
                  geocollection AS (
                    SELECT ST_Collect(geom) as geom from matches
                    ),
                  tile_row AS (
                    select box as tile_box, geom as tile from geocollection, box_extent where not ST_IsEmpty(geom)
                    )
                insert into """+totablename+"""(tile_box, tile) select * from tile_row
            """
    
    cursor.execute(query)
    
    connection.commit()
    

def create_sample_tiles(minx, miny, maxx, maxy, fromtablename, totablename, simplify=None):
    
    xr = range(minx, maxx, 255)
    yr = range(miny, maxy, 255)
    
    tile = 0
    
    for x in xr :
      for y in yr :
        tile += 1
        #print "Starting Tile #"+str(tile)
        try :
            create_vector_tile(x,y,x+255,y+255, fromtablename, totablename, simplify)
        except psycopg2.Error, e :
            print "Error: "
            print "       ", x, y, fromtablename, totablename, simplify
            print "       ",e.pgerror
            print "       ",e.pgcode
        
        #print "Completed Tile #"+str(tile)
    
    print "Completed" + totablename

def gentiles():
    
    #bminx = 583000
    #bmaxx = 584000
    #bminy = 6644000
    #bmaxy = 6645000
    
    bminx = 574500
    bmaxx = 592500
    bminy = 6635000
    bmaxy = 6657000
    
    fromnames = ['"Bygning"', '"DekTeig"', '"KantUtsnitt"' ] #'"AnnenBygning"', '"ArealressursFlate"', 
    raw_to_names = ['bygning', 'dek_teig', 'kant_utsnitt']#'annen_bygning', 'areal_ressurs_flate', 
    tonames = ['map_'+name+'_tiles' for name in raw_to_names]
    tonames_simple = ['map_'+name+'_tiles_simple1' for name in raw_to_names]
    options = { 'simplify' : True, 'simplify_amount' : 1.0 }
    for i, fromname in enumerate(fromnames) :
        #create_sample_tiles(bminx, bminy, bmaxx, bmaxy, fromname, tonames[i])
        create_sample_tiles(bminx, bminy, bmaxx, bmaxy, fromname, tonames_simple[i], options)
        
    
    #create_sample_tiles(bminx, bminy, bmaxx, bmaxy)

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
    
    self.cursor.execute("select ST_AsBinary(tile_box), ST_AsBinary(tile) from map_veg_tiles where tile_box && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")')),25832)")
    
    results = self.cursor.fetchall()
    size = len(results)
    
    #print results 
    #print size
    
    
    
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
                print geom.geom_type
                if geom.geom_type=="Point":
                    pass
                elif geom.geom_type=="GeometryCollection" and geom.geoms == []:
                    pass
                else:
                    assert False
        
        
        tile_headers.extend(array.array('d',[num_geometries, bboxminx, bboxminy]))
    
    print "Tiles: ", size
    
    print header, tile_headers, geometry_headers_type, geometry_headers_nocoordinates
    print len(header), len(tile_headers), len(geometry_headers_type), len(geometry_headers_nocoordinates)
    print data[:20], data[-20:]
    #print data
    
    result_data = header.tostring()+tile_headers.tostring()+geometry_headers_nocoordinates.tostring()+geometry_headers_type.tostring()+data.tostring()
    
    print "Conversion finished"
    
    self.sendMessage(result_data, binary=True)
    
    print "Message sent"

if __name__ == '__main__':

   factory = WebSocketServerFactory("ws://localhost:9090")
   factory.protocol = VectorServerProtocol
   listenWS(factory)
   reactor.run()
