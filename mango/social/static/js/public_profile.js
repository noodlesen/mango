/*$(document).ready(function(){

    $('#private-message__show').on('click', function(){
        if(!$(this).hasClass('disabled')){
            $('#private-message__form').show(300);
        }
    });

    $('#private-message__send-button').on('click', function(){
        var txt = $('#private-message__textarea').val();
        //var id = $(this).attr('data-uid');
        if (userId && txt!=''){
            getResults('/post-messenger', 'json', {text: txt, cmd:'sendMessage', uid: userId}, function(res){
                $('#private-message__textarea').val('');
                if (res.status=='ok'){
                    $('#private-message__form').hide(300); 
                    $('#private-message__status').show(300);
                }
                

            });
        }
    });

    $('#subscribe__btn').on('click', function(){
        getResults('/user-subscribe', 'json', {uid: userId}, function(res){
            if (res.status=='ok'){
                alert('Вы подписаны');
            } else if (res.status=="Already subscribed"){
                alert('Уже подписаны');
            }
        });
    });
});*/

var pp = new Vue({
    el:'#userinfo',
    data:{
        userId: null,
        signedIn: false,
        subscribed: false,
        canSendPm: true,
        showingMessageForm:false,
        messageText:'',
        messageSuccess: false
    },
    methods: {
        subscribe: function(){
            var self = this;
            getResults('/user-subscribe', 'json', {cmd: 'subscribe', uid: userId}, function(res){
                if (res.status=='ok'){
                    self.subscribed = true;
                } 
            });
        },
        unsubscribe: function(){
            var self = this;
            getResults('/user-subscribe', 'json', {cmd: 'unsubscribe', uid: userId}, function(res){
                if (res.status=='ok'){
                    self.subscribed = false;
                }
            });
        },
        showMessageForm: function(){
            this.showingMessageForm = !this.showingMessageForm;
        },
        sendPrivateMessage: function(){
            var self = this;
            if (this.signedIn && this.messageText!=''){
                getResults('/post-messenger', 'json', {text: this.messageText, cmd:'sendMessage', uid: this.userId}, function(res){
                    if (res.status=='ok'){
                        self.messageText='';
                        self.showingMessageForm=false;
                        self.messageSuccess = true;
                    }
                });
            }
        }
    },
    ready: function(){
        this.subscribed = subscribed == "True" ? true : false;
        this.canSendPm = canSendPm == "True" ? true : false;
        this.signedIn = signedIn == "True" ? true : false;
        this.userId = userId;
    }
});