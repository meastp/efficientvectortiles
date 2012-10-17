#
# This is the Web Sockets server implementation and
# contains the logic in the server for replying to
# events from the client.
# 

from autobahn.websocket import WebSocketServerProtocol

import formats.binary.binary
import formats.text.text

import psycopg2 # postgresql library

import array

import json

import events

import sys

import inspect

import config

# Search all available data format classes lists and return an instance of the class that has name equal to fname
def getDataFormatInstance(fname, binary_formats_list, text_formats_list) :
    for name, cls in binary_formats_list :
        if name == fname :
            return cls()
    for name, cls in text_formats_list :
        if name == fname :
            return cls()


class VectorServerProtocol(WebSocketServerProtocol):
  
  # This is executed when the server opens a connection to a client.
  def onOpen(self):
    print "New connection"
    
    # open a database connection for this session
    self.connection = psycopg2.connect(config.POSTGRESQL_CONNECT_STRING)
    self.connection.set_session(readonly=True)
    
    self.BinaryFormats = inspect.getmembers(sys.modules["formats.binary.binary"], inspect.isclass) # get available binary data formats by traversing the class hierarchy
    self.TextFormats = inspect.getmembers(sys.modules["formats.text.text"], inspect.isclass)
    
    #hardcoded values for data formats, transferred to and from the client in binary and text formats.
    self.DataFormatTypes = {
         1 : "FormatGeoJSONTiles",
         2 : "Format1BCachedTiles",
         3 : "Format8BOnDemand",
         4 : "Format2BOnDemand",
         5 : "Format1BTilesOnDemand",
         6 : "FormatGeoJSONTilesSimple",
         7 : "Format1BCachedTilesSimple",
         8 : "Format8BOnDemandSimple",
         9 : "Format2BOnDemandSimple"
        }
    
    #get a reverse lookup table for event types
    self.rEventTypes = {v:k for k, v in events.EventTypes.items()}
    
    #event lookup table
    self.eve = dict()
    self.eve["GetLayer"] = events.GetLayer()
    self.eve["GetAllLayers"] = events.GetAllLayers()
    self.eve["SyncTime"] = events.SyncTime()

  # when the server receives a message from a client
  def onMessage(self, data, is_binary):
    
    MessageData = None
    EventType = None
    DataFormat = None
    
    if is_binary : #if the data is of binary format
        
        event = array.array('b', data[0:2]) #extract event data
        
        MessageData = data[2:] #extract actual data
        
        EventType = self.rEventTypes[event[0]] #lookup the event type
        
        DataFormat = getDataFormatInstance(self.DataFormatTypes[event[1]], self.BinaryFormats, self.TextFormats) #get correct data format object instance
    
    else : # text
        
        # a json object
        
        tdata = json.loads(data) #parse JSON string to objects
        
        #print tdata
        
        EventType = self.rEventTypes[tdata['EventType']]#lookup the event type
        
        MessageData = tdata['MessageData']#extract event data
        
        DataFormat = getDataFormatInstance(self.DataFormatTypes[tdata['DataFormatType']], self.BinaryFormats, self.TextFormats) #get correct data format object instance
        
        #print DataFormat
    
    if EventType == "GetLayer" :
        
        results_data_list = self.eve["GetLayer"].getData(DataFormat, MessageData, self.connection.cursor()) # get and process data 
        
        for data in results_data_list : # send data to the client
            #print data
            self.sendMessage(data , DataFormat.is_binary)
            print "sent data"
        
    elif EventType == "GetAllLayers" :
        
        self.sendMessage(self.eve["GetAllLayers"].getData(DataFormat, MessageData) , DataFormat.is_binary)
    
    elif EventType == "SyncTime" :
        
        self.sendMessage(self.eve["SyncTime"].getData(DataFormat, MessageData) , DataFormat.is_binary)
        
