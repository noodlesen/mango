
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
    computed:{
        
    },
    methods:{
        choosePreSelected: function(){
            if (this.preSelected){
               //window.location = 'http://localhost:5000/place/singapore';

               //$(location).attr('href', 'http://www.sitefinity.com');

                //'http://localhost:5000'+this.results[this.preSelectedIndex].url;
                //window.location.assign("http://www.mozilla.org");//'http://localhost:5000'+this.results[this.preSelectedIndex].url;
                //console.log(this.results[this.preSelectedIndex].url);
                //$('#search-results').trigger('click', 'a #sl'+this.preSelectedIndex);
                $('#sl'+this.preSelectedIndex).click();
                alert();
                //$("#search-results").find("a:first").trigger("click");
            }
        },
        elPreSelected: function(i){
            return ((i==this.preSelectedIndex) && this.preSelected);
        },
        preSelect: function(i){
            if (this.preSelected){
                this.preSelectedIndex+=i;
            } else if (i==1){
                this.preSelectedIndex=0;
            } else if (i = -1){
                this.preSelectedIndex=this.results.length-1;
            }
            this.preSelected = true;
            console.log(this.preSelectedIndex);
        },
        checkNeedle: function(){
            //console.log(JSON.stringify(e));
            
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
