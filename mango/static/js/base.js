
var ev = new Event('eNotificationsUpdated');

function refreshIndicators(){
    console.log('refreshing');
    
    if (serverHasMessages){
        console.log('showing');
        $('.serverMsgCount').html(serverHasMessages);
        $('.serverMsgIndicator').show();
    } else {
        console.log('hiding');
        $('.serverMsgIndicator').hide();
    }

    

    if (serverHasNotifications){
        $('.serverNotsCount').html(serverHasNotifications);
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
            //$('#messenger').dispatchEvent(ev);
            $('#messenger').trigger('eNotificationsUpdated');
            
        }
    });
}

$(document).ready(function(){
    
    refreshIndicators();
    setInterval(checkNotifications,20000);
});
