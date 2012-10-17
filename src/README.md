A major part of the thesis work consisted of software development, and extra care was taken to make this source code available to anyone interested in confirmin the results, or looking at the source code. 

## dataformats-example 

This folder contains examples from the text, and the actual spatial data was taken directly from the data set used to test the vector map implementation. This extra work was done to create realistic examples, and better understand the relationship between the different dataformats (whereas if completely random examples were used, this would not be as clear).

## geoserver-wms-client 

This folder contains the client implementation of the current map standard -- the server is a GeoServer instance, that had to be set up manually (GeoServer does not have proper automation tools), which took a week to complete. Because of this, the source code for the server instance, is not that interesting.

The folder contains the map client, which was used to test the implementation, and also the performance test (the performance-test folder) and also the result data and generated graphs.

## tilestache-polymaps-client 

The TileStache vector tile map server and generator was tested with PostGIS as a backend, but was too slow and relied on old technology (HTTP), which is why the testing was not included in this paper. Nevertheless, it is included for completeness.

## websockets 

The folder contains implementations of client and server (the websockets subfolder) for the different data formats, and tile generation. It was the early implementation while the author was familiarising himself with the technology and data structures. 

## websockets-new 

The individual implementations in the websockets folder were combined and re-architectured into a single client and server implementation. This re-architecture of the implementation was time-consuming and hard work, but the resulting code is much simpler to inspect, and also ensure that the different data formats are tested on as equal terms as possible.

The performance-tests folder contains both the data aquired when testing, the processing of the data (median filter etc.), as well as the generated graphs and data visualisations.

To start the server, run runserver.py. The server will listen on port 9090. The client will work on a local machine, without a web server, as it uses only the HTML5 open standard and JavaScript. It should be able to connect to the server if the ip-address in client.html is correct. The data format is chosen with a configuration parameter in client.html.
