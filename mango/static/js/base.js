
var ev = new Event('eNotificationsUpdated');

var serverHasMessages = 0;
var serverHasNotifications = 0;

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
    console.log('checking');
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
    checkNotifications();
    setInterval(checkNotifications,20000);
});

var placeSearch = new Vue({
    el: '#navbar',
    data: {
        needle: '',
        showingResults: false,
        results:{}
    },
    methods:{
        checkNeedle: function(){
            var self=this;
            if (this.needle.length>=2){
                getResults('/json/place-search','json',{needle: this.needle}, function(res){
                    if (res.status=='ok'){
                        if (res.places.length){
                            self.results=res.places;
                            self.showingResults = true;
                        } else {
                            self.results = {};
                        }
                    }
                });
            } else {
                self.showingResults = false;
            }
        }
    }
});
