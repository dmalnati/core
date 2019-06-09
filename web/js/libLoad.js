'use strict'





// https://jeremenichelli.io/2016/04/patterns-for-a-promise-based-initialization/
export
function LoadScriptAsPromise(url) {
    return new Promise(function(resolve, reject) {
        let script = document.createElement('script');

        script.async = true;
        script.src = url;

        script.onload = resolve;
        script.onerror = reject;

        document.head.appendChild(script);   
    });
}


export
function DocEventListenerAsPromise(eventName)
{
    let eventFn;
    
    let promise = new Promise((resolve) => {
        eventFn = resolve;
    });
    
    document.addEventListener(eventName, eventFn);
    
    return promise;
}












