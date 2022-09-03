
<script>

    import { createEventDispatcher } from 'svelte';
    import { afterUpdate } from 'svelte';
    const dispatch = createEventDispatcher();

    function send_recent(e){
        dispatch('recent', {
			text: e.target.value
		});
    }

    afterUpdate(() => {
        let pops = document.querySelector("#form-prompt");
        pops.addEventListener('mouseenter',()=>{
            document.querySelector(".filter-ex").style.visibility = 'visible';
        });
        pops.addEventListener('mouseleave',()=>{
            document.querySelector(".filter-ex").style.visibility = 'hidden';
        });
    });

</script>

<form id="form" on:change={send_recent}>
    <div id=form-prompt>Filter by: </div>
    <div class="radio-button">
        <input type="radio" id="all" name="age" value="all" checked="checked">
        <label for="alter">All</label><br>
    </div>
    <div class="radio-button">
        <input type="radio" id="built" name="age" value="recent_built">
        <label for="built">Built Year</label><br>
    </div>
    <div class="radio-button">
        <input type="radio" id="alter" name="age" value="recent_alter">
        <label for="alter">Recent Alteration Year</label><br>
    </div>
    <div class="radio-button">
        <input type="radio" id="merge" name="age" value="has_merged">
        <label for="alter">Recent Merger</label><br>
    </div>
</form>

<div class="filter-ex">
    <p class="ex"><b>Built Year:</b><br> Lots with new buildings constructed from 2007 to 2017</p>
    <p class="ex"><b>Recent Alteration Year:</b><br> Lots with Alteration from 2007 to 2017 as recorded by MapPLUTO</p>
    <p class="ex"><b>Recent Merger:</b><br> Lots that were merged in to other lots or other lots were merged into</p>
</div>


<style>

    .filter-ex{
        position: absolute;
        background: rgba(255,255,255,0.95);
        max-width: 350px;
        visibility: hidden;
        z-index: 5;
        text-align: left;
        padding: 10px;
    }
    .filter-ex>.ex{
        font-size: 0.8rem;
        margin:0.1rem;
    }

    form{
        margin-bottom: 15px;
        display: flex;
        flex-direction: row;
    }

    input{
        display: inline;
        cursor: pointer;
        accent-color: rgb(187, 62, 3);
    }

    input:checked + label {
        color: rgb(187, 62, 3);
        font-weight: 500;
    }

    label{
        display: inline;
        font-size: 0.9rem;

    }
    .radio-button{
        text-align: left;
        padding-left: 8px;
        color:#555;
    }
    #form-prompt{
        text-align: left;
        margin: 0;
        font-weight: 500;
        margin-bottom: 5;
        min-width: 15%;
        cursor: pointer;
    }



</style>