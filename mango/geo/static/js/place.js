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
                            <span v-for="t in tags" class="tip__tag" :class="t.style" >{{t.name}}</span>\
                        </div>\
                        <div class="tip__main-text">\
                           <slot></slot>\
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

    props: ['tags']
}); 

Vue.component('c-tip', cTip);


var tag = Vue.extend({
    template:'<div class="filter-item" :class="{\'filter-item-inactive\':state=\'off\'}">\
                        <span class="glyphicon glyphicon-tag" style="font-size:75%" ></span>\
                        <span>{{name}}</span>\
            </div>',
    data: function(){
        return {
        }
    },
    props:['name', 'color', 'state']
});

Vue.component('tag', tag);


var place = new Vue({
        template: '<div>\
                    <div id="filters" class="hidden-xs">\
                        <div class="tags__list">\
                            <h2>Метки</h2>\
                            <div id="tag-list"><tag v-for="t in tags" :name="t.name"></tag></div>\
                        </div>\
                    </div>\
                    <div id="tips">\
                        <div id="tips-content">\
                        <c-tip v-for="tip in tips" :tags="tip.tags">\
                            {{tip.text}}\
                        </c-tip>\
                        </div>\
                    </div>\
                    <div class="clearfix"></div></div>',

        el: '#place-tips',

        data: {
            tags:[],
            tips:[]
        },

        ready: function(){
            var self = this;
            getResults('/json/place', 'json', {place_id: place_id}, function(res){
                if (res.status=='ok'){
                    console.log (JSON.stringify(res));
                    self.tips=res.tips;
                    self.tags=res.place_tags;
                }
            });
        },

});

// ==========================================
/*
var tl = new Vue({
    el:'#tag-list',
    data: {
        place_tags:[]
    },
    ready: function(){
        this.place_tags = place_tags;
    },
    template:'<div id="filters-list"><tag name="Что посмотреть" color="red" state="off"></tag></div>'
});

                    

var t = new Vue({
    el:'#tips-content',
    data:{
        tips:[]
    },
    ready: function(){
        var self = this;
        getResults('/json/place', 'json', {place_id: place_id}, function(res){
            if (res.status=='ok'){
                console.log (JSON.stringify(res));
                self.tips=res.tips;
            }
        });
    },
    template:'<div><c-tip v-for="tip in tips" :tags="tip.tags">\
        {{tip.text}}\
    </c-tip></div>'
});*/