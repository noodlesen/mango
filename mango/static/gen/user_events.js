var csrftoken=$('meta[name=csrf-token]').attr('content');$.ajaxSetup({beforeSend:function(xhr,settings){if(!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)&&!this.crossDomain){xhr.setRequestHeader("X-CSRFToken",csrftoken)}
console.log(csrftoken);}})
function getResults(route,resultType,formData,callback){$.ajax(route,{type:'post',data:JSON.stringify(formData,null,'\t'),dataType:resultType,contentType:'application/json;charset=UTF-8',success:function(result){callback(result);},error:function(result){console.log(result);location.reload();}});}
var ev=new Event('eNotificationsUpdated');var serverHasMessages=0;var serverHasNotifications=0;function refreshIndicators(){if(serverHasMessages){$('.serverMsgCount').html('<span class="glyphicon glyphicon-envelope"></span>'+serverHasMessages);$('.serverMsgIndicator').show();}else{$('.serverMsgIndicator').hide();}
if(serverHasNotifications){$('.serverNotsCount').html('<span class="glyphicon glyphicon-bell"></span>'+serverHasNotifications);$('.serverNotsIndicator').show();}
else{$('.serverNotsIndicator').hide();}}
function checkNotifications(){console.log('checking');getResults('/notifier','json',{cmd:'checkNotifications'},function(res){if(res.status=='ok'){serverHasMessages=res.messages;serverHasNotifications=res.notifications;refreshIndicators();$('#messenger').trigger('eNotificationsUpdated');}});}
$(document).ready(function(){checkNotifications();setInterval(checkNotifications,20000);});var placeSearch=new Vue({el:'.place-search__scope',data:{needle:'',previousNeedle:'',showingResults:false,results:{},preSelected:false,preSelectedIndex:-1},methods:{choosePreSelected:function(){if(this.preSelected){var hr=this.results[this.preSelectedIndex].url;setTimeout(function(){window.location.pathname=hr;},500);}},elPreSelected:function(i){return((i==this.preSelectedIndex)&&this.preSelected);},preSelect:function(i){if(this.preSelected){this.preSelectedIndex+=i;if(this.preSelectedIndex<0){this.preSelectedIndex=this.results.length-1;}
if(this.preSelectedIndex>=this.results.length){this.preSelectedIndex=0;}}else if(i==1){this.preSelectedIndex=0;}else if(i=-1){this.preSelectedIndex=this.results.length-1;}
this.preSelected=true;console.log(this.preSelectedIndex);},checkNeedle:function(e){var self=this;console.log(e);if(this.needle.length>=2){if(this.needle!=this.previousNeedle){this.previousNeedle=this.needle;getResults('/json/place-search','json',{needle:this.needle},function(res){if(res.status=='ok'){if(res.places.length){self.results=res.places;self.showingResults=true;}else{self.results={};}}});}}else{self.showingResults=false;}}}});$(document).ready(function(){getResults('/user/events','json',{cmd:'releaseNotifications'},function(res){if(res.status=='ok'){checkNotifications();}});});