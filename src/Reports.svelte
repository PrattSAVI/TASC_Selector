<script>

    export let data;
    export let filters;

    let lot_th = filters[0];
    let far_th = filters[1];

    let stabs = 0
    let no_stabs = 0


    data = data.filter( function(d){
        if(filters[2] === "All NYC"){
            return d;
        }else{
            return d.puma === filters[2]
        }
    })

    if ( filters[3] === 'recent_built'){
			data = data.filter( function(d){
				return d.recent_built === "1";
			});
    }else if( filters[3] === 'recent_alter'){
        data = data.filter( function(d){
            return d.recent_alter === "1";
        });
    }else if( filters[3] === 'has_merged'){
        data = data.filter( function(d){
            return d.has_merged === "1";
        });
    }else{
        data = data;
    }

    data.forEach(element => {
        if( element['st_2007'] > 0){
            stabs = stabs + 1
        }else{
            no_stabs = no_stabs + 1
        }    
    });


    let perc_stab = Math.round(stabs * 100 / data.length)

    let built = data.filter( (d)=>{
        return d['recent_built'] == "1";
    })

    let alter = data.filter( (d)=>{
        return d['recent_alter'] == "1";
    })

    let merged = data.filter( (d)=>{
        return d['has_merged'] == "1";
    })

    let filtered_data = data.filter( function(d){
        return (d['LotArea_07'] > lot_th ) && (d['availFAR_perc_07'] > far_th ) ;
    })

</script>

<div class="reports">

    <span class="report-title">
    {#if filters[2] != "All NYC"}
        PUMA: {filters[2]}
    {:else}
        All NYC
    {/if}
    </span>
    <hr>
    <div class="stats">
        <p id="1"># of Shown Lots: <span class="num">{data.length}</span></p>
        <p id="1"># of Built Lots: <span class="num">{built.length}</span></p>
        <p id="1"># of Altered Lots: <span class="num">{alter.length}</span></p>
        <p id="1"># of Merged Lots: <span class="num">{merged.length}</span></p>
        <hr>
        <p id="2">% of Lots Included with in the Threshold: <span class="num">{Math.round(filtered_data.length*100/data.length)}%</span></p>
        <p id="3">% of Lots with Rent St. Units: <span class="num">{perc_stab}%</span></p>
    </div>

</div>

<style>

    .num{
        color:rgb(187, 62, 3);
        font-weight: bold;
    }
    hr{
        border:none;
        border-top: 2px solid rgb(187, 62, 3);
        margin: 5px 15px 5px;
    }
    .stats{
        padding: 5px;
    }

    .report-title{
        font-weight: bold;
    }

    .reports{
        display: flex;
        flex-direction: column;
        padding: 5px;
    }

    .stats > p {
        margin:5px;
        font-size: 12pt;
    }

</style>