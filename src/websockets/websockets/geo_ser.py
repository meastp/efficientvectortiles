from twisted.internet import reactor
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

import psycopg2

import json

class ResultObject:
  def __init__(self, result):
    self.result = result

class DbConnection:
  def __init__(self):
    self.connection = psycopg2.connect("dbname='vectordata' user='postgres' host='localhost' password='pass'")
    self.connection.set_session(readonly=True)
    print "Connected"

class QueryObject:
  def __init__(self, dbconnectionobj):
    self.cursor = dbconnectionobj.connection.cursor()
  
  def query(self, query):
    print "Query initiated"
    self.cursor.execute(query)
    print "Query complete"
    result = self.cursor.fetchall()
    print "Results fetched"
    return result

class VectorServerProtocol(WebSocketServerProtocol):
  def onOpen(self):
    self.dbconnection = DbConnection()
    dbquery = QueryObject(self.dbconnection)
    #result = dbquery.query("""select st_asgeojson(st_transform(geom,4326)) from "VEG" limit 1000""")
   # dbquery.cursor.execute("""select st_asgeojson(st_transform(geom,4326),5) from "VEG" where geom && Box2D(ST_GeomFromText('LINESTRING(586000 6640000,590000 6645000)'))""")
    dbquery.cursor.execute("""select st_asgeojson(st_transform(st_simplify(geom,1),4326),5) from "VEG"  """)
    dbquery.cursor.arraysize = 100000
    result_list = dbquery.cursor.fetchmany()
    
    while( len(result_list) > 0 ):
    
      print "Converting geometries"

      data_list = [json.loads(item[0]) for item in result_list]    
    
      data = { "type" : "GeometryCollection",
             "geometries" : data_list }
    
      print "Sending results"
        
      self.sendMessage(json.dumps(data), False)
      
      result_list = dbquery.cursor.fetchmany()
      
    #while( len(result_list)>0 ) :
    #  for ls in result_list:
    #    self.sendMessage(json.dumps(ls), False) 
    #  result_list = dbquery.cursor.fetchmany()
     
    print "Finished sending results"
    

#    print "Sending results ("+str(len(result))+")"
#    
#    for ls in result:
#      self.sendMessage(json.dumps(ls), False)
#
#    print "Finished sending results"
    
#   def onMessage(self, msg, binary):
#      self.sendMessage(msg, binary)


if __name__ == '__main__':

   factory = WebSocketServerFactory("ws://localhost:9090")
   factory.protocol = VectorServerProtocol
   listenWS(factory)
   reactor.run()
