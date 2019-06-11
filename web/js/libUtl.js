'use strict'

export
function Commas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}


// https://flaviocopes.com/javascript-dates/
export
function GetTime(d = new Date())
{
    let dayOfWeekArr = new Array(7);
    dayOfWeekArr[0] = "Sun";
    dayOfWeekArr[1] = "Mon";
    dayOfWeekArr[2] = "Tue";
    dayOfWeekArr[3] = "Wed";
    dayOfWeekArr[4] = "Thu";
    dayOfWeekArr[5] = "Fri";
    dayOfWeekArr[6] = "Sat";
    
    let monthOfYearArr = new Array(12);
    monthOfYearArr[0]  = "Jan";
    monthOfYearArr[1]  = "Feb";
    monthOfYearArr[2]  = "Mar";
    monthOfYearArr[3]  = "Apr";
    monthOfYearArr[4]  = "May";
    monthOfYearArr[5]  = "Jun";
    monthOfYearArr[6]  = "Jul";
    monthOfYearArr[7]  = "Aug";
    monthOfYearArr[8]  = "Sep";
    monthOfYearArr[9]  = "Oct";
    monthOfYearArr[10] = "Nov";
    monthOfYearArr[11] = "Dec";
    
    let dayOfWeek = dayOfWeekArr[d.getDay()];
    
    let yyyy = d.getFullYear();
    let mm   = (d.getMonth() + 1).toString().length == 1 ?  ("0" + (d.getMonth() + 1)) : (d.getMonth() + 1);
    let dd   = (d.getDay() + 1).toString().length == 1 ?  ("0" + (d.getDay() + 1)) : (d.getDay() + 1);
    
    let month = monthOfYearArr[d.getMonth()];
    
    let dayOfMonth = d.getDate().toString().length == 1 ? ("0" + d.getDate()) : d.getDate();
    
    let HH = (d.getHours().toString().length   == 1 ? ("0" + d.getHours()  ) : d.getHours()  );
    let MM = (d.getMinutes().toString().length == 1 ? ("0" + d.getMinutes()) : d.getMinutes());
    let SS = (d.getSeconds().toString().length == 1 ? ("0" + d.getSeconds()) : d.getSeconds());
    
    let hhmmss = HH + ":" + MM + ":" + SS;
    
    let yyyymmdd = yyyy + "-" + mm + "-" + dd;
    
    let tsFull = yyyymmdd + " " + hhmmss;

    
    let t = {
        dayOfWeek,
        yyyy,
        mm,
        dd,
        
        month,
        
        dayOfMonth,
        
        HH,
        MM,
        SS,
        
        hhmmss,
        
        yyyymmdd,
        
        tsFull,
    };
    
    return t;
}


export
function Log(logStr)
{
    let t = GetTime();
    
    let stackStr = new Error().stack.toString().replace(/\n/, '').replace( /  +/g, ' ' )
    let callerStr = stackStr.split(' ')[5];
    
    let logStamped = `[${callerStr}]\n${t.tsFull}: ${logStr}`;
    
    console.log(logStamped);
}


















































