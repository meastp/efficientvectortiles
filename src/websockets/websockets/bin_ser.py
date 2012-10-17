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
    #self.cursor.execute("""select ST_AsBinary(st_transform(st_simplify(geom,1),4326)) from "VEG" """)
    #self.cursor.execute("""select ST_AsBinary(geom) from "VEG" limit 100 where geom &&  box2d(ST_GeomFromText('LINESTRING(6644000 583000, 6645000 584000)'))""")
    #self.cursor.execute("select ST_AsBinary(geom) from \"VEG\" where geom && box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")'))")
    #print "select ST_AsBinary(geom) from \"VEGSIMPLE1\" where geom && box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")', 25832))"
    self.cursor.execute("select ST_AsBinary(geom) from \"VEGSIMPLE1\" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(minx)+" "+str(miny)+", "+str(maxx)+" "+str(maxy)+")')),25832)")
    results = self.cursor.fetchall()
    size = len(results)
    
    header = array.array('L', [size,0])
    sub_headers = array.array('H')
    data = array.array('d')
    
    for result in results:
        obj = loads(array.array('c',result[0]).tostring())
        
        sub_header = array.array('H', [len(obj.coords),0,0,0])
        
        sub_headers.extend(sub_header)
        
        for x,y in obj.coords:
            data.append(x)
            data.append(y)
    
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
