var st = new Vue({
    el:'#single-tip',
    data: {
        upvoted:false,
        downvoted: false,
        upCount:0,
        downCount:0,
        id: null
    },
    ready: function(){
        this.id = tipId;
        this.upvoted = state.upvoted;
        this.downvoted = state.downvoted;
        console.log('U: '+this.upvoted);
            console.log('D: '+this.downvoted);
    },
    methods: {
        upvote: function(){
            if (signedIn){
                var selected;
                if (!this.upvoted && !this.downvoted){
                    selected="none";
                } else if (this.upvoted){
                    selected ="upVote"
                } else if (this.downvoted){
                    selected = "downVote"
                }
                var self = this;
                getResults('/json/tip', 'json', {cmd: 'clickUpVote', selected: selected, id: this.id}, function(res){
                    if (res.status=='ok'){
                        console.log('S: '+selected);
                        switch (selected){
                            case "none":
                                self.upvoted = true;
                                break;
                            case "upVote":
                                self.upvoted=false;
                                break;
                            case "downVote":
                                self.downvoted=false;
                                self.upvoted=true;
                                break;
                        }
                        self.upCount = res.upvoted;
                        self.downCount = res.downvoted;
                        console.log('U: '+self.upvoted);
                        console.log('D: '+self.downvoted);
                        //self.$dispatch('eCheckTipsOrder', {id: self.id, upvoted: self.upvoted, downvoted: self.downvoted});
                    }
                });
            } else {
                $('#si-modal').modal('show');
            }
            
        },
        downvote: function(){
            if (signedIn){
                var selected;
                if (!this.upvoted && !this.downvoted){
                    selected="none";
                } else if (this.upvoted){
                    selected ="upVote"
                } else if (this.downvoted){
                    selected = "downVote"
                }
                var self = this;
                getResults('/json/tip', 'json', {cmd: 'clickDownVote', selected: selected, id: this.id}, function(res){
                    if (res.status=='ok'){
                        console.log('S: '+selected);
                        switch (selected){
                            case "none":
                                self.downvoted = true;
                                break;
                            case "downVote":
                                self.downvoted=false;
                                break;
                            case "upVote":
                                self.upvoted=false;
                                self.downvoted=true;
                                break;
                        }
                        self.upCount = res.upvoted;
                        self.downCount = res.downvoted;
                        console.log('U: '+self.upvoted);
                        console.log('D: '+self.downvoted);
                        //self.$dispatch('eCheckTipsOrder', {id: self.id, upvoted: self.upvoted, downvoted: self.downvoted});
                    }
                });
            } else {
                $('#si-modal').modal('show');
            }


        },
        addComment: function(){

        }
    }
});