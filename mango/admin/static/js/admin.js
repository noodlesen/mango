$(document).ready(function(){

        $('#workers-list').tablesorter();

    $('input, textarea').on('change',function(){
        $(this).addClass('changed-field')
    });

});