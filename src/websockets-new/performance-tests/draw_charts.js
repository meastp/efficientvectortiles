// plot CoordinatesLatencies
// plot FeaturesKBs


// plot(#divname, groups, opts)
// create_data_group(array, opts)
// process_data_array - (array, columns [1,2], callback function on every value) - get mean and standard deviation
// generate_normal_distribution (from, to, mean, std_dev) -> data, array [i, distr]


function getDataSeries(data)
{
    
    var series_list = Array();
    
    for(var group in data)
    {
        series = new Object();
        
        series.label = group;
        
        series.data = getFilteredArray(data[group], 5).filtered_with_tolerance;//findLineByLeastSquares(data[group]);
        
        
        series_list.push(series);
    }
    
    return series_list;
}

function getDataSeriesLinearRegression(data)
{
    
    var series_list = Array();
    
    for(var group in data)
    {
        series = new Object();
        
        series.label = group;
        
        series.data = findLineByLeastSquares(data[group]);
        
        series.hoverable = true;
        
        
        series_list.push(series);
    }
    
    return series_list;
}

function swapArray(array)
{
    for(var i=0;i<array.length;i++)
    {
        var temp = array[i][0];
        array[i][0] = array[i][1];
        array[i][1] = temp;
    }
    
    return array;
}

function createTicks(range, unit)
{
    var arr = new Array();
    
    for(var i=0;i<range.length;i++)
    {
        arr.push([range[i], range[i]+" "+unit]);
    }
    
    return arr;
}
