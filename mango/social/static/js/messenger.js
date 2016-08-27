

var messenger = new Vue({
    el:'#messenger',

    data:{
        selectedUser: {},
        selectedUserIndex: -1,
        currentUser: -1,
        contactList:[],
        sendButtonDisabled: true,
        headerText:'',
        userIsBanned:false,
        messages:[],
        messageArea:'',
        showAllMessages:false,
        onlyLastMessages:false
    },

    computed:{

        banButtonTitle: function(){
            return this.userIsBanned ? 'Разрешить этому пользователю отправлять вам сообщения' : 'Заблокировать пользователя';
        }
    },

    methods: {

        getUserData: function (user_id, callback){
            var self = this;
            getResults('/post-messenger', 'json', {cmd:'loadUserData', uid: user_id}, function(res){
                if (res.messages.length>10 && !self.showAllMessages){
                    self.messages=res.messages.splice(res.messages.length-10, 10);
                    self.onlyLastMessages = true;
                } else {
                    self.messages=res.messages;
                    self.onlyLastMessages = false;
                }
                 console.log(JSON.stringify(self.messages));
                self.userIsBanned=res.isBanned;
                callback();
            });
        },

        sendMessage: function (){
            var self = this;
            getResults('/post-messenger', 'json', {text: this.messageArea, cmd:'sendMessage', uid: this.selectedUser.uid}, function(res){
                if (res.status=='ok'){
                    self.getUserData(self.selectedUser.uid, function(){
                        self.messageArea='';
                    });
                }
                else if(res.status=='disabled'){
                    alert('Вы не можете отправлять сообщения этому пользователю');
                }
                
            });
        },

        releaseNotifications: function(){
            var self = this;
            getResults('post-messenger', 'json', {
                cmd:'releaseNotifications',
                user_from: this.selectedUser.uid,
                }, function(res){
                    if (res.status='ok'){
                        self.contactList[self.selectedUserIndex].unread = 0;
                        serverHasMessages=res.unread;
                        refreshIndicators();
                    }
                });
        },

        selectContact: function(i){
            var self = this;
            console.log(JSON.stringify(this.contactList[i]));
            this.selectedUser = this.contactList[i];
            this.selectedUserIndex = i;
            this.sendButtonDisabled = false; // move it later
            this.headerText = 'Ваш чат с пользователем '+this.selectedUser.name;
            this.showAllMessages=false;
            this.getUserData(this.selectedUser.uid, function(){
                self.releaseNotifications();
            });
        },

        loadContactList: function(){
            var self = this;
            getResults('/post-messenger', 'json', {cmd:'getContacts'}, function(res){
                if (res.status=='ok'){
                    self.contactList = res.list;
                    var selUID = $('meta[name=seluid]').attr('content');
                    if (selUID){
                        selUID = parseInt(selUID, 10);
                        for (var i=0; i<self.contactList.length; i++){
                            if (self.contactList[i].uid == selUID){
                                self.selectContact(i);
                                break;
                            }
                        }
                    }
                }
                else {

                }
                
            });
        },

        toggleBanUser:function(){
            var self = this;
            this.userIsBanned = !this.userIsBanned;
            getResults('/post-messenger', 'json', {cmd:'toggleBanUser', uid:this.selectedUser.uid}, function(res){
                if (res.status=='ok'){

                }
            });
        },

        openAllMessages:function(){
            this.messages=[];
            this.showAllMessages=true;
            this.onlyLastMessages = false;
            this.getUserData(this.selectedUser.uid, function(){
            });
        }

    },


    ready:function(){
        this.currentUser = parseInt($('meta[name=uid]').attr('content'), 10);
        setTimeout(function(){location.reload();},1000*60*10);
        this.loadContactList();
        $('#messenger').on('eNotificationsUpdated', this.loadContactList);
    }

});
