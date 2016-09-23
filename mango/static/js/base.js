
var ev = new Event('eNotificationsUpdated');

function refreshIndicators(){
    
    if (serverHasMessages){
        $('.serverMsgCount').html('<span class="glyphicon glyphicon-envelope"></span>'+serverHasMessages);
        $('.serverMsgIndicator').show();
    } else {
        $('.serverMsgIndicator').hide();
    }

    if (serverHasNotifications){
        $('.serverNotsCount').html('<span class="glyphicon glyphicon-bell"></span>'+serverHasNotifications);
        $('.serverNotsIndicator').show();
    }
    else {
        $('.serverNotsIndicator').hide();
    }
}

function checkNotifications(){
    getResults('/notifier', 'json', {cmd:'checkNotifications'}, function(res){
        if (res.status=='ok'){
            serverHasMessages = res.messages;
            serverHasNotifications = res.notifications;
            refreshIndicators();
            $('#messenger').trigger('eNotificationsUpdated');
            
        }
    });
}

$(document).ready(function(){
    
    refreshIndicators();
    setInterval(checkNotifications,20000);
});
