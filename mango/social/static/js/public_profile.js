

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
            console.log('sending');
            var self = this;
            if (this.signedIn && this.messageText!=''){
                console.log('to server');
                getResults('/post-messenger', 'json', {text: this.messageText, cmd:'sendMessage', uid: this.userId}, function(res){
                    if (res.status=='ok'){
                        console.log('ok');
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
        this.signedIn = signedIn;// == "True" ? true : false;
        this.userId = userId;
    }
});