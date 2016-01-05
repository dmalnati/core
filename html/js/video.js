"use strict";

// #include("graph.js")








	
class DomLogger
{
	constructor(domContainer)
	{
		this.domContainer_ = domContainer;
		this.timeLastMs_   = null;
	}
	
	Log(str)
	{
		let timeNowMs  = (new Date()).getTime();
		let timeDiffMs = timeNowMs - this.timeLastMs_;
		if (!this.timeLastMs_)
		{
			timeDiffMs = 0;
		}
		this.timeLastMs_ = timeNowMs;
		
		let domDiv = document.createElement("div");
		
		domDiv.appendChild(document.createTextNode("[+" + timeDiffMs + "]: "));
		domDiv.appendChild(document.createTextNode(str));
		domDiv.appendChild(document.createElement("br"));
		
		this.domContainer_.appendChild(domDiv);
	}
}





// Properties to observe:
// - currentTime - where in the video stream, as a float number of seconds, are you?
// - 
// 
// State:
// - ended -- boolean yes/no
// - paused -- boolean yes/no
// - error -- indicates state of video (perhaps good for WebRTC?)
// - networkState -- enum representing state of video tag starting up and gathering
//                   data.
// - readyState -- enum representing state of whether video can play now, and whether
//                 it can play future frames.
//
// Other:
// - buffered
//   - list of time ranges you can jump to, already downloaded.  perhaps interesting...
// - played
//   - list of times already played

// Events to observe:
// - abort - when loading is aborted
// - 


class VideoObserver
{
	constructor(domContainer, domVideo)
	{
		// Retain constructor parameters
		this.domContainer_ = domContainer;
		this.domVideo_     = domVideo;
		
		// Create local structures
		this.cbFnList_   = [];
		this.timeLastMs_ = null;
	}
	
	Start()
	{
		// Events
		this.MonitorEventLoadingProcess();
		this.MonitorEventResize();
		this.MonitorEventNetwork();
		this.MonitorFrameRate();
		
		// Properties
		this.MonitorPropertyCurrentTime();
		
		// Set up periodic callback
		this.OnTimeout();
	}
	
	OnTimeout()
	{
		let timeNowMs = (new Date()).getTime();
		
		for (let cbFn of this.cbFnList_)
		{
			let rateScalingFactor = 0;
			
			if (this.timeLastMs_)
			{
				rateScalingFactor = 1000.0 / (timeNowMs - this.timeLastMs_);
			}
			
			cbFn(timeNowMs, this.timeLastMs_, rateScalingFactor);
		}
		
		this.timeLastMs_ = timeNowMs;
		
		setTimeout(() => this.OnTimeout(), 1000);
	}
	
	OnReportTime(cbFn)
	{
		this.cbFnList_.push(cbFn);
	}
	
	PlaceContainer(domContainer)
	{
		this.domContainer_.appendChild(domContainer);
	}
	
	MonitorPropertyCurrentTime()
	{
		// Create container for chart
		let domContainer = document.createElement("div");
		
		// create chart object
		let chartTs = new ChartTimeSeries(() => {
			chartTs.SetUp(domContainer, "CurrentTime", "delta");
			
			this.PlaceContainer(domContainer);

			// set up some effectively static variables
			let currentTimeLast;
			
			// Set up callback handler
			this.OnReportTime((timeNowMs, timeLastMs, rateScalingFactor) => {
				let currentTime = this.domVideo_.currentTime;
				
				if (currentTimeLast && timeLastMs)
				{
					let diff = (currentTime - currentTimeLast) * rateScalingFactor;
					
					chartTs.AddSample(timeNowMs, diff);
				}
				
				currentTimeLast = currentTime;
			})
		});
	}
	
	MonitorEventLoadingProcess()
	{
		// create container for log messages
		let domContainer = document.createElement("div");
		domContainer.style.height = "250px";
		domContainer.style.overflowY = "scroll";
		this.PlaceContainer(domContainer);
		
		// Create a logger
		let dl = new DomLogger(domContainer);
		
		dl.Log("Monitoring Loading Process")
		
		this.domVideo_.onloadstart = () => {
			dl.Log("OnLoadStart");
		};
		
		this.domVideo_.ondurationchange = () => {
			dl.Log("OnDurationChange");
		};
		
		this.domVideo_.onloadedmetadata = () => {
			dl.Log("OnLoadedMetaData");
		};
		
		this.domVideo_.onloadeddata = () => {
			dl.Log("OnLoadedData");
		};
		
		this.domVideo_.onprogress = () => {
			dl.Log("OnProgress");
		};
		
		this.domVideo_.oncanplay = () => {
			dl.Log("OnCanPlay");
		};
		
		this.domVideo_.oncanplaythrough = () => {
			dl.Log("OnCanPlayThrough");
		};
	}
	
	MonitorEventResize()
	{
		// create container for log messages
		let domContainer = document.createElement("div");
		domContainer.style.height = "100px";
		domContainer.style.overflowY = "scroll";
		this.PlaceContainer(domContainer);
		
		// Create a logger
		let dl = new DomLogger(domContainer);
		
		dl.Log("Monitoring Resize")
		
		this.domVideo_.onresize = () => {
			dl.Log("OnResize: " + this.domVideo_.videoWidth + 
			       "x"          + this.domVideo_.videoHeight);
		};
		
	}

	MonitorEventNetwork()
	{
		// create container for log messages
		let domContainer = document.createElement("div");
		domContainer.style.height = "100px";
		domContainer.style.overflowY = "scroll";
		this.PlaceContainer(domContainer);
		
		// Create a logger
		let dl = new DomLogger(domContainer);
		
		dl.Log("Monitoring Network")
		
		// Watch for waiting events
		this.domVideo_.onwaiting = () => {
			dl.Log("OnWaiting");
		};
		
		// Watch for changes to readyState
		this.OnReportTime((timeNowMs, timeLastMs, rateScalingFactor) => {
			console.log("readyState: " + this.domVideo_.readyState)
		});
		
		
	}

	
	MonitorFrameRate()
	{
		// Create container for chart
		let domContainer = document.createElement("div");
		
		// create chart object
		let chartTs = new ChartTimeSeries(() => {
			chartTs.SetUp(domContainer, "FrameCount", "delta");
			
			this.PlaceContainer(domContainer);

			// set up some effectively static variables
			let valLast;
			
			// Set up callback handler
			this.OnReportTime((timeNowMs, timeLastMs, rateScalingFactor) => {
				let val = this.domVideo_.webkitDecodedFrameCount;
				
				if (valLast && timeLastMs)
				{
					let diff = (val - valLast) * rateScalingFactor;
					
					chartTs.AddSample(timeNowMs, diff);
				}
				
				valLast = val;
			})
		});
	}
	
	
	
}














