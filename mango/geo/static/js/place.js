// TIP COMPONENT =========================================

var cTip = Vue.extend({
    data: function(){
        return { 
            disagreed: 16,
            agreed: 34,
            agree: false,
            disagree:false,
            outdated: false,
            favorite: false
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

/*        clickDisagree: function(){
            if (!this.agree && !this.disagree){
                this.disagreed++;
                this.disagree = true;
            } else if (this.disagree){
                this.disagreed--;
                this.disagree=false;
            } else if (this.agree){
                this.agreed--;
                this.agree=false;
                this.disagreed++;
                this.disagree=true;
            }
        },*/

        toggleFavorite: function(){
            var self = this;
            getResults('/json/tip', 'json', {cmd: 'setFavorite', value: !this.favorite, id: this.id}, function(res){
                if (res.status=='ok'){
                    self.favorite = !self.favorite;
                }
            });
            
        }

    },

    template: '<div class="item-block tip has-cmd-bar" :class="{\'tip-agreed\':agree, \'tip-disagreed\':disagree}">\
                    <div class="item-block__body">\
                            <div class="tip__top">\
                              <div class="tip__tags">\
                                    <span v-for="t in tags" class="tip__tag" :class="\'back-\'+t.style" >{{t.name}}</span>\
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
                        <div class="cmd-bar__button">\
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
                </div>',

    props: ['tags', 'author', 'id', 'fave', 'like', 'dislike']
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
    props:['name', 'color', 'active']
});

Vue.component('tag', tag);

// VUE INSTANCE ========================================

var place = new Vue({
        template: '<div>\
                    <div id="filters" class="hidden-xs">\
                        <div class="tags__list">\
                            <h2>Метки</h2>\
                            <div id="tag-list"><tag v-for="t in tags" :name="t.name" :color="t.style" :active="false"></tag></div>\
                        </div>\
                    </div>\
                    <div id="tips">\
                        <div><span class="plink" @click="showAddTipForm">Добавьте свой совет!</span></div>\
                        <div v-if="addTipFormShowing">FORM</div>\
                        <div id="tips-content">\
                        <c-tip v-for="tip in shown_tips" :tags="tip.tags" :author="tip.author" :id="tip.id" :fave="tip.favorite" :like="tip.like" :dislike="tip.dislike">\
                            {{tip.showThis}}\
                            {{tip.text}}\
                        </c-tip>\
                        </div>\
                    </div>\
                    <div class="clearfix"></div></div>',

        el: '#place-tips',

        data: {
            tags:[],
            all_tips:[],
            shown_tips:[],
            selectedTags:{},
            showAll: true,
            addTipFormShowing: false
        },

        methods:{
            showAddTipForm: function(){
                this.addTipFormShowing = true;
            }
        },

        ready: function(){
            var self = this;
            getResults('/json/place', 'json', {place_id: place_id}, function(res){
                if (res.status=='ok'){
                    
                    self.all_tips=res.tips;
                    self.shown_tips=res.tips;
                    self.tags=res.place_tags;
                    self.tags.forEach(function(t){
                        self.selectedTags[t.name]=false;
                    });

                    console.log (JSON.stringify(res));
                }
            });
        },

        events: {
            'eFilterChanged': function(e){
                console.log('GOT IT!');
                var self = this;
                this.selectedTags[e.name] = e.value;

                var hasSelected = false;

                Object.keys(this.selectedTags).forEach(function(t){
                    if (self.selectedTags[t]){
                        hasSelected = true;
                    }
                });

                console.log('hasSelected '+hasSelected);

                this.showAll = hasSelected ? false : true;

                if (!this.showAll){
                    console.log ('SELECTED');
                    this.shown_tips=[];
                    this.all_tips.forEach(function(tip){
                        tip.tags.forEach(function(tag){
                            if (self.selectedTags[tag.name]){
                                //tip.showThis = true;
                                self.shown_tips.push(tip);
                            }
                        });
                    });
                } else {
                    this.shown_tips = this.all_tips;
                }
                console.log (JSON.stringify(this.tips));
            }
        }

});

// ==========================================

/*

<span class="cmd-bar__btn--disagree" :class="{\'cmd-bar__btn--disagree-active\':disagree}"  v-on:click="clickDisagree">\
                        <i class="btn-agree glyphicon glyphicon-remove"></i>\
                            <span>{{disagreed}}</span>\
                        </span>\
                        <span class="cmd-bar__btn--agree" :class="{\'cmd-bar__btn--agree-active\':agree}" v-on:click="clickAgree">\
                            <i class="btn-agree glyphicon glyphicon-ok"></i>\
                            <span>{{agreed}}</span>\
                        </span>\
                    </div>\*/