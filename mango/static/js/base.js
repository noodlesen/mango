
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
        results:{},
        preSelected: false,
        preSelectedIndex: -1
    },
    methods:{
        choosePreSelected: function(){
            if (this.preSelected){
               //location.assign(this.results[this.preSelectedIndex].url);
               var hr = this.results[this.preSelectedIndex].url;
               setTimeout(function(){window.location.pathname = hr;},100);
               

               //$(location).attr('href', 'http://www.sitefinity.com');

                //window.location.assign("http://www.mozilla.org");//'http://localhost:5000'+this.results[this.preSelectedIndex].url;
                //console.log(this.results[this.preSelectedIndex].url);
                //$('#search-results').trigger('click', 'a #sl'+this.preSelectedIndex);
                //$('#sl'+this.preSelectedIndex).trigger('click');
                //$("#search-results").find("a:first").trigger("click");
            }
        },
        elPreSelected: function(i){
            return ((i==this.preSelectedIndex) && this.preSelected);
        },
        preSelect: function(i){
            if (this.preSelected){
                this.preSelectedIndex+=i;
                if (this.preSelectedIndex<0) {
                    this.preSelectedIndex = this.results.length-1;
                }
                if (this.preSelectedIndex>=this.results.length) {
                    this.preSelectedIndex = 0;
                }

            } else if (i==1){
                this.preSelectedIndex=0;
            } else if (i = -1){
                this.preSelectedIndex=this.results.length-1;
            }
            this.preSelected = true;
            console.log(this.preSelectedIndex);
        },
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
