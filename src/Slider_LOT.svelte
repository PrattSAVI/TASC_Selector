

<script>

    export let lotslider_value = 50;
    export let minmax_lot;

</script>

<div class="slider-box">
    <div class="title">{minmax_lot[0]}</div>
    <div class="slidecontainer">
        <input type="range" min= {minmax_lot[1]} max={minmax_lot[2]} class="slider" id="myRange" bind:value={lotslider_value}>
    </div>
    <div class="result">{lotslider_value} Sq.Ft.</div>
</div>

<style>


    /* The slider itself */
    .slider {
        -webkit-appearance: none;  /* Override default CSS styles */
        appearance: none;
        width: 100%; /* Full-width */
        height: 10px; /* Specified height */
        background: #d3d3d3; /* Grey background */
        outline: none; /* Remove outline */
        opacity: 0.7; /* Set transparency (for mouse-over effects on hover) */
        -webkit-transition: .2s; /* 0.2 seconds transition on hover */
        transition: opacity .2s;
    }
    
    /* Mouse-over effects */
    .slider:hover {
        opacity: 1; /* Fully shown on mouse-over */
    }
    
    /* The slider handle (use -webkit- (Chrome, Opera, Safari, Edge) and -moz- (Firefox) to override default look) */
    .slider::-webkit-slider-thumb {
        -webkit-appearance: none; /* Override default look */
        appearance: none;
        width: 8px; /* Set a specific slider handle width */
        height: 25px; /* Slider handle height */
        background: #bb3e03; /* Green background */
        cursor: pointer; /* Cursor on hover */
    }
    
    .slider::-moz-range-thumb {
        width: 8px; /* Set a specific slider handle width */
        height: 25px; /* Slider handle height */
        background: #bb3e03; /* Green background */
        cursor: pointer; /* Cursor on hover */
    }

</style>