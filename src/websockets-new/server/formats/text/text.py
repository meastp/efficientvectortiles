#
# this file contains text formats for transferring spatial vector data
#
#


import json

from shapely.wkb import loads

from ..base import BaseFormat

import array

class FormatGeoJSONTiles(BaseFormat):
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = None
        
        self.db_table_list = {
            'map_annen_bygning_tiles' : 'ANNENBYG', 
            'map_bygning_tiles' : 'BYGNINGT', 
            'map_veg_tiles' : 'VEGTABLE'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}
    
    @property
    def is_binary(self):
        return False
    
    def get_query_list(self):
        
        self.query = "select ST_AsBinary(tile_box), ST_AsGeoJSON(tile) from "+self.db_table_list_reverse[self.table]+" where tile_box && st_setsrid(box2d(ST_GeomFromText('LINESTRING("+str(self.bbox["minx"])+" "+str(self.bbox["miny"])+", "+str(self.bbox["maxx"])+" "+str(self.bbox["maxy"])+")')),25832)"
        
        return [self.query]
    
    def process_data(self, query_result):
        
        no_tiles = len(query_result) #get number of tiles
        
        #create new geojson object
        result = { 
            "type" : "FeatureCollection", 
            "features" : [],
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::25832" } },
            "properties" : {"table":self.table}
            
            }
        
        for tile in query_result:
            
            bbox = loads(array.array('c',tile[0]).tostring()) #get bbox
            bboxminx,bboxminy,bboxmaxx,bboxmaxy = bbox.bounds
            
            tile_data = json.loads(tile[1]) #parse tile
            
            #print tile[1][:200]
            
            idx_remove = []
            
            #loop through and generate geojson data, tile-local coordinates
            if tile_data['type'] == "GeometryCollection" :
                
                
                geometries = []
                for idx, geom in enumerate(tile_data["geometries"]) :
                    
                    if geom["type"] == "Point" :
                        pass
                    
                    elif geom["type"] == "GeometryCollection" and geom["geometries"] == [] :
                        pass
                    
                    elif geom["type"] == "LineString" :
                        geometries.append({ 'type' : "LineString", 'coordinates' : [ [int(x-bboxminx), int(y-bboxminy)] for x,y in geom["coordinates"] ]}) 
                    
                    elif geom["type"] == "Polygon" :
                        
                        geometries.append({ 'type' : "Polygon", 'coordinates' : [ [ [int(x-bboxminx), int(y-bboxminy)] for x,y in ring ] for ring in geom["coordinates"] ]})
                        
                        
                    
                    elif geom["type"] == "MultiLineString" :
                        
                        geometries.append({ 'type' : "MultiLineString", 'coordinates' : [[ [int(x-bboxminx), int(y-bboxminy)] for x,y in linestring ] for linestring in geom["coordinates"]]})
                    
                    elif geom["type"] == "MultiPolygon" :
                        
                        geometries.append({ 'type' : "MultiPolygon", 'coordinates' : [[[ [int(x-bboxminx), int(y-bboxminy)] for x,y in ring ] for ring in polygon ] for polygon in geom["coordinates"] ]})
                    
                    else  :
                        print geom["type"]
                        assert False
                    
                tile_data["geometries"] = geometries
                
                
                
            elif tile_data["type"] == "MultiLineString" :
                for linestring in tile_data["coordinates"] :
                    for coord in linestring :
                        x,y = coord
                        coord[0] = int(x-bboxminx)
                        coord[1] = int(y-bboxminy)
            
            elif tile_data["type"] == "MultiPolygon" :
                for polygon in tile_data["coordinates"] :
                    for ring in polygon :
                        for coord in ring :
                            x,y = coord
                            coord[0] = int(x-bboxminx)
                            coord[1] = int(y-bboxminy)
            else :
                print tile_data["type"]
                assert False
                
            

            
            #print tile_data
            
            
            result["features"].append({ "type" : "Feature", "geometry" : tile_data, "properties" : {"minx" : bboxminx, "miny" : bboxminy} })
        
        #return geojson string
        return result

class FormatGeoJSONTilesSimple(FormatGeoJSONTiles):
    
    def __init__(self, table=None, bbox=None):
        self.table = table
        self.bbox = bbox
        
        self.query = None
        
        self.db_table_list = {
            'map_annen_bygning_tiles_simple1' : 'ANNENBYG', 
            'map_bygning_tiles_simple1' : 'BYGNINGT', 
            'map_veg_tiles_simple1' : 'VEGTABLE'
        }
        self.db_table_list_reverse = {v:k for k, v in self.db_table_list.items()}

