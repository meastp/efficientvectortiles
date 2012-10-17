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
