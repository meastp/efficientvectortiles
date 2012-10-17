// convert string to binary string buffer
function rawStringToBuffer( str ) 
{
    var idx, len = str.length, arr = new Array( len );
    //convert every character to its binary char code number
    for ( idx = 0 ; idx < len ; ++idx ) {
        arr[ idx ] = str.charCodeAt(idx) & 0xFF;
    }
    return new Uint8Array( arr );
}

// create an array buffer from a list of typed arrays and return it
function createArrayBuffer(elements)
        {
            var total_length = 0;
            
            for(var i=0; i < elements.length; i++)
            {
                var obj = elements[i];
                total_length += obj.byteLength;
            }
            
            var raw_buffer = new ArrayBuffer(total_length);
            var raw_buffer_manip = new Uint8Array(raw_buffer);
            
            for(var i=0, offset=0; i < elements.length; i++)
            {
                var obj = elements[i];
                
                raw_buffer_manip.set(obj, offset);
                offset += obj.byteLength;
            }
            
            return raw_buffer;
        }

//calculate an array timestamp to milliseconds
function calculateTimestampToMilliseconds(arr)
{
    total = 0;
    
    if( (arr[0]==0) && (arr[1]==0) && (arr[2]==0) && (arr[3]==0))
    {
        total = (arr[4]*60*1000)+(arr[5]*1000)+(arr[6]);
    }
    else
    {
        console.log("ERROR: Timestamp error!");
        console.log(arr);
    }
    
    return total;
}

//calculate the difference between two timestamps and store it in a new timestamp
function calculateAbsTimestamp(arra, arrb)
{
    var arr = new Array(7);
    
    for(var i=0;i<7;i++)
    {
        if(arra[i]>arrb[i])
        {
            arr[i] = arra[i]-arrb[i];
        }
        else
        {
            arr[i] = arrb[i]-arra[i];
        }
    }
    return arr;
}

//convert or create a typed array timestamp (can be used as a binary format)
function getTimestampAsArray(timestamp)
{
    if( typeof(timestamp) == 'undefined') {
        timestamp = new Date();
    }
    
    arr = new Uint16Array(7);
    arr[0] = timestamp.getFullYear();
    arr[1] = timestamp.getMonth();
    arr[2] = timestamp.getDate();
    arr[3] = timestamp.getHours();
    arr[4] = timestamp.getMinutes();
    arr[5] = timestamp.getSeconds();
    arr[6] = timestamp.getMilliseconds();
    
    return arr;
}

//convert or create a normal array timestamp (used in text formats)
function getTimestampAsTextFriendlyArray(timestamp)
{
    if( typeof(timestamp) == 'undefined') {
        timestamp = new Date();
    }
    
    arr = new Array(7);
    arr[0] = timestamp.getFullYear();
    arr[1] = timestamp.getMonth();
    arr[2] = timestamp.getDate();
    arr[3] = timestamp.getHours();
    arr[4] = timestamp.getMinutes();
    arr[5] = timestamp.getSeconds();
    arr[6] = timestamp.getMilliseconds();
    
    return arr;
}

// convert type to array
function getTypeAsArray(Type){var arr = new Uint8Array(1); arr[0] = Type; return arr;}

// convert array to type
function getType(arr){ return arr[0];}






















