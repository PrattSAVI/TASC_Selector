<script>

    export let data;
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();

    function extractColumn(arr, column) {
        return arr.map(x => x[column])
    }

    let pumas = extractColumn( data , 'puma')
    let unique_pumas = [...new Set(pumas)].sort();
    unique_pumas.unshift( "All NYC" );

    //let puma_filter = 'All NYC';

    function send_puma(){
        let val = document.getElementById("Pumas")
        dispatch('puma', {
			text: val.value
		});
    }

</script>

<div class="dd">

    <form>
        <label for="Pumas">PUMA: </label>
        <select name="Pumas" id="Pumas" on:change={send_puma} >
            {#each unique_pumas as puma}
            <option value={puma}>{puma}</option>
            {/each}
        </select>
    </form>

</div>

<style>
    label{
        min-width: 15%;
        text-align: left;
        margin-right: 10px;
        font-weight: 500;
    }

    form{
        display: flex;
        flex-direction: row;
        margin-right: 25px;
    }
    select{
        width: 70%;
    }

    label{
        padding-top: 0.5rem;
    }

</style>