<script>

	import Histogram_LOT from "./Hist_LOT.svelte";
	import Histogram_FAR from "./Hist_FAR.svelte";
	import Slider_LOT from './Slider_LOT.svelte';
	import Slider_FAR from './Slider_FAR.svelte';
	import BarChart from "./Bar_Rent.svelte"
	import Reports from "./Reports.svelte"
	import PumaFilter from "./DD_PUMA.svelte"	
	import BuiltFilter from "./RecentFilter.svelte"
	import * as d3 from 'd3';

	//Format function
	const row = function (data) {
		data["LotArea_07"] = +data["LotArea_07"];
		data["availFAR_perc_07"] = +data["availFAR_perc_07"];
		data["AssedImprov_perc_07"] = +data["AssedImprov_perc_07"];
		return data;
	};

	//Lazy loading, returns a promise
	async function loadData() {
		const temp1 = await d3.csv("data/20220414_Altered.csv", row).then((data) => {
			console.log( data );
			return data;
		});
		return temp1;
	};

	//Python equivalnet of .tolist()
	const arrayColumn = (arr, n) => arr.map(x => x[n]);

	//Vars to feed to functions
	let minmax_lot = ["Lot Area: ",1000, 40000];
	let lotslider_value=5000;

	let minmax_far = ["Av. FAR %: ", -100, 100];
	let farslider_value=0;

	let recent_filter = 'all';

	$: puma_filter = "All NYC";
	$: filters = [lotslider_value,farslider_value,puma_filter,recent_filter];

	//dispatched value
	function handle_puma(event){
		puma_filter = event.detail.text;
		filters[2] = puma_filter;
	}

	//dispatched value
	function handle_recent(event){
		recent_filter = event.detail.text;
		filters[3] = recent_filter;
	}

	// filter by puma
	function filter_data(data,column){

		let data1 = data.filter( function(d){
			if(filters[2] === "All NYC"){
				return d;
			}else{
				return d.puma === filters[2]
			}
		})
		
		//Recent Filter
		if (recent_filter === 'recent_built'){
			data1 = data1.filter( function(d){
				return d.recent_built === "1";
			})
		}else if(recent_filter === 'recent_alter'){
			data1 = data1.filter( function(d){
				return d.recent_alter === "1";
			});
		}else if(recent_filter === 'has_merged'){
			data1 = data1.filter( function(d){
				return d.has_merged === "1";
			});
		}else{
			data1 = data1;
		}

		data1 = arrayColumn(data1,column);
		return data1;
	}

</script>

<svelte:head>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;700&display=swap" rel="stylesheet"> 
</svelte:head>

<main>
	{#await loadData()}
		<p>Waiting</p>
	{:then data}

		<div class="explanation">
			<h2>TASC Threshold Selector</h2>
			<p class="intro">
				This tool help visualize the effect of CEQR screening parameters. By changing the parametesr below, you can visualize number of developed lots and whether these lots were considered soft sites.  
			</p>
		</div>
		<div class="block button-holder">
			<div class="slides">
				<BuiltFilter  on:recent={handle_recent} /> 
				<PumaFilter {data} on:puma={handle_puma}/>
				<Slider_LOT bind:lotslider_value minmax_lot={minmax_lot} />
				<Slider_FAR bind:farslider_value minmax_lot={minmax_far} />
			</div>
			<div class="notes">
				{#key filters}
					<Reports {data} filters = {filters}/>
				{/key}
			</div>
		</div>
 
		<div class="block lot-holder">
			<div class="what">Distribution of Developped Lots based on Lot Area</div>
			{#key filters.slice(2,4)}
				<Histogram_LOT data={filter_data(data,'LotArea_07')} vline={lotslider_value}/>
			{/key}
		</div>
		<div class="block far-holder"> 
			<div class="what">Distribution of Developped Lots based on Percentage of Available FAR</div>
			{#key filters.slice(2,4)}
				<Histogram_FAR data={filter_data(data,'availFAR_perc_07')} vline={farslider_value}/>
			{/key}
		</div>
		<div class="block rent-holder">
			<div class="what">How many lots have rent stabilized units?</div>
			{#key filters.slice(2,4)}
				<BarChart {data} {filters}/>
			{/key}
		</div>

	{/await}
</main>

<style>

	.what{
		margin-top:5px;
		margin-bottom:5px;
	}
	main {
		text-align: center;
		padding: 1em;
		max-width: 1000px;
		margin: 0 auto;
	}

	.intro{
		font-weight: 400;
	}

	.button-holder{
		padding:20px 20px;
		display: flex;
		flex-direction: row;
		background-color: rgba(0,0,0,0.05);
	}

	.notes{
		width: 35%;
		height: auto;
		padding: 10px;
		margin: auto 10px;
		display: flex;
		flex-direction: column;
		border-left: 1px solid #888;
	}

	.slides{
		width:65%;
		display: flex;
		flex-direction: column;
		justify-content: space-evenly;
		padding-right: 15px;
	}

	.block{
		min-height: 50px;
		margin-bottom: 15px;
		padding-top: 15px;
		padding-left: 15px;
		padding-right: 15px;
		padding-bottom: 15px;
	}

</style>