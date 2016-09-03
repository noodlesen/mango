// TIP COMPONENT =========================================

var cTip = Vue.extend({
    data: function(){
        return {
            
            disagreed: 16,
            agreed: 34,
            agree: false,
            disagree:false,
            outdated: false
        }
    },
    methods:{
        clickAgree: function(){
            if (!this.agree && !this.disagree){
                this.agreed++;
                this.agree = true;
            } else if (this.agree){
                this.agreed--;
                this.agree=false;
            } else if (this.disagree){
                this.disagreed--;
                this.disagree=false;
                this.agreed++;
                this.agree=true;
            }
        },

        clickDisagree: function(){
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
        }

    },

    template: '<div class="item-block tip has-cmd-bar" :class="{\'tip-agreed\':agree, \'tip-disagreed\':disagree}">\
                    <div class="item-block__body">\
                          <div class="tip__tags">\
                                <span v-for="t in tags" class="tip__tag" :class="\'back-\'+t.style" >{{t.name}}</span>\
                            </div>\
                        <div class="tip__main-text">\
                           <slot></slot>\
                        </div>\
                        <div class="tip__bottom">\
                            <div class="tip__author" style="text-align:right">\
                                <span class="glyphicon glyphicon-user"></span>\
                                <a href="/user/{{author.id}}" >{{author.name}}</a>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="cmd-bar">\
                        \
                        <span class="cmd-bar__btn--disagree" :class="{\'cmd-bar__btn--disagree-active\':disagree}"  v-on:click="clickDisagree">\
                        <i class="btn-agree glyphicon glyphicon-remove"></i>\
                            <span>{{disagreed}}</span>\
                        </span>\
                        <span class="cmd-bar__btn--agree" :class="{\'cmd-bar__btn--agree-active\':agree}" v-on:click="clickAgree">\
                            <i class="btn-agree glyphicon glyphicon-ok"></i>\
                            <span>{{agreed}}</span>\
                        </span>\
                    </div>\
                </div>',

    props: ['tags', 'author']
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
                        <c-tip v-for="tip in shown_tips" :tags="tip.tags" :author="tip.author">\
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

                    console.log (JSON.stringify(self.selectedTags));
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