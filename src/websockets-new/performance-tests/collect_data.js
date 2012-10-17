ptest = new Object();

ptest.results = new Object();

ptest.addResult = function(group_name, result)
{
    if(typeof(this.results[group_name]) == 'undefined')
    {
        this.results[group_name] = new Array();
    }
    this.results[group_name].push(result);
}

ptest.extractResultsFeatures = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(this.results[group_name][i].features);
            
            //console.log(result_list[group_name]);
        }
    }
    
    return result_list;
}

ptest.extractResultsCoordinates = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(this.results[group_name][i].coordinates);
            
            //console.log(result_list[group_name]);
        }
    }
    
    return result_list;
}

ptest.extractResultsCoordinatesFeatures = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            var data = new Array(2);
            data[0] = this.results[group_name][i].coordinates;
            data[1] = this.results[group_name][i].features;
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(data);
            
            //console.log(result_list[group_name]);
        }
    }
    
    //console.log(JSON.stringify(arr));
    
    console.log(result_list);
    
    for(var group_name in result_list)
    {
        for(var table_name in result_list[group_name])
        {
            result_list[group_name][table_name].sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); });
        }
    }
    
    console.log(result_list);
    
    return result_list;
}

ptest.extractResultsKBFeatures = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            var data = new Array(2);
            data[0] = this.results[group_name][i].data_size_kb;
            data[1] = this.results[group_name][i].features;
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(data);
            
            //console.log(result_list[group_name]);
        }
    }
    
    //console.log(JSON.stringify(arr));
    
    console.log(result_list);
    
    for(var group_name in result_list)
    {
        for(var table_name in result_list[group_name])
        {
            result_list[group_name][table_name].sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); });
        }
    }
    
    console.log(result_list);
    
    return result_list;
}

ptest.extractFeaturesQueryLatencies = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            //console.log(this.results[group_name][i]);
            
            var data = new Array(2);
            
            data[0] = this.results[group_name][i].query_time;// + this.results[group_name][i].server_processing_time + this.results[group_name][i].client_processing_time;
            data[1] = this.results[group_name][i].features;
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(data);
            
            //console.log(result_list[group_name]);
        }
    }
    
    //console.log(JSON.stringify(arr));
    /*
    console.log(result_list);
    
    for(var group_name in result_list)
    {
        for(var table_name in result_list[group_name])
        {
            result_list[group_name][table_name].sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); });
        }
    }
    */
    console.log(result_list);
    
    return result_list;
}

ptest.extractFeaturesServerProcessingLatencies = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            //console.log(this.results[group_name][i]);
            
            var data = new Array(2);
            
            data[0] = this.results[group_name][i].server_processing_time //+ this.results[group_name][i].client_processing_time;
            data[1] = this.results[group_name][i].features;
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(data);
            
            //console.log(result_list[group_name]);
        }
    }
    
    //console.log(JSON.stringify(arr));
    /*
    console.log(result_list);
    
    for(var group_name in result_list)
    {
        for(var table_name in result_list[group_name])
        {
            result_list[group_name][table_name].sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); });
        }
    }
    
    console.log(result_list);
    */
    return result_list;
}

ptest.extractFeaturesClientProcessingLatencies = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            //console.log(this.results[group_name][i]);
            
            var data = new Array(2);
            
            data[0] = this.results[group_name][i].client_processing_time;
            data[1] = this.results[group_name][i].features;
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(data);
            
            //console.log(result_list[group_name]);
        }
    }
    
    //console.log(JSON.stringify(arr));
    /*
    console.log(result_list);
    
    for(var group_name in result_list)
    {
        for(var table_name in result_list[group_name])
        {
            result_list[group_name][table_name].sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); });
        }
    }
    
    console.log(result_list);
    */
    return result_list;
}

ptest.extractFeaturesLatencies = function()
{
    var result_list = new Object();
    
    for(var group_name in this.results)
    {
        //result_list[group_name] = new Object();
        
        for(var i=0;i<this.results[group_name].length;i++)
        {
            if(typeof(result_list[this.results[group_name][i].name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name] = new Object();
            }
            
            if(typeof(result_list[this.results[group_name][i].name][group_name]) == 'undefined')
            {
                result_list[this.results[group_name][i].name][group_name] = new Array();
            }
            
            //console.log(this.results[group_name][i]);
            
            var data = new Array(4);
            
            data[0] = this.results[group_name][i].query_time;
            data[1] = this.results[group_name][i].server_processing_time;
            data[2] = this.results[group_name][i].client_processing_time;
            data[3] = this.results[group_name][i].features;
            
            //console.log(data);
            
            result_list[this.results[group_name][i].name][group_name].push(data);
            
            //console.log(result_list[group_name]);
        }
    }
    
    console.log(result_list);
    
    return result_list;
}
