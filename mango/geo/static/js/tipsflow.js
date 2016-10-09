
moment.locale('ru');

var relatedUsers =[];

$(document).ready(function(){
});




// TIP COMPONENT 
// ==================================================================================

var cTip = Vue.extend({
    data: function(){
        return { 
            upVote: false,
            downVote:false,
            outdated: false,
            favorite: false,
            showingComments: false,
            showingShare: false,
            commentText:'',
            signedIn: false
        }
    },
    ready:function(){
        this.signedIn = signedIn;
        //console.log(this.id+'>   '+this.fave);
        this.favorite = this.fave;
        if (this.upvote){
            this.upVote=true;
        } else if (this.downvote){
            this.downVote = true;
        }
    },
    computed: {
        hasComments : function(){
            return this.comments.length > 0;
        }
    },
    methods:{
        shareVk: function(){
            Share.vkontakte(this.url, 'Полезный совет', 'А тут собственно текст');
        },

        shareFacebook: function(){
            Share.facebook(this.url, 'Полезный совет');
        },

        shareTwitter: function(){
            Share.twitter(this.url, 'Полезный совет');
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
                getResults('/json/tip', 'json', {cmd: 'clickUpVote', selected: selected, id: this.id}, function(res){
                    if (res.status=='ok'){
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

        getDate: function(timestamp){
            return moment.utc(timestamp, 'YY MM DD hh mm ss').fromNow();
        },

        getUser: function(uid){
            console.log('get user: '+uid);
            return relatedUsers.find(function(u){ return u.id==uid}).nickname;
        }
    },


    template: '<div>\
                <div class="item-block tip has-cmd-bar" >\
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
                           <slot></slot> <span class="plink comment-link" v-if="hasComments" @click="toggleShowComments"> <i class="fa fa-comment"></i>{{comments.length}}</span>\
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
                                <div class="tip__share-link">Ссылка: <input type="text" size="40" v-model="url"></div>\
                    </div>\
                    <div class="cmd-bar">\
                        <div class="cmd-bar__left">\
                        <div class="cmd-bar__button" @click="toggleShowShare">\
                                <i class="fa fa-share-alt-square"></i> Поделиться\
                        </div>\
                        <div class="cmd-bar__button" @click="toggleShowComments">\
                                <i class="fa fa-comment-o"></i> Комментарии\
                        </div>\
                        </div>\
                        <div class="cmd-bar__right">\
                        <div class="cmd-bar__button tip__author">\
                                <a href="/user/{{author.id}}" ><span class="glyphicon glyphicon-user"></span> {{author.name}}</a>\
                        </div>\
                        </div>\
                        <div class="clearfix"></div>\
                    </div>\
                </div>\
                <div v-if="showingComments" class="comments">\
                    <div class="comment" v-for="c in comments">\
                        <div class="comment__text">{{c.text}}</div>\
                        <div class="comment__meta">{{getUser(c.author_id)}} / {{getDate(c.timestamp)}}</div>\
                    </div>\
                    <div class="addCommentForm" v-if="signedIn">\
                        <textarea v-model="commentText" class="addCommentForm__ta" rows="3" placeholder="Добавьте свой комментарий"></textarea>\
                    <button @click="addComment" class="btn btn-large btn-default add-comment__button">Добавить комментарий</button>\
                    </div>\
                    <div class="divider"></div>\
                </div>\
                </div>',

    props: ['tags', 'author', 'id', 'fave', 'upvote', 'downvote','upvoted', 'downvoted', 'comments', 'url']
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
                        <span>{{name}}</span>\
            </div>'
});

Vue.component('tag', tag);









// ================================================================================
//                                                                               //
//                      TIPFLOW VUE INSTANCE                                     //
//                                                                               //
// ================================================================================

var tipFlow = new Vue({
        
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
                tipText:''
            },

            all_tips:[],
            shown_tips:[],

            // CONFIG / STATE
            showAll: true,
            siModalShowing:true,
            signedIn:false,
            mode:'',
            showingAddTipForm: false,
            showingMoreTags: false,
            allowAddTip: true,
            allowFilters: true
        },

        computed:{
            searchActive: function(){
                return this.newTipForm.tagsText!='';
            }
        },


        // READY
        //............................
        ready: function(){
            
            var self = this;
            var jd = JSON.parse(jsonData);

            self.allowFilters = jd.config.allowFilters ? true : false;
            self.allowAddTip = jd.config.allowAddNewTip ? true : false;

            
            //self.mode = jd.mode;
            self.all_tips=jd.tips;
            self.shown_tips=jd.tips;
            self.sortTips();

            self.tagsFilter.placeTags=jd.place_tags;

            /*if (self.mode=='place'){
                self.newTipForm.allTags=jd.all_tags;
            } else {
                self.newTipForm.allTags =[];
            }*/
            self.newTipForm.allTags=jd.all_tags;


            self.newTipForm.popularTags = self.newTipForm.allTags.slice(0, 12);
            self.newTipForm.moreTags = self.newTipForm.allTags.slice(12, 64);
            self.tagsFilter.placeTags.forEach(function(t){
                self.tagsFilter.selectedTags[t.name]=false;
            });
            relatedUsers=jd.related_users;

            /*if (self.mode == 'user'){
                self.allowAddTip = false;
                self.allowFilters = false;
            }*/

            



            this.signedIn = signedIn;
        },

        // METHODS
        //............................
        methods:{

            sortTips: function(){
               this.shown_tips.sort(function(a,b){
                    var rating = function(t){ return t.upvoted - t.downvoted }
                    return rating(b) - rating(a);
                }); 
            },

            submitAddTipForm: function(){
                var self=this;
                getResults('/json/tip', 
                            'json', 
                            {
                                cmd:'addNew', 
                                tags: this.newTipForm.addedTags, 
                                text:this.newTipForm.tipText, 
                                placeID: place_id
                            },
                            function(res){
                                if (res.status=='ok'){
                                    self.showingAddTipForm = false;
                                    self.newTipForm.addedTags.forEach(function(t){
                                        if (self.tagsFilter.placeTags.find(function(pt){return pt.name == t.name }) == undefined){
                                            self.tagsFilter.placeTags.push(t);
                                        }
                                    });
                                    newTip = {
                                        favorite: false,
                                        like: false,
                                        dislike: false,
                                        upvoted:0,
                                        downvoted:0,
                                        text: self.newTipForm.tipText,
                                        tags: self.newTipForm.addedTags,
                                        author: {id: res.tip_data.author_id, name: res.tip_data.author_name},
                                        id: res.tip_data.tip_id
                                    };
                                    self.all_tips.push(newTip);
                                    self.shown_tips.push(newTip);
                                    self.resetNewTipForm();
                                } else {
                                    alert('error');
                                }
                            });
            },

            closeAddTipForm: function(){
                this.showingAddTipForm = false;
                this.resetNewTipForm();
            },

            resetNewTipForm: function(){
                var popularTagsTemp = this.newTipForm.popularTags;
                this.newTipForm = {
                    allTags:[],
                    acTags:[],
                    tagsText:'',
                    addedTags:[],
                    moreTags:[],
                    tipText:''
                }
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

            showAddTipForm: function(){
                if (signedIn){
                    this.showingAddTipForm = true;
                } else {
                    $('#si-modal').modal('show');
                }
                
            },

            // FILTER METHODS
            //............................
            resetFilters : function(){
                this.selectedTags = {};
                this.showAll = true;
                this.shown_tips = this.all_tips;
                this.$broadcast('eResetAllFilters');
            },
            

            filterTips: function(){
                var self = this;

                self.tagsFilter.message = "";
                Object.keys(this.tagsFilter.selectedTags).forEach(function(t){
                    console.log(t);
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

                this.shown_tips=[];
                    this.all_tips.forEach(function(tip){
                        tip.tags.forEach(function(tag){
                            if (self.tagsFilter.selectedTags[tag.name]){
                                self.shown_tips.push(tip);
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
                    this.shown_tips = this.all_tips;
                }
                console.log (JSON.stringify(this.tips));
            },

            'eFilterOnly': function(e){
                console.log(e);
                var self = this;
                this.showAll = false;
                Object.keys(this.tagsFilter.selectedTags).forEach(function(t){
                    self.tagsFilter.selectedTags[t]=false;
                });
                this.tagsFilter.selectedTags[e.name]=true;
                this.filterTips();
                this.$broadcast('eSwitchFilterOn',{name: e.name});
            },

            'eCheckTipsOrder': function(e){
                this.shown_tips.every(function(el, i){
                    if (el.id == e.id) {
                        el.upvoted = e.upvoted;
                        el.downvoted = e.downvoted;
                        return false;
                    }
                    else return true;
                });
                this.all_tips.every(function(el, i){
                    if (el.id == e.id) {
                        el.upvoted = e.upvoted;
                        el.downvoted = e.downvoted;
                        return false;
                    }
                    else return true;
                });
                console.log(JSON.stringify(this.shown_tips));
                this.sortTips();
            }
        },

        template: '<div>\
                    <div id="filters" class="hidden-xs" v-if="allowFilters">\
                        <div class="tags__list">\
                            <h2>Метки</h2>\
                            <div id="tag-list"><tag v-for="t in tagsFilter.placeTags" :name="t.name" :color="t.style" :active="false"></tag></div>\
                        </div>\
                    </div>\
                    \
                    <!-- ==== TIPS COLUMN ==== -->\
                    \
                    <div id="tips" :class="{\'tips-narrow\': allowFilters}">\
                        <div v-show="!showingAddTipForm&&allowAddTip" id="add-tip-btn" @click="showAddTipForm">\
                            <span class="glyphicon glyphicon-plus-sign"></span>\
                            <span>Добавьте свой совет!</span>\
                        </div>\
                        <div v-if="showingAddTipForm" id="tip__add-new-form">\
                            <div id="addTipForm__header"><h2>Добавьте свой совет</h2></div>\
                            <div @click="closeAddTipForm" id="addTipForm__close"><span class="glyphicon glyphicon-remove"></span></div>\
                            <div class="clearfix"></div>\
                            <textarea v-model="newTipForm.tipText" id = "add-new-form__textarea" placeholder="Напишите здесь свой совет другим путешественникам..."></textarea>\
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
                            <button @click="closeAddTipForm" class="btn btn-large btn-default" style="width:15%" >Отмена</button>\
                            <button @click="submitAddTipForm" class="btn btn-large btn-primary" style="width:84%" >Сохранить мой совет</button>\
                        </div>\
                        <div id="tips__info" v-if="!showAll" >\
                            <div>Показаны советы с метками: </div>\
                            <div id="filter-message" v-html="tagsFilter.message" ></div>\
                            <div style="text-align:right" @click="resetFilters">\
                                <span class="glyphicon glyphicon-remove"></span>\
                                <span class="plink">Снять все фильтры</span></div>\
                        </div>\
                        \
                        <!-- ==== TIPS CONTENT ==== -->\
                        \
                        <div id="tips-content">\
                        <c-tip v-for="tip in shown_tips" \
                                :tags="tip.tags" \
                                :author="tip.author"\
                                :id="tip.id" \
                                :fave="tip.favorite" \
                                :upvote="tip.like" \
                                :downvote="tip.dislike" \
                                :upvoted="tip.upvoted" \
                                :downvoted="tip.downvoted" \
                                :url="tip.url" \
                                :comments="tip.comments">\
                            {{tip.showThis}}\
                            {{tip.text}}\
                        </c-tip>\
                        </div>\
                    </div>\
                    <div class="clearfix"></div>\
                    </div>'
 

});
