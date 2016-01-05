

////////////////////////////////
//
// Google Library Loader
//
////////////////////////////////

function LoadGoogleLibsAsync(cbReady)
{
    var domScript = document.createElement("script");

    domScript.onload = function() {
        google.load("visualization", 1, {
            packages: ["corechart"],
            callback: cbReady
        });
    };

    document.head.appendChild(domScript);

    domScript.async = false;
    domScript.src   = "https://www.google.com/jsapi";
}






////////////////////////////////
//
// Google Time-Series Chart
//
////////////////////////////////

function ChartTimeSeries(cbReady)
{
    var t = this;

// Private

var data_         = null;
var chart_        = null;
var chartOptions_ = {};
var domContainer_ = null;


// Public

t.GetDomContainer = function()
{
	return domContainer_;
}

t.SetUp = function(domContainer, title, seriesName)
{
	domContainer_ = domContainer;
	
    data_ = new google.visualization.DataTable();
    data_.addColumn('datetime', "Time");
    data_.addColumn('number', seriesName);

    chartOptions_ = {
        title: title,
        chartArea: {
            top: "10%",
            left: "10%",
            width: "80%",
            height: "80%"
        },
        legend: {
            position: "in",
            alignment: "end"
        }
    };

    chart_ = new google.visualization.LineChart(domContainer);
    chart_.draw(data_, chartOptions_);

    window.addEventListener("resize", function () {
        requestAnimationFrame(function () {
            chart_.draw(data_, chartOptions_);
        });
    });
}

t.AddSample = function(ts, val)
{
    data_.addRows([
        [
            new Date(ts),
            val
        ]
    ]);
    chart_.draw(data_, chartOptions_);
}

t.Clear = function()
{
    data_.removeRows(0, data_.getNumberOfRows());
    chart_.draw(data_, chartOptions_);
}


LoadGoogleLibsAsync(cbReady);

}





////////////////////////////////
//
// Google Histogram Chart
//
////////////////////////////////


function ChartHistogram(cbReady)
{
    var t = this;

// Private

var data_         = null;
var chart_        = null;
var chartOptions_ = {};
var domContainer_ = null;


// Public

t.GetDomContainer = function()
{
	return domContainer_;
}

t.SetUp = function(domContainer, title, seriesName, bucketSize)
{
	domContainer_ = domContainer;
	
    data_ = new google.visualization.DataTable();
    data_.addColumn('number', seriesName);

    chartOptions_ = {
        title: title,
        histogram: {
            bucketSize: bucketSize,
            hideBucketItems: true
        },
        hAxis: {
            maxTextLines: 1,
            slantedText: false
        },
        chartArea: {
            top: "10%",
            left: "10%",
            width: "80%",
            height: "80%"
        },
        legend: {
            position: "in",
            alignment: "end"
        }
    };

    chart_ = new google.visualization.Histogram(domContainer);
    chart_.draw(data_, chartOptions_);

    window.addEventListener("resize", function () {
        requestAnimationFrame(function () {
            chart_.draw(data_, chartOptions_);
        });
    });
}

t.AddSample = function(val)
{
    data_.addRows([
        [
            val
        ]
    ]);
    chart_.draw(data_, chartOptions_);
}

t.Clear = function()
{
    data_.removeRows(0, data_.getNumberOfRows());
    chart_.draw(data_, chartOptions_);
}


LoadGoogleLibsAsync(cbReady);

}












