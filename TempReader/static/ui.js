/// <reference path="jquery.d.ts" />
/// <reference path="jquery.flot.d.ts" />
$(function () {
    var sensor_info = {
        "28-0000067a9b24": {
            "name": "Raumtemperatur Wohnzimmer",
            "color": "#FF0000",
            "yaxis": 1
        },
        "28-0415a4658dff": {
            "name": "Zufluss Wohnzimmer",
            "color": "#CF0000",
            "yaxis": 2
        },
        "28-0415a40bafff": {
            "name": "Heizkörper Wohnzimmer",
            "color": "#9F0000",
            "yaxis": 2
        },
        "28-0415a463d4ff": {
            "name": "Raumtemperatur Kinderzimmer",
            "color": "#00FF00",
            "yaxis": 1
        },
        "28-0415a40a21ff": {
            "name": "Zufluss Kinderzimmer",
            "color": "#00CF00",
            "yaxis": 2
        },
        "28-0315a47057ff": {
            "name": "Heizkörper Kinderzimmer",
            "color": "#009F00",
            "yaxis": 2
        },
        "outside": {
            "name": "Außentemperatur",
            "color": "#0000FF",
            "yaxis": 2
        }
    };
    var options = {
        lines: {
            show: true
        },
        points: {
            show: false
        },
        xaxes: [{
            mode: "time",
            timezone: "browser",
            timeformat: "%H:%M"
        }],
        yaxes: [{ position: "right" }, { position: "left" }],
        legend: {
            show: false
        },
        grid: {
            hoverable: true
        }
    };
    var series = {};
    function isToday(timestamp) {
        var date = new Date(timestamp);
        var today = new Date();
        return date.getDate() == today.getDate() && date.getMonth() == today.getMonth() && date.getFullYear() == today.getFullYear() && date.getHours() >= 6;
    }
    function cleanUp(data) {
        while (data.length > 0 && !isToday(data[0][0])) {
            data.shift();
        }
    }
    function valuesAsArray(a) {
        var array_values = [];
        for (var sensor in a) {
            var data = a[sensor];
            cleanUp(data);
            array_values.push({
                data: data,
                yaxis: sensor_info[sensor].yaxis,
                label: sensor_info[sensor].name,
                color: sensor_info[sensor].color
            });
        }
        return array_values;
    }
    function load() {
        $.get("/sensors", function (newData) {
            var time = Date.now();
            for (var sensor in newData) {
                series[sensor].push([time, newData[sensor].temperature]);
            }
            $.plot($("#placeholder"), valuesAsArray(series), options);
        });
    }
    $("<div id='tooltip'></div>").css({
        position: "absolute",
        display: "none",
        border: "1px solid #fdd",
        padding: "2px",
        "background-color": "#fee",
        opacity: 0.80
    }).appendTo("body");
    $("#placeholder").bind("plothover", function (event, pos, item) {
        if (item) {
            var y = item.datapoint[1].toFixed(2);
            $("#tooltip").html(item.series.label + " = " + y).css({ top: item.pageY + 5, left: item.pageX + 5 }).fadeIn(200);
        }
        else {
            $("#tooltip").hide();
        }
    });
    $.get("/sensors/history", function (data) {
        series = data;
        $.plot($("#placeholder"), valuesAsArray(series), options);
    });
    setInterval(function () { return load(); }, 60000);
});
//# sourceMappingURL=ui.js.map