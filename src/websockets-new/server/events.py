#
# This file contains the event handling code for the server events
#


import datetime

import array

import json


EventTypes = {
    "GetLayer" : 1,
    "GetAllLayers" : 2,
    "SyncTime" : 3
}

#superclass for events
class BaseEvent :
    
    def getTimestampAsArray(self, ts):
        return array.array('H', [ ts.year, ts.month-1, ts.day, ts.hour, ts.minute, ts.second, ts.microsecond/1000])
    def getTimestampAsTextFriendlyArray(self, ts):
        return [ ts.year, ts.month-1, ts.day, ts.hour, ts.minute, ts.second, ts.microsecond/1000]

#getlayer is the event for data request, i.e. spatial data
class GetLayer(BaseEvent) :
    
    # a request for data
    def getData(self, format, data, dbcursor) :
        if format.is_binary :
            return self.getBinaryData(format, data, dbcursor)
        else :
            return self.getTextData(format, data, dbcursor)
    
    #geojson format data
    def getTextData(self, format, data, dbcursor) :
        
        timestamp = { "requested" : datetime.datetime(
                                year=data["requested"][0], 
                                month=1+data["requested"][1],
                                day=data["requested"][2],
                                hour=data["requested"][3],
                                minute=data["requested"][4],
                                second=data["requested"][5],
                                microsecond=data["requested"][6]
                                ),
                            "received" : datetime.datetime.today()
                        }
        
        format.bbox = { 'minx' : data["data"]["bbox"][0], 'maxx' : data["data"]["bbox"][1], 'miny' : data["data"]["bbox"][2], 'maxy' : data["data"]["bbox"][3] }
        format.table = data["data"]["name"]
        
        queries = format.get_query_list() #get the queries for the data format
        
        timestamp["started_query"] = datetime.datetime.today()
        
        #print query
        
        results = list() # run queries and collect the results
        for query in queries :
            dbcursor.execute(query)
            results.append(dbcursor.fetchall())
        
        timestamp["started_processing"] = datetime.datetime.today()
        
        data_results = [ format.process_data(r) for r in results ] # process data in data format specific way.
        
        timestamp["finished_processing"] = datetime.datetime.today()
        
        # return formatted data
        return  [ json.dumps({ 'EventType' : EventTypes["GetLayer"], 'requested' : self.getTimestampAsTextFriendlyArray(timestamp["requested"]), 'received' : self.getTimestampAsTextFriendlyArray(timestamp["received"]), 'started_query' : self.getTimestampAsTextFriendlyArray(timestamp["started_query"]), 'started_processing' : self.getTimestampAsTextFriendlyArray(timestamp["started_processing"]), 'finished_processing' : self.getTimestampAsTextFriendlyArray(timestamp["finished_processing"]), 'data' : data }) for data in data_results ]
    
    #binary format data
    def getBinaryData(self, format, data, dbcursor) :
        data = { "name" : data[:8], "bbox" : array.array('d', data[8:-(7*2)]), "request_timestamp" : array.array('H', data[-(7*2):]) } #get data from raw binary structure
        name = data["name"]
        bbox = { "minx" : data["bbox"][0], "miny" : data["bbox"][2], "maxx" : data["bbox"][1], "maxy" : data["bbox"][3]}
        timestamp = { "requested" : datetime.datetime(
                                year=data["request_timestamp"][0], 
                                month=1+data["request_timestamp"][1],
                                day=data["request_timestamp"][2],
                                hour=data["request_timestamp"][3],
                                minute=data["request_timestamp"][4],
                                second=data["request_timestamp"][5],
                                microsecond=data["request_timestamp"][6]
                                ),
                            "received" : datetime.datetime.today()
                        }
        
        format.bbox = bbox # set bbox and tablename
        format.table = name
        
        queries = format.get_query_list() #get the queries for the data format
        
        #print queries
        
        timestamp["started_query"] = datetime.datetime.today()
        
        #print query
        
        special_tile_flag = False
        
        results = list() # run queries and collect the results
        for query in queries :
            dbcursor.execute(query)
            results.append(dbcursor.fetchall())
        
        timestamp["started_processing"] = datetime.datetime.today()
        
        #print "processing"
        
        data_results = [ format.process_data(r) for r in results ]
        
        #print "finished"
        
        timestamp["finished_processing"] = datetime.datetime.today()
        
        # return formatted data
        return [array.array('b', [EventTypes["GetLayer"], 0, 0, 0, 0, 0, 0, 0]).tostring() + self.getTimestampAsArray(timestamp["requested"]).tostring()+ self.getTimestampAsArray(timestamp["received"]).tostring()+ self.getTimestampAsArray(timestamp["started_query"]).tostring()+ self.getTimestampAsArray(timestamp["started_processing"]).tostring()+ self.getTimestampAsArray(timestamp["finished_processing"]).tostring()+ array.array('b', [0, 0]).tostring()+ datastr for datastr in data_results ]
        
    
#getalllayers is the event for requesting available map layers
class GetAllLayers(BaseEvent) :
    
    def getData(self, format, data) :
        if format.is_binary :
            return self.getBinaryData(format, data)
        else :
            return self.getTextData(format, data)
    
    def getTextData(self, format, data) :
        
#        timestamp = { "requested" : datetime.datetime(
#                                year=data["requested"][0], 
#                                month=1+data["requested"][1],
#                                day=data["requested"][2],
#                                hour=data["requested"][3],
#                                minute=data["requested"][4],
#                                second=data["requested"][5],
#                                microsecond=data["requested"][6]
#                                ),
#                            "received" : datetime.datetime.today()
#                        }
        
        return json.dumps({ 'EventType' : EventTypes["GetAllLayers"], 'Layers' : format.table_list.values() })
    
    def getBinaryData(self, format, data) :
#        data = { "request_timestamp" : array.array('H', data) }
#        timestamp = { "requested" : datetime.datetime(
#                                year=data["request_timestamp"][0], 
#                                month=1+data["request_timestamp"][1],
#                                day=data["request_timestamp"][2],
#                                hour=data["request_timestamp"][3],
#                                minute=data["request_timestamp"][4],
#                                second=data["request_timestamp"][5],
#                                microsecond=data["request_timestamp"][6]
#                                ),
#                            "received" : datetime.datetime.today()
#                        }
        
        nolayers = len(format.table_list.keys()) # number of layers
        layerstring = array.array('c', ''.join(format.table_list.values())) # concatenate the layer names. since they are all 8 characters long, and we have nolayers, they are easy to parse
        
        return array.array('b', [EventTypes["GetAllLayers"], 0, 0, 0, 0, 0, 0, nolayers]).tostring()+ layerstring.tostring()

#synctime event is for synchronizing the clocks and testing latency
class SyncTime(BaseEvent) :
    
    def getData(self, format, data) :
        
        if format.is_binary :
            return self.getBinaryData(format, data)
        else :
            return self.getTextData(format, data)
    
    def getTextData(self, format, data) :
        
        timestamp = { "requested" : datetime.datetime(
                                year=data["requested"][0], 
                                month=1+data["requested"][1],
                                day=data["requested"][2],
                                hour=data["requested"][3],
                                minute=data["requested"][4],
                                second=data["requested"][5],
                                microsecond=data["requested"][6]
                                ),
                            "received" : datetime.datetime.today()
                        }
        
        return json.dumps({ 'EventType' : EventTypes["SyncTime"], 'requested' : self.getTimestampAsTextFriendlyArray(timestamp["requested"]), 'received' : self.getTimestampAsTextFriendlyArray(timestamp["received"]) })
    
    def getBinaryData(self, format, data) :
        #ts1 = datetime.datetime.now()
        data = { "request_timestamp" : array.array('H', data) }
        timestamp = { "requested" : datetime.datetime(
                                year=data["request_timestamp"][0], 
                                month=1+data["request_timestamp"][1],
                                day=data["request_timestamp"][2],
                                hour=data["request_timestamp"][3],
                                minute=data["request_timestamp"][4],
                                second=data["request_timestamp"][5],
                                microsecond=data["request_timestamp"][6]
                                ),
                            "received" : datetime.datetime.today()
                        }
        #ts2 = datetime.datetime.now()
        #print ts2-ts1
        return array.array('b', [EventTypes["SyncTime"], 0, 0, 0, 0, 0, 0, 0]).tostring()+ self.getTimestampAsArray(timestamp["requested"]).tostring()+ self.getTimestampAsArray(timestamp["received"]).tostring()
