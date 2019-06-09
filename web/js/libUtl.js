'use strict'

export
function Commas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}


// https://flaviocopes.com/javascript-dates/
export
function GetTime(d = Date())
{
    let dayOfWeek = new Array(7);
    dayOfWeek[0]=  "Sun";
    dayOfWeek[1] = "Mon";
    dayOfWeek[2] = "Tue";
    dayOfWeek[3] = "Wed";
    dayOfWeek[4] = "Thu";
    dayOfWeek[5] = "Fri";
    dayOfWeek[6] = "Sat";
    
    let monthOfYear = new Array(12);
    monthOfYear[0] = "Jan";
    monthOfYear[1] = "Feb";
    monthOfYear[2] = "Mar";
    monthOfYear[3] = "Apr";
    monthOfYear[4] = "May";
    monthOfYear[5] = "Jun";
    monthOfYear[6] = "Jul";
    monthOfYear[7] = "Aug";
    monthOfYear[8] = "Sep";
    monthOfYear[9] = "Oct";
    monthOfYear[10] = "Nov";
    monthOfYear[11] = "Dec";
    
    let t = {
        dayOfWeek : dayOfWeek[d.getDay()],
        
        month : monthOfYear[d.getMonth()],
        
        dayOfMonth : d.getDate().toString().length == 1 ? ("0" + d.getDate()) : d.getDate(),
        
        hhmmss : (d.getHours().toString().length   == 1 ? ("0" + d.getHours()  ) : d.getHours()  ) + ":" +
                 (d.getMinutes().toString().length == 1 ? ("0" + d.getMinutes()) : d.getMinutes()) + ":" +
                 (d.getSeconds().toString().length == 1 ? ("0" + d.getSeconds()) : d.getSeconds()),
    };
    
    return t;
}














