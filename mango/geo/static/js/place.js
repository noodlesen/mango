
moment.locale('ru');
// TIP COMPONENT =========================================

var cTip = Vue.extend({
    data: function(){
        return { 
            disagreed: 16,
            agreed: 34,
            agree: false,
            disagree:false,
            outdated: false,
            favorite: false,
            showingComments: false,
            commentText:''
        }
    },
    ready:function(){
        console.log(this.id+'>   '+this.fave);
        this.favorite = this.fave;
        if (this.like){
            this.agree=true;
        } else if (this.dislike){
            this.disagree = true;
        }
    },
    methods:{
        clickAgree: function(){
            var selected;
            if (!this.agree && !this.disagree){
            
                selected="none";
            } else if (this.agree){
             
                selected ="agree"
            } else if (this.disagree){

                selected = "disagree"
            }
            var self = this;
            getResults('/json/tip', 'json', {cmd: 'clickAgree', selected: selected, id: this.id}, function(res){
                if (res.status=='ok'){
                    switch (selected){
                        case "none":
                            self.agreed++;
                            self.agree = true;
                            break;
                        case "agree":
                            self.agreed--;
                            self.agree=false;
                            break;
                        case "disagree":
                            self.disagreed--;
                            self.disagree=false;
                            self.agreed++;
                            self.agree=true;
                            break;
                    }
                }
            });

        },        

        clickDisagree: function(){
            var selected;
            if (!this.agree && !this.disagree){
                selected="none";
            } else if (this.agree){
                selected ="agree"
            } else if (this.disagree){
                selected = "disagree"
            }
            var self = this;
            getResults('/json/tip', 'json', {cmd: 'clickDisagree', selected: selected, id: this.id}, function(res){
                if (res.status=='ok'){
                    switch (selected){
                        case "none":
                            self.disagreed++;
                            self.disagree = true;
                            break;
                        case "disagree":
                            self.disagreed--;
                            self.disagree=false;
                            break;
                        case "agree":
                            self.agreed--;
                            self.agree=false;
                            self.disagreed++;
                            self.disagree=true;
                            break;
                    }
                }
            });

        },

        toggleFavorite: function(){
            var self = this;
            getResults('/json/tip', 'json', {cmd: 'setFavorite', value: !this.favorite, id: this.id}, function(res){
                if (res.status=='ok'){
                    self.favorite = !self.favorite;
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

        addComment: function(){
            var self = this;
            getResults('/json/tip', 'json', {cmd: 'addComment', text: this.commentText, id: this.id}, function(res){
                if (res.status=='ok'){
                    self.commentText = '';
                    self.comments = res.comments;
                }
            });
        },

        getDate: function(timestamp){

            return moment.utc(timestamp, 'YY MM DD hh mm ss').fromNow();
        }
    },


    template: '<div>\
                <div class="item-block tip has-cmd-bar" :class="{\'tip-agreed\':agree, \'tip-disagreed\':disagree}">\
                    <div class="item-block__body">\
                            <div class="tip__top">\
                              <div class="tip__tags">\
                                    <span v-for="t in tags" class="tip__tag" :class="\'back-\'+t.style" @click="filterByTag(t.name)">{{t.name}}</span>\
                                </div>\
                                <div class="tip__favorite" @click="toggleFavorite">\
                                    <i v-if="!favorite" class="fa fa-star-o" title="Добавить в избранное"></i>\
                                    <i v-if="favorite" class="fa fa-star" title="Уже у вас в избранном"></i>\
                                </div>\
                                <div class="clearfix"></div>\
                            </div>\
                        <div class="tip__main-text">\
                           <slot></slot>\
                        </div>\
                        <div class="tip__bottom">\
                        </div>\
                    </div>\
                    <div class="item-block__sidebar">\
                        <div class="tip__vote-up" @click="clickAgree" :class="{\'tip__vote-up--active\':agree}">\
                            <span class="glyphicon glyphicon-ok" ></span>\
                        </div>\
                        <div class="tip__vote-dn"  @click="clickDisagree" :class="{\'tip__vote-dn--active\':disagree}">\
                            <span class="glyphicon glyphicon-remove" ></span>\
                        </div>\
                    </div><div class="clearfix"></div>\
                    <div class="cmd-bar">\
                        <div class="cmd-bar__left">\
                        <div class="cmd-bar__button">\
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
                        <div class="comment-text">{{c.text}}</div>\
                        <div class="comment-meta">{{c.author_id}} / {{getDate(c.timestamp)}}</div>\
                    </div>\
                    <div class="addCommentForm">\
                        <textarea v-model="commentText" class="addCommentForm__ta" rows="3" placeholder="Добавьте свой комментарий"></textarea>\
                    </div>\
                    <button @click="addComment" class="btn btn-large btn-warning">Добавить комментарий</button>\
                    <div class="divider"></div>\
                </div>\
                </div>',

    props: ['tags', 'author', 'id', 'fave', 'like', 'dislike', 'comments']
}); 

Vue.component('c-tip', cTip);


// FILTER TAG COMPONENT =========================================

var tag = Vue.extend({
    template:'<div class="filter-item" :class="[tag_class]" @click="toggle">\
                        <span class="glyphicon glyphicon-tag" :class="[act_color]" style="font-size:75%" ></span>\
                        <span>{{name}}</span>\
            </div>',
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
    }
});

Vue.component('tag', tag);

// VUE INSTANCE ========================================

var place = new Vue({
        template: '<div>\
                    <div id="filters" class="hidden-xs">\
                        <div class="tags__list">\
                            <h2>Метки</h2>\
                            <div id="tag-list"><tag v-for="t in tagsFilter.placeTags" :name="t.name" :color="t.style" :active="false"></tag></div>\
                        </div>\
                    </div>\
                    \
                    <!-- ==== TIPS COLUMN ==== -->\
                    \
                    <div id="tips">\
                        <div v-show="!addTipFormShowing"><span class="plink" @click="showAddTipForm">Добавьте свой совет!</span></div>\
                        <div v-if="addTipFormShowing" id="tip__add-new-form">\
                            <div id="addTipForm__header"><h2>Добавьте свой совет</h2></div>\
                            <div id="addTipForm__close"><span class="glyphicon glyphicon-remove"></span></div>\
                            <div class="clearfix"></div>\
                            <textarea id = "add-new-form__textarea" placeholder="Напишите здесь свой совет другим путешественникам..."></textarea>\
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
                            <button class="btn btn-large btn-normal" >Отмена</button>\
                            <button class="btn btn-large btn-warning" >Готово</button>\
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
                        <c-tip v-for="tip in shown_tips" :tags="tip.tags" :author="tip.author" :id="tip.id" :fave="tip.favorite" :like="tip.like" :dislike="tip.dislike" :comments="tip.comments">\
                            {{tip.showThis}}\
                            {{tip.text}}\
                        </c-tip>\
                        </div>\
                    </div>\
                    <div class="clearfix"></div></div>',

        el: '#place-tips',

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
                moreTags:[]
            },

            all_tips:[],
            shown_tips:[],
            showAll: true,
            addTipFormShowing: false,
            showingMoreTags: false
        },

        computed:{
            searchActive: function(){
                return this.newTipForm.tagsText!='';
            }
        },

        // METHODS **************************************************

        methods:{



            // ADD NEW TIP / TAGS ============================================

            showMoreTags: function(){
                this.showingMoreTags = !this.showingMoreTags;
            },

            createTag: function(){
                var name = this.newTipForm.tagsText;
                if(this.newTipForm.addedTags.filter(function(t){return t.name==name}).length==0){
                    var newTag = {name: name, style:'color-none', count:0};
                    this.newTipForm.addedTags.push(newTag); 
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
                this.addTipFormShowing = true;
            },

            // FILTER METHODS =========================================================

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

        // READY ********************************************************

        ready: function(){
            var self = this;
            var jd = JSON.parse(jsonData);
            
            self.all_tips=jd.tips;
            self.shown_tips=jd.tips;
            self.tagsFilter.placeTags=jd.place_tags;
            self.newTipForm.allTags=jd.all_tags;
            self.newTipForm.popularTags = jd.all_tags.slice(0, 12);
            self.newTipForm.moreTags = jd.all_tags.slice(12, 64);
            self.tagsFilter.placeTags.forEach(function(t){
                self.tagsFilter.selectedTags[t.name]=false;
            });
            self.relatedUsers=jd.related_users;
            console.log (JSON.stringify(self.relatedUsers));
/*            getResults('/json/place', 'json', {place_id: place_id}, function(res){
                if (res.status=='ok' || res.status=='not logged in'){
                    
                    self.all_tips=res.tips;
                    self.shown_tips=res.tips;
                    self.tagsFilter.placeTags=res.place_tags;
                    self.newTipForm.allTags=res.all_tags;
                    self.newTipForm.popularTags = res.all_tags.slice(0, 12);
                    self.newTipForm.moreTags = res.all_tags.slice(12, 64);
                    self.tagsFilter.placeTags.forEach(function(t){
                        self.tagsFilter.selectedTags[t.name]=false;
                    });

                    console.log (JSON.stringify(res));
                }
            });*/
        },

        // EVENTS ********************************************************

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
            }
        } 

});
