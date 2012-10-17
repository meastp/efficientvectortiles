
// process and render geojson tiles data format
function render_FORMAT_GJ_CACHED_TILES(json_data, map, byte_size)
{
    //console.log(json_data);
    
    var tiles = json_data['features'];
    
    var layer_name = json_data['properties']['table'];
    
    var object_data = { lines : [], polygons : [] };
    
    var nfeatures = 0;
    var ncoordinates = 0;
    
    // loop through the data and correct geometries from tile-local coordinates
    for(var i=0;i<tiles.length;i++)
    {
        var feature = tiles[i];
        
        
        var minx = parseInt(feature['properties']['minx']);
        var miny = parseInt(feature['properties']['miny']);
        
        var geometry_collection = feature['geometry'];
        
        //console.log(geometry_collection);
        
        if(geometry_collection["type"] == "GeometryCollection")
        {
            //console.log("GeometryCollection");
            
            for(var j=0;j<geometry_collection["geometries"].length;j++)
            {
                var geometry = geometry_collection["geometries"][j];
                
                if(geometry["type"]=="LineString")
                {
                    console.log("LineString");
                    nfeatures++;
                    ncoordinates += 2*geometry["coordinates"].length;
                    for (var k=0;k<geometry["coordinates"].length;k++)
                    {
                        geometry["coordinates"][k][0]+=minx;
                        geometry["coordinates"][k][1]+=miny;
                    }
                    object_data.lines = object_data.lines.concat(geometry["coordinates"]);
                    ncoordinates += geometry["coordinates"].length;
                }
                else if(geometry["type"]=="MultiLineString")
                {
                    //console.log("MultiLineString");
                    nfeatures += geometry["coordinates"].length;
                    for(var k=0;k<geometry["coordinates"].length;k++)
                    {
                        ncoordinates += 2*geometry["coordinates"][k].length;
                        for (var l=0;l<geometry["coordinates"][k].length;l++)
                        {
                            geometry["coordinates"][k][l][0]+=minx;
                            geometry["coordinates"][k][l][1]+=miny;
                        }
                        object_data.lines = object_data.lines.concat(geometry["coordinates"][k]);
                        ncoordinates += geometry["coordinates"].length;
                    }
                }
                else if(geometry["type"]=="Polygon")
                {
                    //console.log("Polygon");
                    nfeatures ++;
                    for (var k=0;k<geometry["coordinates"].length;k++)
                    {
                            ncoordinates += 2*geometry["coordinates"][k].length;
                            for(var l=0;l<geometry["coordinates"][k].length;l++)
                            {
                                //console.log(geometry_collection["coordinates"][k][l][m]);
                                geometry["coordinates"][k][l][0]+=minx;
                                geometry["coordinates"][k][l][1]+=miny;
                                //console.log(geometry_collection["coordinates"][k][l][m]);
                            }
                    }
                    object_data.polygons = object_data.polygons.concat(geometry["coordinates"]);
                    ncoordinates += geometry["coordinates"].length;
                }
                else if(geometry["type"]=="MultiPolygon")
                {
                    //console.log("MultiPolygon");
                    nfeatures += geometry["coordinates"].length;
                    for(var k=0;k<geometry["coordinates"].length;k++)
                    {
                    
                    
                        //var lines = new Array(geometry_collection["coordinates"][k].length);
                        
                        
                        
                        for (var l=0;l<geometry["coordinates"][k].length;l++)
                        {
                        
                            ncoordinates += 2*geometry["coordinates"][k][l].length;
                            for(var m=0;m<geometry["coordinates"][k][l].length;m++)
                            {
                                //console.log(geometry_collection["coordinates"][k][l][m]);
                                geometry["coordinates"][k][l][m][0]+=minx;
                                geometry["coordinates"][k][l][m][1]+=miny;
                                //console.log(geometry_collection["coordinates"][k][l][m]);
                            }
                        }
                        object_data.polygons = object_data.polygons.concat(geometry["coordinates"][k]);
                        //console.log(geometry_collection["coordinates"][k]);
                        ncoordinates += geometry["coordinates"].length;
                    
                    
                    /*
                        for (var l=0;l<geometry["coordinates"].length;l++)
                        {
                            geometry["coordinates"][k][l][0]+=minx;
                            geometry["coordinates"][k][l][1]+=miny;
                        }
                        object_data.polygons.push(geometry["coordinates"][k]);
                        ncoordinates += geometry["coordinates"].length;
                    */
                    }
                }
                else
                {
                    console.log("Error: Unknown geometry type"+geometry["type"]);
                }
                
                
            }
            
        }
        else if(geometry_collection["type"] == "MultiPolygon")
        {
            //console.log("MultiPolygon");
            nfeatures += geometry_collection["coordinates"].length;
            for(var k=0;k<geometry_collection["coordinates"].length;k++)
            {
                //var lines = new Array(geometry_collection["coordinates"][k].length);
                
                
                
                for (var l=0;l<geometry_collection["coordinates"][k].length;l++)
                {
                    ncoordinates += 2*geometry_collection["coordinates"][k][l].length;
                    for(var m=0;m<geometry_collection["coordinates"][k][l].length;m++)
                    {
                        //console.log(geometry_collection["coordinates"][k][l][m]);
                        geometry_collection["coordinates"][k][l][m][0]+=minx;
                        geometry_collection["coordinates"][k][l][m][1]+=miny;
                        //console.log(geometry_collection["coordinates"][k][l][m]);
                    }
                }
                object_data.polygons = object_data.polygons.concat(geometry_collection["coordinates"][k]);
                //console.log(geometry_collection["coordinates"][k]);
                ncoordinates += geometry_collection["coordinates"].length;
            }
            //console.log("END");
        }
        else if(geometry_collection["type"] == "MultiLineString")
        {
            nfeatures += geometry_collection["coordinates"].length;
            for(var k=0;k<geometry_collection["coordinates"].length;k++)
            {
                            ncoordinates += 2*geometry_collection["coordinates"][k].length;
                for (var l=0;l<geometry_collection["coordinates"][k].length;l++)
                {
                    geometry_collection["coordinates"][k][l][0]+=minx;
                    geometry_collection["coordinates"][k][l][1]+=miny;
                }
                object_data.lines.push(geometry_collection["coordinates"][k]);
                ncoordinates += geometry_collection["coordinates"].length;
            }
        }
        else
        {
            console.log("Error: Unknown Geometry Collection Type");
        }
    }
    
/*

    var object_data = { lines : [], polygons : [] };

    var tile_offset=0;
    var data_offset=0;
    for(var i=0;i<size;i++)
    {
        var tile_elements = tile_header[i*3];
        var origox = tile_header[i*3+1];
        var origoy = tile_header[i*3+2];
        
        //console.log(tile_elements); // number of geometries in the geometrycollection/tile
        //console.log(origox);
        //console.log(origoy);
        
        
        var geometry_elements_coords = geometry_header_coords.subarray(tile_offset, tile_offset+tile_elements); // coordinates in the geometry
        var geometry_elements_type = geometry_header_type.subarray(tile_offset, tile_offset+tile_elements);
        
        for(var j=0;j<geometry_elements_coords.length;j++)
        {
            var object = new Array(geometry_elements_coords[j]);
            
            
            for(var k=0;k<geometry_elements_coords[j];k++)
            {
                object[k] = [ origox+data[data_offset], origoy+data[data_offset+1] ];
                data_offset += 2;
            }
            
            if (geometry_elements_type[j] == 1)
                object_data.lines.push(object);
            
            if (geometry_elements_type[j] == 2)
                object_data.polygons.push(object);
                
            //if geometry_elements_type[j] == 3 :
        }
        
        
        
        tile_offset += tile_elements;
    }
    
    //console.log(layer+" Tiles: "+size+" Features: "+geometry_header_type.length+" Coordinates: "+data.length+" Size: "+(binary_data.byteLength)/1000.0+"KB");

*/

    //console.log(object_data);

    map.events.update(map);
    
    map.features.select("#"+layer_name).selectAll("path").remove();
    
    map.features.select("#"+layer_name).selectAll("path")
              .data(object_data.lines)
              .enter().append("path")
              .attr("d", map.line_draw_function);
              
            map.features.select("#"+layer_name).selectAll("path")
              .data(object_data.polygons)
              .enter().append("path")
              .attr("d", map.polygon_draw_function);
    
    return { name : layer_name, tiles : tiles.length, features : nfeatures, coordinates : ncoordinates, data_size_kb : byte_size/1000.0}
}
