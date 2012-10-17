        
        // a map window projection, with a bounded coordinate window
        function Projection(minx, maxx, miny, maxy)
        {
            this.bbox = { x : {min : minx, max : maxx}, y : {min : miny, max : maxy} };
            
            this.rawbbox = new Float64Array(4);
            this.get_rawbbox = function() //for binary
            {
                this.rawbbox[0] = this.bbox.x.min;
                this.rawbbox[1] = this.bbox.x.max;
                this.rawbbox[2] = this.bbox.y.min;
                this.rawbbox[3] = this.bbox.y.max;
                
                return this.rawbbox;
            }
            this.get_textbbox = function()//for text
            {
                return [this.bbox.x.min, this.bbox.x.max, this.bbox.y.min, this.bbox.y.max];
            }
        }
        
        // a map
        function Map(projection, width, heigth)
        {
            this.width = width;
            this.heigth = heigth;
            
            this.projection = projection;
            
            this.events = d3.dispatch("update"); //event container for the map
            
            this.comp = null; //compare functions
            this.polygon_draw_function = null; // draw polygon
            this.line_draw_function = null; // draw line
            
            function newViewport(self)
            {
                self.comp = 
                {
                x : d3.scale.linear().domain([projection.bbox.x.min, projection.bbox.x.max]).range([0, self.width]), 
                y : d3.scale.linear().domain([projection.bbox.y.min, projection.bbox.y.max]).range([self.heigth, 0])
                }
                
                var compx = self.comp.x;
                var compy = self.comp.y;
                
                self.line_draw_function = d3.svg.line().x(function(d){return compx(d[0]);}).y(function(d){return compy(d[1]);});
                
                var line_draw_function = self.line_draw_function;
                self.polygon_draw_function = function(d){return line_draw_function(d) + "Z";} // SVG path ended with Z is self-closing
            };
            newViewport(this);
            
            this.events.on("update", newViewport); // connect viewport update to event
            
            this.svg = d3.select("#map").append("svg").attr("width", this.width).attr("height", this.heigth); //attach map to div
            
            this.features = this.svg.append("g").attr("id", "features"); //create feature group
        }
        
        //map controls
        function Controls(map)
        {
            
            this.controls = map.svg.append("g").attr("id", "controls");
            
            this.pan = this.controls.append("g");
            
            this.arrowright = this.pan.append("g").attr("id", "arrowright").attr("class", "buttongroup");
            this.arrowright.append("path").attr("class", "button").attr("d", "m 53.299632,45.971635 18.72773,0 0,-17.170169 -18.72773,0 -14.353531,8.585085 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.42448819;stroke-opacity:1");
            this.arrowright.append("path").attr("class", "arrow").attr("d", "m 67.248683,38.012542 0,-1.251991 -5.467029,-5.467031 -1.669322,1.669323 3.241266,3.241267 -23.252938,0 0,2.364873 23.252938,0 -3.241266,3.241267 1.669322,1.669323 5.467029,-5.467031")
                                .attr("style", "font-size:20px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:Ubuntu;-inkscape-font-specification:Ubuntu");
            
            this.arrowdown = this.pan.append("g").attr("id", "arrowdown").attr("class", "buttongroup");
            this.arrowdown.append("path").attr("class", "button").attr("d", "m 28.988243,53.141272 0,18.72773 17.170169,0 0,-18.72773 -8.585085,-14.353531 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.42448819;stroke-opacity:1");
            this.arrowdown.append("path").attr("class", "arrow").attr("d", "m 36.947336,67.090323 1.251991,0 5.467031,-5.467029 -1.669323,-1.669322 -3.241267,3.241266 0,-23.252938 -2.364873,0 0,23.252938 -3.241267,-3.241266 -1.669323,1.669322 5.467031,5.467029")
                                .attr("style", "font-size:20px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:Ubuntu;-inkscape-font-specification:Ubuntu");
            
            this.arrowleft = this.pan.append("g").attr("id", "arrowleft").attr("class", "buttongroup");
            this.arrowleft.append("path").attr("class", "button").attr("d", "m 21.848752,45.971635 -18.7277305,0 0,-17.170169 18.7277305,0 14.353531,8.585085 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.42448819;stroke-opacity:1");
            this.arrowleft.append("path").attr("class", "arrow").attr("d", "m 7.8997058,38.012542 0,-1.251991 5.4670292,-5.467031 1.669322,1.669323 -3.241266,3.241267 23.252938,0 0,2.364873 -23.252938,0 3.241266,3.241267 -1.669322,1.669323 -5.4670292,-5.467031")
                                .attr("style", "font-size:20px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:Ubuntu;-inkscape-font-specification:Ubuntu");
            
            this.arrowup = this.pan.append("g").attr("id", "arrowup").attr("class", "buttongroup");
            this.arrowup.append("path").attr("class", "button").attr("d", "m 28.988243,21.643532 0,-18.7277305 17.170169,0 0,18.7277305 -8.585085,14.353531 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.42448819;stroke-opacity:1");
            this.arrowup.append("path").attr("class", "arrow").attr("d", "m 36.947336,7.6944858 1.251991,0 5.467031,5.4670292 -1.669323,1.669322 -3.241267,-3.241266 0,23.252938 -2.364873,0 0,-23.252938 -3.241267,3.241266 -1.669323,-1.669322 5.467031,-5.4670292")
                                .attr("style", "font-size:20px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:Ubuntu;-inkscape-font-specification:Ubuntu");
            
            this.zoom = this.controls.append("g");
            
            this.plus = this.zoom.append("g").attr("id", "plus").attr("class", "buttongroup");
            this.plus.append("path").attr("class", "button").attr("d", "m 28.98824,151.53223 0,8.65508 17.170169,0 0,-8.65508 z")
                                .attr("style", "fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:1.42448819;stroke-opacity:1");
            this.plus.append("path").attr("class", "symbol").attr("d", "m 36.165929,155.36406 2.814789,0 0,0.99145 -2.814789,0 0,-0.99145")
                                .attr("style", "font-size:11.39590549px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#ffffff;fill-opacity:1;stroke:none;font-family:Ubuntu;-inkscape-font-specification:Ubuntu");
            
            this.zoom5 = this.zoom.append("g").attr("id", "zoom5").attr("class", "buttongroup");
            this.zoom5.append("path").attr("class", "button").attr("d", "m 31.313497,139.44879 0,6.31087 12.519664,0 0,-6.31087 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.03866839;stroke-opacity:1");
            
            this.zoom4 = this.zoom.append("g").attr("id", "zoom4").attr("class", "buttongroup");
            this.zoom4.append("path").attr("class", "button").attr("d", "m 31.313497,127.55826 0,6.31087 12.519664,0 0,-6.31087 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.03866839;stroke-opacity:1");
            
            this.zoom3 = this.zoom.append("g").attr("id", "zoom3").attr("class", "buttongroup");
            this.zoom3.append("path").attr("class", "button").attr("d", "m 31.313497,115.66773 0,6.31087 12.519664,0 0,-6.31087 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.03866839;stroke-opacity:1");
            
            this.zoom2 = this.zoom.append("g").attr("id", "zoom2").attr("class", "buttongroup");
            this.zoom2.append("path").attr("class", "button").attr("d", "m 31.313497,103.7772 0,6.31087 12.519664,0 0,-6.31087 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.03866839;stroke-opacity:1");
            
            this.zoom1 = this.zoom.append("g").attr("id", "zoom1").attr("class", "buttongroup");
            this.zoom1.append("path").attr("class", "button").attr("d", "m 31.313497,91.88667 0,6.310867 12.519664,0 0,-6.310867 z")
                                .attr("style", "fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:1.03866839;stroke-opacity:1");
            
            this.minus = this.zoom.append("g").attr("id", "minus").attr("class", "buttongroup");
            this.minus.append("path").attr("class", "button").attr("d", "m 28.988243,77.459023 0,8.655077 17.170169,0 0,-8.655077 z")
                                .attr("style", "fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:1.42448819;stroke-opacity:1");
            this.minus.append("path").attr("class", "symbol").attr("d", "m 34.963655,81.33072 2.153826,0 0,-2.347557 0.911672,0 0,2.347557 2.153826,0 0,0.900276 -2.153826,0 0,2.358953 -0.911672,0 0,-2.358953 -2.153826,0 0,-0.900276")
                                .attr("style", "font-size:11.39590549px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#ffffff;fill-opacity:1;stroke:none;font-family:Ubuntu;-inkscape-font-specification:Ubuntu");
            
            // Events for the controls
            
            this.events = d3.dispatch("arrowup", "arrowdown", "arrowright", "arrowleft", "plus", "minus"); // event container for controls
            var events = this.events;
            
            this.arrowup.on("click", function(g, i)
                {
                    // SEND EVENT TO LISTENERS
                    events.arrowup();
                });
            this.arrowleft.on("click", function(g, i)
                {
                    // SEND EVENT TO LISTENERS
                    events.arrowleft();
                });
            this.arrowright.on("click", function(g, i)
                {
                    // SEND EVENT TO LISTENERS
                    events.arrowright();
                });
            this.arrowdown.on("click", function(g, i)
                {
                    // SEND EVENT TO LISTENERS
                    events.arrowdown();
                });
                
            this.minus.on("click", function(g, i)
                {
                    // SEND EVENT TO LISTENERS
                    events.minus();
                });
            this.plus.on("click", function(g, i)
                {   
                    // SEND EVENT TO LISTENERS
                    events.plus();
                });
        }
        
        // a feature type
        function FeatureType(map, name, type)
        {
            this.name = name;
            this.type = type;
            
            this.node = map.features.append("g").attr("id", this.name).attr("class", this.type);
        }
