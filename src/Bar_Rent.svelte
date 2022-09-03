<script>

    import * as d3 from 'd3';
    export let data;
    export let filters;
    import { afterUpdate } from 'svelte';

    function extractColumn(arr, column) {
        return arr.map(x => x[column])
    }
    data = data.filter( function(d){
        if(filters[2] === "All NYC"){
            return d;
        }else{
            return d.puma === filters[2]
        }
    })

    //console.log( filters.slice(2,4 ) );
    if (filters[3] === 'recent_built'){
        data = data.filter( function(d){
            return d.recent_built === "1";
        })

    }else{
        console.log('Filter by Recent Alter')
        data = data.filter( function(d){
            return d.recent_alter === "1";
        })
    }

    function BarChart( data ){

        var margin = {top: 20, right: 20, bottom: 20, left: 20},
        width = 1000,
        height = 125;

        var w_ext = width;
        var h_ext = height;

        width = 1000 - margin.left - margin.right,
        height = 125 - margin.top - margin.bottom;

        var svg = d3.select("#bar-chart");
        
        svg = svg.append("svg")
                .attr("width", w_ext )
                .attr("height", h_ext )
                .attr("viewBox", [0, 0, w_ext, h_ext])
                .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
            .append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");

        // Add X axis
        var x = d3.scaleLinear()
            .domain([0, d3.max( extractColumn(data, 'count' ) )])
            .range([ 0, width]);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x))
            .selectAll("text")
            //.attr("transform", "translate(-10,0)rotate(-45)")
            .attr("transform", "translate(15,0)")
            .style("text-anchor", "end");

        // Y axis
        var y = d3.scaleBand()
            .range([ 0, height ])
            .domain(data.map(function(d) { return d.state; }))
            .padding(.1);

        svg.append("g")
            .call(d3.axisLeft(y))
        
            //Bars
        svg.selectAll("myRect")
            .data(data)
            .enter()
            .append("rect")
            .attr("x", x(0) )
            .attr("y", function(d) { return y(d.state); })
            .attr("width", function(d) { return x(d.count); })
            .attr("height", y.bandwidth() )
            .attr("fill", "#333")
        
        return svg;
    }

    let stabs = 0
    let no_stabs = 0
    data.forEach(element => {
        if( element['st_2007'] > 0){
            stabs = stabs + 1
        }else{
            no_stabs = no_stabs + 1
        }    
    });

    let stab_count = [
        {'state':"Y",'count':stabs},
        {'state':"N",'count':no_stabs}
    ];

    afterUpdate(() => {
        document.getElementById('bar-chart').innerHTML = "";
        BarChart(stab_count);
    });

</script>


<div id="bar-chart"></div>