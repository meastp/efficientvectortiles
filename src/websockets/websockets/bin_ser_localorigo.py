from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from shapely.wkb import loads

import psycopg2

import json

import array

def create_vector_tile(minx, miny, maxx, maxy):
    connection = psycopg2.connect("dbname='vectordata' user='postgres' host='localhost' password='pass'")
    #connection.set_session(readonly=True)
    cursor = connection.cursor()
    
    query = """WITH 
                  box_extent as (
                    select st_setsrid(box2d(ST_GeomFromText('LINESTRING("""+str(minx)+""" """+str(miny)+""", """+str(maxx)+""" """+str(maxy)+""")')),25832) as box
                    ),
                  matches AS (
                    select ST_AsText(intersection(geom, box)) as geom, box from "VEG", box_extent
                      where not ST_IsEmpty(intersection(geom, box))
                    ),
                  geocollection AS (
                    SELECT ST_Collect(geom) as geom from matches
                    ),
                  tile_row AS (
                    select box as tile_box, geom as tile from geocollection, box_extent
                    )
                insert into veg_tiles(tile_box, tile) select * from tile_row
            """
    
    
    cursor.execute(query)
    
    connection.commit()

def create_sample_tiles(minx, miny, maxx, maxy):
    
    xr = range(minx, maxx, 255)
    yr = range(miny, maxy, 255)
    
    for x in xr :
      for y in yr :
        create_vector_tile(x,y,x+255,y+255)
    


#minx = 583000
#maxx = 584000
#miny = 6644000
#maxy = 6645000

#create_sample_tiles(minx, miny, maxx, maxy)

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
    
    assert maxx-minx < 65536-5000
    assert maxy-miny < 65536-5000
    
    self.cursor = self.connection.cursor()
    #self.cursor.execute("""select ST_AsBinary(st_transform(st_simplify(geom,1),4326)) from "VEG" """)
    #self.cursor.execute("""select ST_AsBinary(geom) from "VEG" limit 100 where geom &&  box2d(ST_GeomFromText('LINESTRING(583000 6644000, 584000 6645000)'))""")
    #self.cursor.execute("select ST_AsBinary(geom) from \"VEG\" where geom && box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")'))")
    #self.cursor.execute("select ST_AsBinary(geom) from \"VEG\" where geom && box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")'))")
    self.cursor.execute("select ST_AsBinary(geom) from \"VEGSIMPLE1\" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")')),25832)")
    #self.cursor.execute("select ST_AsBinary(geom) from \"VEGSIMPLE2p5\" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")')),25832)")
    #self.cursor.execute("select ST_AsBinary(geom) from \"VEGSIMPLE5\" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")')),25832)")
    results = self.cursor.fetchall()
    size = len(results)
    
    header = array.array('L', [size,0])
    sub_headers = array.array('H')
    data = array.array('H')
    
    for result in results:
        obj = loads(array.array('c',result[0]).tostring())
        
        sub_header = array.array('H', [len(obj.coords),0,0,0])
        
        sub_headers.extend(sub_header)
        
        for x,y in obj.coords:
            #print maxx, x, int(maxx-x)+2500
            #print maxy, y, int(maxy-y)+2500
            data.append(int(maxx-x)+2500)
            data.append(int(maxy-y)+2500)
    
    result_data = header.tostring()+sub_headers.tostring()+data.tostring()
    
    #print header
    #print sub_headers
    
    print "Conversion finished"
    
    self.sendMessage(result_data, binary=True)
    
    print "Message sent"

if __name__ == '__main__':

   factory = WebSocketServerFactory("ws://localhost:9090")
   factory.protocol = VectorServerProtocol
   listenWS(factory)
   reactor.run()
