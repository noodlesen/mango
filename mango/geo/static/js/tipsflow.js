
moment.locale('ru');

//var relatedUsers =[];

$(document).ready(function(){
});


function checkHttp(s){
    if (s && s!=''){
        if (!(s.startsWith('http:') || s.startsWith('https:'))){
            return 'http://'+s;
        } else {
            return s;
        }
    } else {
        return '';
    }
}



// TIP COMPONENT 
// ==================================================================================

var cTip = Vue.extend({

    props: ['text','tags', 'author', 'id', 'fave', 'upvote', 'downvote','upvoted', 'downvoted', 'comments', 'url', 'edit', 'related','mode', 'featured', 'place','country', 'countryurl', 'directionurl', 'attachedurl'],

    data: function(){
        return { 
            upVote: false,
            downVote:false,
            outdated: false,
            favorite: false,
            showingComments: false,
            showingShare: false,
            commentText:'',
            commentFormEditMode: false,
            commentToSave: null,
            signedIn: false,
            pendingDelete: false,
            pendingCommentDelete: false,
            allowCmdBar:true
        }
    },
    ready:function(){
        console.log(this.countryurl)
        this.signedIn = signedIn;
        this.favorite = this.fave;
        if (this.upvote){
            this.upVote=true;
        } else if (this.downvote){
            this.downVote = true;
        }
        if (this.featured){
            this.showingShare = true;
            this.showingComments = true;
            this.allowCmdBar = true;
        }
    },
    computed: {
        hasComments : function(){
            return this.comments ? this.comments.length>0 : false;
        }
    },
    methods:{
        shareVk: function(){
            Share.vkontakte(this.url, 'Кудабы.Ру: Совет от пользователя '+this.author.name, this.text);
        },

        shareFacebook: function(){
            Share.facebook(this.url, this.text);
        },

        shareTwitter: function(){
            Share.twitter(this.url, this.text);
        },
        clickUpVote: function(){
            if (signedIn){
                var selected;
                if (!this.upVote && !this.downVote){
                
                    selected="none";
                } else if (this.upVote){
                 
                    selected ="upVote"
                } else if (this.downVote){

                    selected = "downVote"
                }
                var self = this;
                switch (selected){
                    case "none":
                        self.upVote = true;
                        break;
                    case "upVote":
                        self.upVote=false;
                        break;
                    case "downVote":
                        self.downVote=false;
                        self.upVote=true;
                        break;
                }
                getResults('/json/tip', 'json', {cmd: 'clickUpVote', selected: selected, id: this.id}, function(res){
                    if (res.status=='ok'){
             
                        self.upvoted = res.upvoted;
                        self.downvoted = res.downvoted;
                        self.$dispatch('eCheckTipsOrder', {id: self.id, upvoted: self.upvoted, downvoted: self.downvoted});
                    }
                });
            } else {
                $('#si-modal').modal('show');
            }

        },        

        clickDownVote: function(){
            if (signedIn){
                var selected;
                if (!this.upVote && !this.downVote){
                    selected="none";
                } else if (this.upVote){
                    selected ="upVote"
                } else if (this.downVote){
                    selected = "downVote"
                }
                var self = this;
                getResults('/json/tip', 'json', {cmd: 'clickDownVote', selected: selected, id: this.id}, function(res){
                    if (res.status=='ok'){
                        switch (selected){
                            case "none":
                                //self.downVoted++;
                                self.downVote = true;
                                break;
                            case "downVote":
                                //self.downVoted--;
                                self.downVote=false;
                                break;
                            case "upVote":
                                //self.upVoted--;
                                self.upVote=false;
                                //self.downVoted++;
                                self.downVote=true;
                                break;
                        }
                        self.upvoted = res.upvoted;
                        self.downvoted = res.downvoted;
                        self.$dispatch('eCheckTipsOrder', {id: self.id, upvoted: self.upvoted, downvoted: self.downvoted});
                    }
                });
            } else {
                $('#si-modal').modal('show');
            }

        },

        toggleFavorite: function(){
            if (signedIn){
                var self = this;
                getResults('/json/tip', 'json', {cmd: 'setFavorite', value: !this.favorite, id: this.id}, function(res){
                    if (res.status=='ok'){
                        self.favorite = !self.favorite;
                    }
                });
            } else {
                $('#si-modal').modal('show');
            }
            
        },

        clickEdit: function(){
            this.$dispatch('eEditTip', {id: this.id});
        },

        askDelete: function(){
            this.pendingDelete = true;
        },

        cancelDelete: function(){
            this.pendingDelete = false;
        },

        confirmDelete: function(){
            var self=this;
            getResults('/json/tip','json',{cmd:'delete', id: this.id}, function(res){
                console.log(res.status);
                if (res.status=='ok'){
                    self.pendingDelete = false;
                    self.$dispatch('eTipRemoved', {id: self.id})
                }
            });
        },

        filterByTag: function(name){
            this.$dispatch('eFilterOnly', {name: name});
            console.log(name);
        },

        toggleShowComments: function(){
            this.showingComments=!this.showingComments;
        },

        toggleShowShare: function(){
            this.showingShare=!this.showingShare;
        },

        addComment: function(){
            var self = this;
            if (this.commentText.trim()!=''){
                getResults('/json/tip', 'json', {cmd: 'addComment', text: this.commentText, id: this.id}, function(res){
                    if (res.status=='ok'){
                        self.commentText = '';
                        self.comments = res.comments;
                    }
                });
            }
        },

        editComment: function(i){
            this.commentFormEditMode = true;
            this.commentText = this.comments[i].text;
            this.commentToSave = i;
        },

        saveComment: function(i){
            var self = this;
            if (this.commentText.trim()!=''){
                getResults('/json/tip', 'json', {cmd: 'saveComment', text: this.commentText, id: this.id, cid: this.commentToSave}, function(res){
                    if (res.status=='ok'){
                        self.commentText = '';
                        self.comments = res.comments;
                        self.commentFormEditMode=false;
                    }
                });
            }
        },

        confirmCommentDelete: function(){
            var self = this;
            getResults('/json/tip', 'json', {cmd: 'deleteComment', id: this.id, cid: this.commentToSave}, function(res){
                if (res.status=='ok'){
                    self.commentText = '';
                    self.comments = res.comments;
                    self.commentFormEditMode=false;
                    self.pendingCommentDelete=false;
                }
            });
        },

        getDate: function(timestamp){
            return moment.utc(timestamp, 'YY MM DD hh mm ss').fromNow();
        },

        getUser: function(uid){
            console.log('get user: '+uid);
            console.log(JSON.stringify(this.related));
            return this.related.find(function(u){ return u.id==uid}).nickname;
        },

        getPublicProfile: function(uid){
            return this.related.find(function(u){ return u.id==uid}).public_profile;
        }
    },


    template: '<div>\
                <div class="tip__extra-top" v-if="mode==\'favorites\' || mode==\'my_tips\'|| mode==\'public_profile\'"><a href="{{url}}">{{place}}</a> - <a href="{{countryurl}}">{{country}}</a></div>\
                <div class="item-block tip has-cmd-bar" :class="{\'featured\':featured}" >\
                    <div class="tip-block__body" :class="{\'tip-upVoted\':upVote, \'tip-downVoted\':downVote}" >\
                            <div class="tip__top">\
                              <div class="tip__tags">\
                                    <span v-for="t in tags" class="tip__tag" :class="\'back-\'+t.style" @click="filterByTag(t.name)">{{t.name}}</span>\
                                </div>\
                                <div class="tip__favorite" @click="toggleFavorite">\
                                    <i v-if="!favorite" class="glyphicon glyphicon-bookmark color-pale-blue" title="Добавить в избранное"></i>\
                                    <i v-if="favorite" class="glyphicon glyphicon-bookmark color-blue" title="Уже у вас в избранном"></i>\
                                </div>\
                                <div class="clearfix"></div>\
                            </div>\
                        <div class="tip__main-text">\
                            <slot></slot><p>{{text}}</p> <span class="plink comment-link" v-if="hasComments" @click="toggleShowComments"> <i class="fa fa-comment"></i>{{comments ? comments.length : 0}}</span>\
                            <p v-if="attachedurl"><br/><a :href="attachedurl" target="_blank"><span class="glyphicon glyphicon-link"></span>&nbsp;{{attachedurl}}</a></p>\
                        </div>\
                        <div class="tip__bottom">\
                        </div>\
                    </div>\
                    <div class="tip-block__sidebar">\
                        <div class="tip__vote-up" @click="clickUpVote" :class="{\'tip__vote-up--active\':upVote}">\
                            <div class="glyphicon glyphicon-triangle-top tip__vote-icon" ></div>\
                            <div class="tip__vote-number">{{upvoted}}</div>\
                        </div>\
                        <div class="tip__vote-dn"  @click="clickDownVote" :class="{\'tip__vote-dn--active\':downVote}">\
                            <div class="tip__vote-number">{{downvoted}}</div>\
                            <div class="glyphicon glyphicon-triangle-bottom tip__vote-icon" ></div>\
                        </div>\
                    </div><div class="clearfix"></div>\
                    <div class="tip__share" v-if="showingShare">\
                                <div class="tip__share-block" @click="shareFacebook"><i class="fa fa-facebook"></i></div>\
                                <div class="tip__share-block" @click="shareVk"><i class="fa fa-vk"></i></div>\
                                <div class="tip__share-block" @click="shareTwitter"><i class="fa fa-twitter"></i></div>\
                                <div class="tip__share-link"><a href="{{url}}">Ссылка:</a> <input type="text" size="40" v-model="url"></div>\
                    </div>\
                    <div class="cmd-bar" v-if="allowCmdBar">\
                        <div class="cmd-bar__left">\
                        <div class="cmd-bar__button" @click="toggleShowShare">\
                                <i class="fa fa-share-alt-square"></i> Поделиться\
                        </div>\
                        <div class="cmd-bar__button" @click="toggleShowComments">\
                                <i class="fa fa-comment-o"></i> Комментарии: {{comments ? comments.length : 0}}\
                        </div>\
                        </div>\
                        <div class="cmd-bar__right">\
                        <div class="cmd-bar__button tip__author" v-if="!edit">\
                                <a href="/user/{{author.id}}" ><span class="glyphicon glyphicon-user"></span> {{author.name}}</a>\
                        </div>\
                        <div class="cmd-bar__button tip__edit-btn" v-if="edit" @click="clickEdit">\
                                Редактировать\
                        </div>\
                        <div class="cmd-bar__button tip__delete-btn" v-if="edit" @click="askDelete">\
                            <span class="glyphicon glyphicon-trash"></span>\
                        </div>\
                        </div>\
                        <div class="clearfix"></div>\
                    </div>\
                    <div class="confirm-delete" v-if="pendingDelete">Вы уверены, что хотите это удалить? \
                        <span class="cmd-bar__button" @click="confirmDelete">Да, удаляем! </span>\
                        <span class="cmd-bar__button" @click="cancelDelete"> Нет, нет, нет!</span>\
                    </div>\
                </div>\
                <div v-if="showingComments" class="comments">\
                    <div class="comment" v-for="c in comments" track-by="$index">\
                        <div class="comment__text">{{c.text}}</div>\
                        <div class="comment__meta">\
                        <span @click="editComment($index)" v-if="c.is_mine" class="plink"><span class="glyphicon glyphicon-edit"></span></span>\
                        <a href="{{getPublicProfile(c.author_id)}}">{{getUser(c.author_id)}}</a> {{getDate(c.timestamp)}}\
                        </div>\
                    </div>\
                    <div class="commentForm" v-if="signedIn">\
                        <textarea v-model="commentText" class="commentForm__ta" rows="3" placeholder="Добавьте свой комментарий"></textarea>\
                    <button v-if="!commentFormEditMode" @click="addComment" class="btn btn-large btn-default comment__button">Добавить комментарий</button>\
                    <button v-if="commentFormEditMode" @click="saveComment" class="btn btn-large back-color-green comment__button">Сохранить комментарий</button>\
                    <span v-if="commentFormEditMode" @click="pendingCommentDelete=true" class="btn btn-large color-red comment__button">\
                        <span class="glyphicon glyphicon-trash"></span>\
                        Удалить комментарий</span>\
                    </div>\
                    <div class="confirm-delete" v-if="pendingCommentDelete" >\
                        Вы уверены, что хотите удалить этот комментарий? \
                        <span class="cmd-bar__button" @click="confirmCommentDelete">Да, удаляем! </span>\
                        <span class="cmd-bar__button" @click="pendingCommentDelete=false"> Нет, нет, нет!</span>\
                    </div>\
                    <div class="divider"></div>\
                </div>\
                </div>'
}); 

Vue.component('c-tip', cTip);






// FILTER TAG COMPONENT 
// ==================================================================================

var tag = Vue.extend({
    data: function(){
        return {
        }
    },
    methods:{
        toggle: function(){
            this.active = !this.active;
            this.$dispatch('eFilterChanged', {name: this.name, value: this.active});
        }
    },
    computed:{
        act_color: function(){
            if (this.active){
                return ('back-'+this.color);
            } else {
                return (this.color);
            }
        },
        tag_class: function(){
            if (this.active){
                return ('back-'+this.color);
            } else {
                return ('filter-item-inactive');
            }
        }
    },
    props:['name', 'color', 'active'],
    events: {
        'eSwitchFilterOn' : function(e){
            if (e.name==this.name){
                this.active = true;
            } else {
                this.active = false;
            }
        },
        'eResetAllFilters' : function(){
            this.active = false;
        }
    },
    template:'<div class="filter-item" :class="[tag_class]" @click="toggle">\
                        <span class="glyphicon glyphicon-tag" :class="[act_color]" style="font-size:75%" ></span>\
                        <span :style="{fontSize: (name.length>15 ? 70 : 100) +\'%\'}" >{{name}}</span>\
            </div>'
});

Vue.component('tag', tag);









// ================================================================================
//                                                                               //
//                      TIPSFLOW VUE INSTANCE                                     //
//                                                                               //
// ================================================================================

var tipsFlow = new Vue({
    
    el: '#tipsflow',

    data: {
        tagsFilter:{
            placeTags:[],
            selectedTags:{},
            message:''
        },

        newTipForm:{
            allTags:[],
            acTags:[],
            popularTags:[],
            tagsText:'',
            addedTags:[],
            moreTags:[],
            tipText:'',
            error: false,
            errorMessage:'',
            attachedUrl: ''
        },

        allTips:[],
        shownTips:[],

        // CONFIG / STATE
        showAll: true,
        siModalShowing:true,
        signedIn:false,
        mode:'',
        showingTipForm: false,
        showingMoreTags: false,
        allowAddTip: true,
        allowFilters: true,
        allowEdit: false,
        lastEdited: null,
        collapsed: false,
        collapsedMessage: '',
        allowTipFilters: true,
        relatedUsers:[],
        featured: null
    },

    computed:{
        searchActive: function(){
            return this.newTipForm.tagsText!='';
        },

        limitError: function(){
            return this.newTipForm.tipText.length>600;
        },

        hasTips: function(){
            return this.allTips.length>0;
        }
    },


    // READY
    //............................
    ready: function(){
        
        var self = this;
        var jd = JSON.parse(jsonData);

        self.mode = jd.config.mode;

/*        this.featured = featured;
        this.hasFeatured = featured >= 0 ? true : false;*/

        if (self.mode=='place'){
            this.allowFilters=true;
            this.allowAddTip = true;
            this.allowTipFilters = true;

        } else if (self.mode=='single'){
            this.allowFilters=false;
            this.allowAddTip = false;
            this.allowTipFilters = false;
        
        } else if (self.mode=='my_tips'){
            this.allowFilters=false;
            this.allowAddTip = false;
            this.allowEdit = true;

        } else if (self.mode=='public_profile'){
            this.allowFilters=false;
            this.allowAddTip = false;
            this.allowEdit = false;
            this.collapsed = false;
            //this.collapsedMessage =jd.config.collapsed_message;

        } else if (self.mode=='favorites'){
            this.allowFilters=false;
            this.allowAddTip = false;
            this.allowPlacesList = true;
        }


        this.relatedUsers=jd.related_users;
        self.allTips=jd.tips;
        self.shownTips=jd.tips;
        self.sortTips();

        self.featured = jd.featured;

        self.tagsFilter.placeTags=jd.place_tags;
        self.newTipForm.allTags=jd.all_tags ? jd.all_tags : [];


        console.log(JSON.stringify(this.relatedUsers));

        self.newTipForm.popularTags = self.newTipForm.allTags.slice(0, 12);
        self.newTipForm.moreTags = self.newTipForm.allTags.slice(12, 64);
        self.tagsFilter.placeTags.forEach(function(t){
            self.tagsFilter.selectedTags[t.name]=false;
        });
        

        this.signedIn = signedIn;
    },

    // METHODS
    //............................
    methods: {

        uncollapse: function(){
            this.collapsed = false;
        },

        sortTips: function(){
           this.shownTips.sort(function(a,b){
                var rating = function(t){ return t.upvoted - t.downvoted }
                return rating(b) - rating(a);
            }); 
        },

        submitTipForm: function(edit){
            // Submits form data to server when you add or edit a tip 

            var self=this;

            // validate form data
            if (self.newTipForm.addedTags.length==0){
                self.newTipForm.error=true;
                self.newTipForm.errorMessage='Добавьте хотя бы одну метку';
            } else if (self.newTipForm.addedTags.length>5){
                self.newTipForm.error=true;
                self.newTipForm.errorMessage='Можно добавить не более пяти меток';
            } else if (self.limitError){
                self.newTipForm.error=true;
                self.newTipForm.errorMessage='Совет должен быть не более 600 символов';

            } else if (self.newTipForm.tipText.trim().length==0){
                self.newTipForm.error=true;
                self.newTipForm.errorMessage='Похоже, вы забыли написать сам совет ;)';

            } else {
                self.newTipForm.error=false;
            }

            console.log(JSON.stringify(self.newTipForm.addedTags));
            console.log(self.newTipForm.error);
            console.log(self.newTipForm.errorMessage);

            // if valid — send to server
            if (!self.newTipForm.error){
                getResults('/json/tip', 
                            'json', 
                            {
                                cmd: edit ? 'edit' : 'addNew', 
                                tags: this.newTipForm.addedTags, 
                                text:this.newTipForm.tipText, 
                                attached_url:this.newTipForm.attachedUrl, 
                                placeID: edit ? null : place_id,
                                tipID: this.lastEdited
                            },
                            function(res){
                                if (res.status=='ok'){
                                    self.showingTipForm = false;
                                    self.newTipForm.addedTags.forEach(function(t){
                                        if (self.tagsFilter.placeTags.find(function(pt){return pt.name == t.name }) == undefined){
                                            self.tagsFilter.placeTags.push(t);
                                        }
                                    });

                                    if (!edit){
                                        newTip = {
                                            favorite: false,
                                            like: false,
                                            dislike: false,
                                            upvoted:0,
                                            downvoted:0,
                                            text: self.newTipForm.tipText,
                                            tags: self.newTipForm.addedTags,
                                            author: {id: res.tip_data.author_id, name: res.tip_data.author_name},
                                            id: res.tip_data.tip_id,
                                            attached_url: checkHttp(self.newTipForm.attachedUrl),
                                            url: res.tip_data.url
                                        };
                                        console.log('before');
                                        console.log(JSON.stringify(self.allTips));
                                        console.log(JSON.stringify(self.shownTips));
                                        //self.allTips.push(newTip);
                                        self.shownTips.push(newTip);
                                        console.log('pushed 1');
                                        console.log(JSON.stringify(self.allTips));
                                        console.log(JSON.stringify(self.shownTips));
                                    } else {
                                        self.shownTips.every(function(el, i){
                                            if (el.id == self.lastEdited){
                                                el.text = self.newTipForm.tipText;
                                                el.tags = self.newTipForm.addedTags;
                                                el.attached_url = checkHttp(self.newTipForm.attachedUrl);
                                            }
                                        });
                                    }
                                    self.resetNewTipForm();

                                } else {
                                    alert('error');
                                }
                            });
            }
        },

        closeTipForm: function(){
            this.showingTipForm = false;
            this.resetNewTipForm();
        },

        resetNewTipForm: function(){
            var popularTagsTemp = this.newTipForm.popularTags;
  /*          this.newTipForm = {
                allTags:[],
                acTags:[],
                tagsText:'',
                addedTags:[],
                moreTags:[],
                tipText:''
            }*/
            this.newTipForm.tipText='';
            this.newTipForm.addedTags=[];
            this.newTipForm.attachedUrl='';
            //this.newTipForm.moreTags=[];
            this.showingMoreTags = false;

            this.newTipForm.popularTags = popularTagsTemp;
        },


        // ADD NEW TIP / TAGS METHODS
        //............................
        showMoreTags: function(){
            this.showingMoreTags = !this.showingMoreTags;
        },

        createTag: function(){
            var name = this.newTipForm.tagsText;
            if(this.newTipForm.addedTags.filter(function(t){return t.name==name}).length==0){
                var newTag = {name: name, style:'color-none', count:0};
                this.newTipForm.addedTags.push(newTag); 
                //this.newTipForm.createdTags.push(newTag); 
                this.newTipForm.allTags.push(newTag); 
                this.newTipForm.tagsText = '';
            }
        },

        addTag: function(src, i){
            console.log('addtag');
            var self = this;
            var target;
            if (src=='ac'){
                console.log('ac');
                target = this.newTipForm.acTags;
            } else if (src=='popular'){
                target = this.newTipForm.popularTags;
            } else if (src=='more'){
                target = this.newTipForm.moreTags;
                console.log('more');
            }

            if(this.newTipForm.addedTags.filter(function(t){return t.name==target[i].name}).length==0){
                   this.newTipForm.addedTags.push(target[i]); 
                   console.log(JSON.stringify(this.newTipForm.addedTags));
            }
        },

        removeAddedTag: function(i){
            console.log(i);
            this.newTipForm.addedTags.splice(i,1);
        },

        tagsTextChanged:function(){
                
                var self = this;
                var textTags = this.newTipForm.tagsText.split(',');
                var needle = textTags[textTags.length-1].trim();
                this.newTipForm.acTags = this.newTipForm.allTags.filter(function(t){
                    return (t.name.lastIndexOf(needle, 0 ) == 0 &&  needle.trim()!='');
                });
                console.log(JSON.stringify(this.newTipForm.acTags));
        },

        linkTextChanged: function(){

        },


        showTipForm: function(){
            if (signedIn){
                this.showingTipForm = true;
            } else {
                $('#si-modal').modal('show');
            }
        },

        // FILTER METHODS
        //............................
        resetFilters : function(){
            this.tagsFilter.selectedTags = {};
            this.showAll = true;
            this.shownTips = this.allTips;
            this.$broadcast('eResetAllFilters');
        },
        
        filterTips: function(){
            var self = this;
            self.tagsFilter.message = "";
            Object.keys(this.tagsFilter.selectedTags).forEach(function(t){
                if (self.tagsFilter.selectedTags[t]){
                    var style='';
                    self.tagsFilter.placeTags.forEach(function(f){
                        if (f.name==t){
                            style=f.style;
                        }
                    });
                    if (style != ''){
                        style='back-'+style;
                    }
                    self.tagsFilter.message += '<span class="tip__tag '+style+'">'+t+"</span>";
                }
                
            });

            this.shownTips=[];
                this.allTips.forEach(function(tip){
                    tip.tags.forEach(function(tag){
                        if (self.tagsFilter.selectedTags[tag.name]){
                            self.shownTips.push(tip);
                            console.log('pushed 2');
                        }
                    });
                });
        }

    },

    // EVENTS
    //............................
    events: {
        'eFilterChanged': function(e){
            var self = this;
            this.tagsFilter.selectedTags[e.name] = e.value;

            var hasSelected = false;

            Object.keys(this.tagsFilter.selectedTags).forEach(function(t){
                if (self.tagsFilter.selectedTags[t]){
                    hasSelected = true;
                }
            });

            this.showAll = hasSelected ? false : true;

            if (!this.showAll){
                this.filterTips();

            } else {
                this.shownTips = this.allTips;
            }
            console.log (JSON.stringify(this.tips));
        },

        'eFilterOnly': function(e){
            console.log(this.allowTipFilters);
            if (this.allowTipFilters){
                var self = this;
                this.showAll = false;
                Object.keys(this.tagsFilter.selectedTags).forEach(function(t){
                    self.tagsFilter.selectedTags[t]=false;
                });
                this.tagsFilter.selectedTags[e.name]=true;
                this.filterTips();
                this.$broadcast('eSwitchFilterOn',{name: e.name});
            }
        },

        'eCheckTipsOrder': function(e){
            this.shownTips.every(function(el, i){
                if (el.id == e.id) {
                    el.upvoted = e.upvoted;
                    el.downvoted = e.downvoted;
                    return false;
                }
                else return true;
            });
            this.allTips.every(function(el, i){
                if (el.id == e.id) {
                    el.upvoted = e.upvoted;
                    el.downvoted = e.downvoted;
                    return false;
                }
                else return true;
            });
            console.log(JSON.stringify(this.shownTips));
            //this.sortTips();
        },

        'eEditTip': function(e){
            var self=this;
            this.showTipForm();
            this.allTips.every(function(el,i){
                if (el.id == e.id){
                    self.newTipForm.tipText=el.text;
                    self.newTipForm.addedTags=el.tags;
                    self.newTipForm.attachedUrl=el.attached_url;
                    self.lastEdited = e.id;
                    return false;
                } else return true;
            });
        },

        'eTipRemoved': function(e){
            var self = this;
            this.allTips = this.allTips.filter(function(n){return n.id!=e.id});
            this.shownTips = this.shownTips.filter(function(n){return n.id!=e.id});
        }
    },

    template: '<div>\
                <button style="width:100%; font-size:120%;" class="btn btn-large btn-default" @click="uncollapse" v-text="collapsedMessage" v-if="collapsed">\
                </button>\
                <div id="filters" class="hidden-xs tips-sidebar" v-if="allowFilters&&!collapsed">\
                    <div class="tags__list">\
                        <div class="fheader">Метки</div>\
                        <div id="tag-list"><tag v-for="t in tagsFilter.placeTags" :name="t.name" :color="t.style" :active="false"></tag></div>\
                    </div>\
                </div>\
                \
                <!-- ==== TIPS COLUMN ==== -->\
                \
                <div id="tips" :class="{\'tips-1sb\': allowFilters}" v-if="!collapsed">\
                    <div id="featured-box" v-if="featured">\
                        <div class="clearfix"></div>\
                        <c-tip\
                            :tags="featured.tags" \
                            :author="featured.author"\
                            :id="featured.id" \
                            :fave="featured.favorite" \
                            :upvote="featured.like" \
                            :downvote="featured.dislike" \
                            :upvoted="featured.upvoted" \
                            :downvoted="featured.downvoted" \
                            :url="featured.url" \
                            :edit="allowEdit"\
                            :related="relatedUsers"\
                            :mode="mode"\
                            :text="featured.text"\
                            :featured="true"\
                            :comments="featured.comments">\
                    </c-tip>\
                    <div id="featured-box__other">Другие советы:</div>\
                    </div>\
                    <div id="no-tips-message" v-if="!hasTips && mode==\'place\' &&!featured">\
                        <div class="message-header">Ой! Здесь пока ничего нет...</div>\
                        <div class="message-body">\
                            Станьте первооткрывателем!<br/>Поделитесь своим опытом с другими путешественниками.<br/>\
                            Для кого-то любой ваш совет обязательно окажется полезным\
                        </div>\
                    </div>\
                    <div v-show="!showingTipForm&&allowAddTip" id="add-tip-btn" @click="showTipForm">\
                        <span class="glyphicon glyphicon-plus-sign"></span>\
                        <span>Поделитесь своим опытом</span>\
                    </div>\
                    <div v-if="showingTipForm" id="tip__add-new-form">\
                        <div id="addTipForm__header"><h2><span v-if="!allowEdit">Поделитесь своим опытом</span><span v-if="allowEdit">Редактировать пост</span></h2></div>\
                        <div @click="closeTipForm" id="addTipForm__close"><span class="glyphicon glyphicon-remove"></span></div>\
                        <div class="clearfix"></div>\
                        <div style="text-align:right" :class="{\'error-text\':limitError}">{{newTipForm.tipText.length}}/600</div>\
                        <textarea v-model="newTipForm.tipText" id = "add-new-form__textarea" :class="{\'error-text\':limitError}" placeholder="Напишите здесь свой совет другим путешественникам..."></textarea>\
                        <div id="add-new-form__added-tags">\
                                <span v-show="!newTipForm.addedTags.length">Добавьте от одной до пяти меток</span>\
                                <span class="form__added-tag back-{{t.style}}" transition="expand" v-for="t in newTipForm.addedTags"  @click="removeAddedTag($index)">\
                                {{t.name}}<span class="added-tag__remove-sign glyphicon glyphicon-remove" style="font-size:80%;"></span>\
                                </span>\
                            </div>\
                            \
                        <div id="add-new-form__tags" >\
                            <div class="add-new-form__popular-tags">\
                                <span class="form__main-tag back-{{t.style}}" v-for="t in newTipForm.popularTags" @click="addTag(\'popular\', $index)">\
                                {{t.name}}</span>\
                            </div>\
                            <div v-show="showingMoreTags" transition="expand">\
                                <span class="form__tag back-{{t.style}}" v-for="t in newTipForm.moreTags" @click="addTag(\'more\', $index)">{{t.name}}</span>\
                            </div>\
                            <div v-show="showingMoreTags"  transition="expand" ><span class="plink" @click="showMoreTags">Свернуть</span></div>\
                            <div v-show="!showingMoreTags"  transition="expand"><span class="plink" @click="showMoreTags">Показать больше</span></div>\
                            <div id="add-new-form__search-tags" :class="{\'search-active\':searchActive}">\
                                <span class="glyphicon glyphicon-search"></span>\
                                <input placeholder="Найти или создать метку" type="text" id="add-new-form__tags-ta" @keyup="tagsTextChanged" @blur="tagsTextChanged" v-model="newTipForm.tagsText"></input>\
                                <div id="add-new-form__tags-ac">\
                                    <span class="form__tag back-{{t.style}}" v-for="t in newTipForm.acTags" @click="addTag(\'ac\', $index)">{{t.name}}</span>\
                                </div>\
                                <div v-show="searchActive && newTipForm.tagsText.length>1">\
                                    <span class="plink" @click="createTag">Создать новую метку "{{newTipForm.tagsText}}"</span>\
                                </div>\
                            </div>\
                        </div><div class="divider"></div>\
                            <div id="add-new-form__add-link">\
                            <span class="glyphicon glyphicon-link"></span>\
                            <input placeholder="Добавить ссылку" type="text" id="add-new-form__link-ta" @keyup="linkTextChanged" @blur="linkTextChanged" v-model="newTipForm.attachedUrl"></input>\
                            </div>\
                        <div class="divider"></div>\
                        <div class="alert alert-danger" v-show="newTipForm.error">{{newTipForm.errorMessage}}</div>\
                        <button @click="closeTipForm" class="btn btn-large btn-default" id="add-tip__cancel-btn">Отмена</button>\
                        <button v-if="!allowEdit" @click="submitTipForm(allowEdit)" class="btn btn-large btn-primary" id="add-tip__commit-btn" >Сохранить мой совет</button>\
                        <button v-if="allowEdit" @click="submitTipForm(allowEdit)" class="btn btn-large btn-primary" id="add-tip__commit-btn"  >Завершить редактирование</button>\
                    </div>\
                    <div id="tips__info" v-if="!showAll" >\
                        <div>Показаны советы с метками: </div>\
                        <div id="filter-message" v-html="tagsFilter.message" ></div>\
                        <div style="text-align:right" >\
                            <span class="glyphicon glyphicon-remove" @click="resetFilters"></span>\
                            <span class="plink" @click="resetFilters">Снять все фильтры</span></div>\
                    </div>\
                    \
                    <!-- ==== TIPS CONTENT ==== -->\
                    \
                    <div id="tips-content" v-if="!collapsed">\
                    <c-tip v-for="tip in shownTips" track-by="id" \
                            :tags="tip.tags" \
                            :author="tip.author"\
                            :id="tip.id" \
                            :fave="tip.favorite" \
                            :upvote="tip.like" \
                            :downvote="tip.dislike" \
                            :upvoted="tip.upvoted" \
                            :downvoted="tip.downvoted" \
                            :url="tip.url" \
                            :edit="allowEdit"\
                            :related="relatedUsers"\
                            :mode="mode"\
                            :text="tip.text"\
                            :featured="false"\
                            :place="tip.place_name"\
                            :country="tip.country_name"\
                            :countryurl="tip.country_url"\
                            :directionurl="tip.direction_url"\
                            :attachedurl="tip.attached_url"\
                            :comments="tip.comments">\
                    </c-tip>\
                    </div>\
                </div>\
                <div class="clearfix"></div>\
                </div>'
 
});
