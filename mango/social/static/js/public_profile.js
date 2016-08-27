$(document).ready(function(){

    $('#private-message__show').on('click', function(){
        if(!$(this).hasClass('disabled')){
            $('#private-message__form').show(300);
        }
    });

    $('#private-message__send-button').on('click', function(){
        var txt = $('#private-message__textarea').val();
        var id = $(this).attr('data-uid');
        if (id && txt!=''){
            getResults('/post-messenger', 'json', {text: txt, cmd:'sendMessage', uid: id}, function(res){
                $('#private-message__textarea').val('');
                if (res.status=='ok'){
                    $('#private-message__form').hide(300); 
                    $('#private-message__status').show(300);
                }
                

            });
        }
    });
});