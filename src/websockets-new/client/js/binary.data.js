

// render 2 byte on demand data format
function render_FORMAT_BINARY_2B_ONDEMAND(binary_data, offset, map) // websockets-bin-test
{
    var raw_layer = new Uint8Array(binary_data,offset,8); // layer name
    //console.log(raw_layer);
    
    var layer = String.fromCharCode.apply(null, raw_layer); // convert to string
    //console.log(layer);
    
    ////
    
    var header = new Uint32Array(binary_data,raw_layer.byteOffset+raw_layer.byteLength,4); // get the data header with size
    var size = header[0];
    //console.log(header);
    
    
    var offset_header = new Uint16Array(binary_data, header.byteOffset+header.byteLength, 2); // coordinate offsets
    //console.log(offset_header);
    
    var sub_header = new Uint16Array(binary_data, offset_header.byteOffset+offset_header.byteLength, 4*size); // header with features
    //console.log(sub_header);
    
    var data = new Uint16Array(binary_data, sub_header.byteOffset+sub_header.byteLength); //raw_data).subarray(8+(size*4)); // coordinate data
    //console.log(data.subarray(0,100));
    
    formatted_data = new Array(size);
    
    var no_coordinates = 0;
    
    //loop through data and correct coordiantes
    
    for(var i=0,loffset = 0;i<size;i++)
    {
        
        var nelements = sub_header[i*4];
        no_coordinates += 2*nelements;
        //console.log(offset);
        //console.log(nelements);
        
        //var data = new Float64Array(raw_data, (2)+(4*size)+(offset), 2);
        
        //formatted_data[i] = data.subarray(offset, offset+nelements);
        
        formatted_data[i] = new Array(nelements);
        
        for(var j=0; j<nelements;j++)
        {
            formatted_data[i][j] = new Uint32Array(2);
            formatted_data[i][j][0] = data[loffset+j*2] + map.projection.bbox.x.min - offset_header[0];
            formatted_data[i][j][1] = data[loffset+j*2+1] + map.projection.bbox.y.min - offset_header[1];
            
            
            //formatted_data[i][j] = data.subarray(loffset+j*2, (loffset+j*2)+2);
            //formatted_data[i][j][0] += map.projection.bbox.x.min - offset_header[0];
            //formatted_data[i][j][1] += map.projection.bbox.y.min - offset_header[1];
        }
        
        loffset += nelements*2;
        
    }
    
    //console.log(formatted_data[0])
    
    map.events.update(map);
    
    map.features.select("#"+layer).selectAll("path").remove();
    
    
    
    map.features.select("#"+layer).selectAll("path")
              .data(formatted_data)
              .enter().append("path")
              .attr("d", map.line_draw_function);
    
    /*
              
    map.features.select("#"+layer).selectAll("path")
              .data(formatted_data)
              .enter().append("path")
              .attr("d", map.polygon_draw_function);
    */
    return { name : layer, features : size, coordinates : no_coordinates, data_size_kb : binary_data.byteLength/1000.0 }
}

// the 8 byte per coordinate data format
function render_FORMAT_BINARY_8B_ONDEMAND(binary_data, offset, map) // websockets-bin-test
{
    var raw_layer = new Uint8Array(binary_data,offset,8); // layer name
    //console.log(raw_layer);

    var layer = String.fromCharCode.apply(null, raw_layer); // convert to string
    //console.log(layer);
    
    var header = new Uint32Array(binary_data,raw_layer.byteOffset+raw_layer.byteLength,2); // object size/ count
    var size = header[0];
    //console.log(header);
    
    var sub_header = new Uint16Array(binary_data, header.byteOffset+header.byteLength, 4*size); // features
    //console.log(sub_header);
    
    var data = new Float64Array(binary_data).subarray(((sub_header.byteOffset+sub_header.byteLength)/8)+1); // coordinate data
    
    formatted_data = new Array(size);
    
    var no_coordinates = 0;
    
    // loop through data, correct coordinates
    for(var i=0,loffset = 0;i<size;i++)
    {
        
        var nelements = sub_header[i*4];
        no_coordinates += 2*nelements;
        //console.log(offset);
        //console.log(nelements);
        
        //var data = new Float64Array(raw_data, (2)+(4*size)+(offset), 2);
        
        //formatted_data[i] = data.subarray(offset, offset+nelements);
        
        formatted_data[i] = new Array(nelements);
        
        for(var j=0; j<nelements;j++)
        {
            formatted_data[i][j] = data.subarray(loffset+j*2, (loffset+j*2)+2);
        }
        
        loffset += nelements*2;
        
    }
    
    map.events.update(map);
    
    map.features.select("#"+layer).selectAll("path").remove();
    
    
    map.features.select("#"+layer).selectAll("path")
              .data(formatted_data)
              .enter().append("path")
              .attr("d", map.line_draw_function);
    /*
              
    map.features.select("#"+layer).selectAll("path")
              .data(formatted_data)
              .enter().append("path")
              .attr("d", map.polygon_draw_function);
    */
    return { name : layer, features : size, coordinates : no_coordinates, data_size_kb : binary_data.byteLength/1000.0 }
}

// single byte tiled data format
function render_FORMAT_BINARY_1B_CACHED_TILES(binary_data, offset, map)
{

    var raw_layer = new Uint8Array(binary_data,offset,8); //layer name
    //console.log(raw_layer);

    var layer = String.fromCharCode.apply(null, raw_layer); //name to string
    //console.log(layer);

    var header = new Uint32Array(binary_data,offset+8,4); // number of tiles
    var size = header[0];
    //console.log(header);

    var header_offset = header.byteOffset,
        header_byte_size = header.byteLength/header.length,
        header_length = header.length;

    var tile_header_offset = header_offset+(header_byte_size*header_length),
        tile_header_byte_size = 8,
        tile_header_length = 3*size;

    var tile_header = new Float64Array(binary_data, header.byteOffset+header.byteLength, tile_header_length); // tiles
    //console.log(tile_header);

    var geometry_header_coords_offset = tile_header_offset+(tile_header_byte_size*tile_header_length),
        geometry_header_coords_byte_size = 2,
        geometry_header_coords_length = d3.sum(tile_header, function(obj){ 
                                                            if (obj < 1000) 
                                                             { return obj; } 
                                                            else { return null; }
                                                            } 
                                                        );

    var geometry_header_coords = new Uint16Array(binary_data, tile_header.byteOffset+tile_header.byteLength, geometry_header_coords_length); //features
    //console.log(geometry_header_coords);


    var geometry_header_type_offset = geometry_header_coords_offset+(geometry_header_coords_byte_size*geometry_header_coords_length),
        geometry_header_type_byte_size = 1,
        geometry_header_type_length = geometry_header_coords_length;

    var geometry_header_type = new Uint8Array(binary_data, geometry_header_type_offset, geometry_header_type_length); //feature type
    //console.log(geometry_header_type);

    var data = new Uint8Array(binary_data,geometry_header_type_offset+(geometry_header_type_byte_size*geometry_header_type_length)); //coordinate data
    //console.log(data)

    var object_data = { lines : [], polygons : [] };
    
    // correct all tile-local coordinates, add features to object_data
    
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
    
    console.log(object_data);
    
    //console.log(layer+" Tiles: "+size+" Features: "+geometry_header_type.length+" Coordinates: "+data.length+" Size: "+(binary_data.byteLength)/1000.0+"KB");
    
    
    map.events.update(map);
    
    map.features.select("#"+layer).selectAll("path").remove();
    
    map.features.select("#"+layer).selectAll("path")
              .data(object_data.lines)
              .enter().append("path")
              .attr("d", map.line_draw_function);
              
    map.features.select("#"+layer).selectAll("path")
              .data(object_data.polygons)
              .enter().append("path")
              .attr("d", map.polygon_draw_function);
    
    //alert("pause");
    
    return { name : layer, tiles : size, features : geometry_header_type.length, coordinates : data.length, data_size_kb : binary_data.byteLength/1000.0}
}
