$(document).ready(function(){
    getResults('/user/events', 'json', {cmd:'releaseNotifications'}, function(res){
        if (res.status=='ok'){
            checkNotifications();
        }
    });
});