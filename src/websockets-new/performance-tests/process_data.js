function calculateStandardDistribution(data_array, range)
{
    alert("empty");
}

function getColumnAsArray(array, accessor)
{
    var result_array = new Array();
    for(var i=0;i<array.length;i++)
    {
        result_array.push(accessor(array[i]));
    }
    return result_array;
}

function setArrayAsColumn(array, column, accessor)
{
    for(var i=0;i<array.length;i++)
    {
        accessor(array, column, i);
    }
}

function _applyMedianFilter(array, window_size)
{
    if(Math.floor(window_size/2.0) == Math.ceil(window_size/2.0))
    {
        alert("Error: even numbered window not possible");
    }
    
    var result_array = array.slice(0, array.length+1);

    var lower_bound = 0;
    var upper_bound = window_size;
    
    for(var i=0;i<array.length;i++)
    {
        
        var window = array.slice(lower_bound, upper_bound);
        var t = window.slice(0, window.length+1);
        //console.log("Window");
        //console.log(t);
        window = window.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        //console.log(window);
        
        var value_index = Math.floor((window_size/2));
        var median = window[value_index];
        
        //console.log(median);
        //console.log(result_array[lower_bound+value_index]);
        result_array[lower_bound+value_index] = median;
        //console.log(result_array[lower_bound+value_index]);
        
        if(upper_bound >= array.length)
        {
            break;
        }
        else
        {
            lower_bound++;
            upper_bound++;
        }       
        
    }
    
    return result_array;
}

function applyComplexMedianFilter(array, window_size)
{
    if(Math.floor(window_size/2.0) == Math.ceil(window_size/2.0))
    {
        alert("Error: even numbered window not possible");
    }
    
    var result_array = array.slice(0, array.length+1);


    result_array = result_array.sort(function(a, b) { return (a[1] < b[1] ? -1 : (a[1] > b[1] ? 1 : 0)); }); // sorted on features


    var lower_bound = 0;
    var upper_bound = window_size;
    
    for(var i=0;i<result_array.length;i++)
    {
        
        var window = new Array();
        
        for(var j=lower_bound; j<upper_bound; j++)
        {
            window.push(result_array[j][0]);
        }
        
        var t = window.slice(0, window.length+1);
        //console.log("Window");
        //console.log(t);
        window = window.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        //console.log(window);
        
        var value_index = Math.floor((window_size/2));
        var median = window[value_index];
        
        //console.log(median);
        
        result_array[i][0] = median;
        
        //console.log(result_array[i])
        
        
        if(upper_bound < array.length)
        {
            lower_bound++;
            upper_bound++;
        }       
        
    }
    
    return result_array;
}

function applyMedianFilter(array, column_number, window_size)
{
    var values_column = getColumnAsArray(array, function(value){return value[column_number];});

    var filtered_values_column = _applyMedianFilter(values_column, window_size);

    setArrayAsColumn(array, filtered_values_column, function(array, column, i){array[i][column_number] = column[i]});
}


function calculateMeanValues(array, range, tolerance)
{
    result_array = new Array();
    
    for(var i = 0; i<range.length;i++)
    {
        var value_lower = range[i]-tolerance;
        var value_upper = range[i]+tolerance;
        
        var values = new Array();
        
        var sum = 0.0;
        var count = 0;
        
        for(var j=0;j<array.length;j++)
        {
            if((array[j][1]>value_lower) && (array[j][1]<value_upper))
            {
                count++;
                sum += array[j][0];
                
                values.push(array[j][0]);
            }
        }
        
        var mean = sum/count;
        
        /*
        var std_dev_square_sum = 0.0;
        for(var j=0;j<values.length;j++)
        {
            std_dev_square_sum += Math.pow((values[j][0]-mean),2);
        }
        var std_dev = Math.sqrt(std_dev_square_sum/count);
        */
        
        result_array.push([ sum/count , range[i] ]);
    }
    
    return result_array;
}

function _getValues(array, index, column, tolerance, value_column)
{
    
    var value = array[index][column];
    
    var value_list = new Object();
    value_list.x = new Array();
    value_list.y = new Array();
    
    for(var i=index;i<index+tolerance;i++)
    {
        if(i>=(array.length)) break;
        
        value_list.x.push(array[i][0]);
        value_list.y.push(array[i][1]);
    }
    
    /*
    var ival = value;
    var i = index;
    while((i-->0) && (ival>(value-tolerance)))
    {
        ival = array[i][column];
        
    }
    
    var jval = value;
    var j = index;
    
    while((j++<array.length-1) && (jval<(value+tolerance)))
    {
        value_list.x.push(array[j][0]);
        value_list.y.push(array[j][1]);
        jval = array[j][column];
    }
    */
    /*
    var sum=0.0;
    for(var i=0;i<value_list.length;i++)
    {
        sum+=value_list[i][column];
    }
    
    var mean = sum/value_list.length;
    */
    return value_list;
}

function complexMedianFilter(array, parts)
{
    var result_array = array.sort(function(a, b) { return (a[1] < b[1] ? -1 : (a[1] > b[1] ? 1 : 0)); }); // sorted on features
    //var value_array = array.sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); }); // sorted on values
    
    var result = new Array();
    
    result.push([0,0]);
    
    //var parts = 10;
    var feature_size = Math.ceil((array[array.length-1][1] - array[0][1])/parts);
    console.log(feature_size);
    
    var bite_size = Math.ceil(array.length/parts);
    
    var i=0;
    for(;i<result_array.length;i+=bite_size)
    {
        
        var values = _getValues(result_array, i, 1, bite_size, 0);
        //var values = _getValues(value_array, i, 0, 500, 1);
        
        values.x = values.x.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        values.y = values.y.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        
        
        
        var median_x = NaN;
        if(Math.floor(values.x.length/2) == Math.ceil(values.x.length/2))
        {
            median_x = (values.x[Math.floor(values.x.length/2)-1] + values.x[Math.floor(values.x.length/2)])/2.0;
        }
        else
        {
            median_x = values.x[Math.floor(values.x.length/2)];
        }
        
        var median_y = NaN;
        if(Math.floor(values.y.length/2) == Math.ceil(values.y.length/2))
        {
            median_y = (values.y[Math.floor(values.y.length/2)-1] + values.y[Math.floor(values.y.length/2)])/2.0;
        }
        else
        {
            median_y = values.y[Math.floor(values.y.length/2)];
        }
        
        
        result.push([median_x, median_y]);
        
//        if(i>result_array.length-10)
//        {
//        console.log(values.x);
//        console.log(values.y);
//        console.log([median_x, median_y]);
//        }
    }
    
    // Last window
    
    console.log("sdfas");
    console.log(bite_size*(parts-1));
    console.log(array.length);
    
    console.log(i-bite_size);
    i = i-bite_size;
    var chunk_size = (array.length-(i-bite_size))
    while(chunk_size>25)
    {
        var values = _getValues(result_array, i, 1, chunk_size, 0);
        
        values.x = values.x.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        values.y = values.y.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        
        var median_x = NaN;
        if(Math.floor(values.x.length/2) == Math.ceil(values.x.length/2))
        {
            median_x = (values.x[Math.floor(values.x.length/2)-1] + values.x[Math.floor(values.x.length/2)])/2.0;
        }
        else
        {
            median_x = values.x[Math.floor(values.x.length/2)];
        }
        
        var median_y = NaN;
        if(Math.floor(values.y.length/2) == Math.ceil(values.y.length/2))
        {
            median_y = (values.y[Math.floor(values.y.length/2)-1] + values.y[Math.floor(values.y.length/2)])/2.0;
        }
        else
        {
            median_y = values.y[Math.floor(values.y.length/2)];
        }
        
        console.log(values)
        //console.log([median_x, median_y]);
        
        result.push([median_x, median_y]);
        
        chunk_size = Math.floor(chunk_size/3);
        i += (Math.floor(2*(chunk_size/3)));
    }
    //result.push([])
    
    result = result.sort(function(a, b) { return (a[1] < b[1] ? -1 : (a[1] > b[1] ? 1 : 0)); }); // sorted on features
    
    return result;

}

function applyComplexMeanFilter(array, window_size)
{
    
    var result_array = array.slice(0, array.length+1);
    result_array = result_array.sort(function(a, b) { return (a[1] < b[1] ? -1 : (a[1] > b[1] ? 1 : 0)); }); // sorted on features

    var result_arr = new Array();
    
    for(var lower=0,upper=window_size;upper<result_array.length;)
    {
        if(upper>result_array.length){ upper = result_array.length;}
        
        var window = new Array();
        
        var sum_0 = 0.0;
        var sum_1 = 0.0;
        
        var j = lower;
        var value = result_array[j][0];
        while((j<result_array.length) && (result_array[j][0] < (value+window_size)))
        {
            window.push(result_array[j]);
            sum_0 += result_array[j][0];
            sum_1 += result_array[j][1];
            
            j++;
        }
        
        //var t = window.slice(0, window.length+1);
        //console.log("Window");
        //console.log(t);
        //window = window.sort(function(a, b) { return (a < b ? -1 : (a > b ? 1 : 0)); });
        //console.log(window);
        
        //console.log(median);
        
        result_arr.push([sum_0/window.length, sum_1/window.length])
        
        lower += window.length;
        upper += window.length;
        
    }
    
    return result_arr;
}
                
function getFilteredArray(array, window_size, parts)
{
    if(typeof(window_size)=='undefined')
    {
        window_size = 9;
    }
    var test_test_array = array;
    test_test_array = complexMedianFilter(test_test_array, parts);
    //test_test_array = applyMedianFilter(array, 0, 5)
    //test_test_array = applyComplexMedianFilter(array, 15);
    //test_test_array = applyComplexMeanFilter(test_test_array, 5);
    
    //array = array.sort(function(a, b) { return (a[1] < b[1] ? -1 : (a[1] > b[1] ? 1 : 0)); });
    
    applyMedianFilter(array, 0, window_size);
    
    //array = array.sort(function(a, b) { return (a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0)); });
    
    //applyMedianFilter(array, 1, 3);
    
    array = array.sort(function(a, b) { return (a[1] < b[1] ? -1 : (a[1] > b[1] ? 1 : 0)); });
    
    array = array.slice(0, array.length-Math.floor(window_size/2));
    
    
    filter_values_array = new Array();
    for(var i=0; i<600; i+=25){ filter_values_array.push(i);}
    
    array_filtered = calculateMeanValues(array, filter_values_array, 50);
    
    applyMedianFilter(array_filtered, 0, 5);
    
    return { filtered : test_test_array, filtered_with_tolerance : array_filtered };
}
