#
# this file contains the binary data formats
#
#

import array

from shapely.wkb import loads

from ..base import BaseFormat

# corresponding websockets old test files :
# bin_ser.py 8 byte data, on demand [OK]
# bin_ser_localorigo.py 2 byte data, on demand [OK]
# bin_ser_tiles.py 1 byte data, tiles [OK]
# bin_ser_tiles_map.py 1 byte data, tiles, geomtype [OK]
# bin_ser_tiles_ondemand.py 1 byte data, tiles, on demand
# bin_tiles_map.py 1 byte data, tiles, geomtype, foreach tile/table [OK]
# geo_ser.py, gentiles.py, echo_ser.py, echo_server.py TEST 

class Format2BOnDemand(BaseFormat) : # bin_ser_localorigo.py
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = list()
        
        self.db_table_list = {
            '"VEG"' : 'VEGTABLE',
            '"BYGNING"' : 'BYGNINGT',
            '"ANNENBYGNING"' : 'ANNENBYG'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}
    
    @property
    def is_binary(self):
        return True
    
    def get_query_list(self):
        self.query = "select ST_AsBinary(geom) from "+self.db_table_list_reverse[self.table]+" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(self.bbox["minx"])+" "+str(self.bbox["miny"])+", "+str(self.bbox["maxx"])+" "+str(self.bbox["maxy"])+")')),25832)"
        
        return [ self.query ]
    
    def process_data(self, query_result):
        
        
        size = len(query_result)
        
        # the geometries are not clipped, due to performace reasons, so we need some extra space around the tile
        invisible_space = { 'x' : 65536 - ( self.bbox['maxx']-self.bbox['minx'] ), 'y' : 65536 - ( self.bbox['maxy']-self.bbox['miny'] ) }
        offset = {'x': int(invisible_space['x']/2.0), 'y':int(invisible_space['y']/2.0)} #calculate offset
        
        table_name_header = array.array('c', self.table) #layer name
        header = array.array('L', [size,0]) # features size
        offset_headers = array.array('H', [offset['x'],offset['y']])# the offset
        sub_headers = array.array('H') # features
        data = array.array('H') # coordinate data
        
        #print offset_headers, data[:100]
        
        #build data structure
        for result in query_result:
            obj = loads(array.array('c',result[0]).tostring())
            
            sub_header = array.array('H', [len(obj.coords),0,0,0])
            
            sub_headers.extend(sub_header)
            
            for x,y in obj.coords:
                data.append(int(x-self.bbox['minx'])+offset['x'])
                data.append(int(y-self.bbox['miny'])+offset['y'])
        
        #return binary string
        return table_name_header.tostring()+header.tostring()+offset_headers.tostring()+sub_headers.tostring()+data.tostring()

class Format2BOnDemandSimple(Format2BOnDemand) : # bin_ser_localorigo.py
    
    def get_query_list(self):
        self.query = "select ST_AsBinary(ST_Simplify(geom, 1)) from "+self.db_table_list_reverse[self.table]+" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(self.bbox["minx"])+" "+str(self.bbox["miny"])+", "+str(self.bbox["maxx"])+" "+str(self.bbox["maxy"])+")')),25832)"
        
        return [ self.query ]

class Format8BOnDemand(BaseFormat) : # bin_ser.py
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = list()
        
        
        self.db_table_list = {
            '"VEG"' : 'VEGTABLE',
            '"BYGNING"' : 'BYGNINGT',
            '"ANNENBYGNING"' : 'ANNENBYG'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}
    
    @property
    def is_binary(self):
        return True
    
    def get_query_list(self):
        self.query = "select ST_AsBinary(geom) from "+self.db_table_list_reverse[self.table]+" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(self.bbox["minx"])+" "+str(self.bbox["miny"])+", "+str(self.bbox["maxx"])+" "+str(self.bbox["maxy"])+")')),25832)"
        
        return [self.query]
    
    def process_data(self, query_result):
        
        size = len(query_result)
        
        table_name_header = array.array('c', self.table) #layer name
        header = array.array('L', [size,0]) # feature size
        sub_headers = array.array('H') # feature with coordinate count
        data = array.array('d') # coordinate data
        
        for result in query_result:
            obj = loads(array.array('c',result[0]).tostring())
            
            sub_header = array.array('H', [len(obj.coords),0,0,0])
            
            sub_headers.extend(sub_header)
            
            for x,y in obj.coords:
                data.append(x)
                data.append(y)
        
        #return binary string
        return table_name_header.tostring()+header.tostring()+sub_headers.tostring()+data.tostring()

class Format8BOnDemandSimple(Format8BOnDemand) : # bin_ser.py
    
    def get_query_list(self):
        self.query = "select ST_AsBinary(ST_Simplify(geom, 1)) from "+self.db_table_list_reverse[self.table]+" where geom && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(self.bbox["minx"])+" "+str(self.bbox["miny"])+", "+str(self.bbox["maxx"])+" "+str(self.bbox["maxy"])+")')),25832)"
        
        return [self.query]

class Format1BTilesOnDemand(BaseFormat) :
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.range = None
        
        self.query = list()
        
        
        self.db_table_list = {
            'annen_bygning' : 'ANNENBYG', 
            'bygning' : 'BYGNINGT', 
            'veg' : 'VEGTABLE'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}
    
    @property
    def is_binary(self):
        return True
    
    def get_query_list(self):
        
        self.range = {"x" : range(int(self.bbox["minx"]), int(self.bbox["maxx"]), 255), "y" : range(int(self.bbox["miny"]), int(self.bbox["maxy"]), 255)}
        
        for x in self.range['x'] :
            for y in self.range['y'] :
                
                query = """WITH 
                              box_extent as (
                                select st_setsrid(box2d(ST_GeomFromText('LINESTRING("""+str(x)+""" """+str(y)+""", """+str(x+255)+""" """+str(y+255)+""")')),25832) as box
                                ),
                              matches AS (
                                select intersection(geom, box) as geom, box from """+self.db_table_list_reverse[self.table]+""", box_extent
                                  where ST_IsValid(geom) and ST_IsValid(intersection(geom, box)) and not ST_IsEmpty(intersection(geom, box))
                                ),
                              geocollection AS (
                                SELECT ST_Collect(geom) as geom from matches
                                )
                                select ST_AsBinary(box), ST_AsBinary(geom) from geocollection, box_extent where not ST_IsEmpty(geom)
                """
                
                self.query.append(query)
        
        return self.query
    
    def process_data(self, query_result):
        
        size = len(query_result)
        
        #print results 
        #print size
        
        table_name_header = array.array('c', self.table) #layer name
        header = array.array('L', [size, 0]) # contains the number of tiles in the data packet
        tile_headers = array.array('d') # contains the number of geometry objects in the tile and bounds
        geometry_headers_nocoordinates = array.array('H') # contains the number of coordinates in the geometry (up to 65536)
        geometry_headers_type = array.array('B') # contains the geometry type
        data = array.array('B') # contains the coordinates
        
        for tile in query_result:
            
            
            bbox = loads(array.array('c',tile[0]).tostring()) # get the bbox from the results
            bboxminx,bboxminy,bboxmaxx,bboxmaxy = bbox.bounds
            
            geometry_collection = loads(array.array('c',tile[1]).tostring()) #get the tile data from the results
            
            
            num_geometries = 0
            
            #loop through the geometries and create the binary data structure and tile-local coordinates
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
        
        #print "Tiles: ", size
        
        #print header, tile_headers, geometry_headers_type, geometry_headers_nocoordinates
        #print len(header), len(tile_headers), len(geometry_headers_type), len(geometry_headers_nocoordinates)
        #print data[:20], data[-20:]
        #print data
        
        #return binary data string
        return table_name_header.tostring()+header.tostring()+tile_headers.tostring()+geometry_headers_nocoordinates.tostring()+geometry_headers_type.tostring()+data.tostring()


class Format1BCachedTiles(BaseFormat) :
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = list()
        
        
        self.db_table_list = {
            'map_annen_bygning_tiles' : 'ANNENBYG', 
            'map_bygning_tiles' : 'BYGNINGT', 
            'map_veg_tiles' : 'VEGTABLE'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}
    
    @property
    def is_binary(self):
        return True
    
    def get_query_list(self):
        self.query = "select ST_AsBinary(tile_box), ST_AsBinary(tile) from "+self.db_table_list_reverse[self.table]+" where tile_box && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(self.bbox["minx"])+" "+str(self.bbox["miny"])+", "+str(self.bbox["maxx"])+" "+str(self.bbox["maxy"])+")')),25832)"
        
        return [self.query]
    
    def process_data(self, query_result):
        
        size = len(query_result)
        
        #print results 
        #print size
        
        table_name_header = array.array('c', self.table) #layer name
        header = array.array('L', [size, 0]) # contains the number of tiles in the data packet
        tile_headers = array.array('d') # contains the number of geometry objects in the tile and bounds
        geometry_headers_nocoordinates = array.array('H') # contains the number of coordinates in the geometry (up to 65536)
        geometry_headers_type = array.array('B') # contains the geometry type
        data = array.array('B') # contains the coordinates
        
        for tile in query_result:
            
            
            bbox = loads(array.array('c',tile[0]).tostring()) #get bbox from results
            bboxminx,bboxminy,bboxmaxx,bboxmaxy = bbox.bounds
            
            geometry_collection = loads(array.array('c',tile[1]).tostring()) #get tile geometry from results
            
            
            num_geometries = 0
            
            #loop through the geometries, create binary data structure and tile-local coordinates
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
        
        #print "Tiles: ", size
        
        #print header, tile_headers, geometry_headers_type, geometry_headers_nocoordinates
        #print len(header), len(tile_headers), len(geometry_headers_type), len(geometry_headers_nocoordinates)
        #print data[:20], data[-20:]
        #print data
        
        return table_name_header.tostring()+header.tostring()+tile_headers.tostring()+geometry_headers_nocoordinates.tostring()+geometry_headers_type.tostring()+data.tostring()

class Format1BCachedTilesSimple(Format1BCachedTiles) :
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = list()
        
        
        self.db_table_list = {
            'map_annen_bygning_tiles_simple1' : 'ANNENBYG', 
            'map_bygning_tiles_simple1' : 'BYGNINGT', 
            'map_veg_tiles_simple1' : 'VEGTABLE'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}
