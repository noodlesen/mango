var cTip = Vue.extend({
    data: function(){
        return {
            text: 'остров Airborek - чудо расчудесное, мечта. Обязательно побывайте здесь! Белые попугаи, звездное небо, которое напоминает космические снимки или как - будто ты находишься на совершенно другой планете и конечно  главная достопримечательность этого острова - стаи мант',
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
            }
        },
        clickDisagree: function(){
            if (!this.agree && !this.disagree){
                this.disagreed++;
                this.disagree = true;
            }
        }

    },

    template: '<div class="item-block tip has-cmd-bar">\
                    <div class="item-block__body">\
                        <div class="tip__main-text">\
                           {{text}}\
                        </div>\
                        <div class="tip__tags">\
                            <span class="tip__tag">Что посмотреть</span>\
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
                </div>'
}); 

Vue.component('c-tip', cTip);

var f = new Vue({
    el: '#filters',
    data:{
        inactive: [
            {name: 'Что посмотреть', state: false, style:'', init: 'color-red'},
            {name: 'Как добраться', state: true,  style:'', init: 'color-yellow'},
            {name: 'Транспорт', state: true,   style:'', init: 'color-green'},
            {name: 'Цены', state: true,   style:'', init: 'color-green'}
        ]
    },
    methods:{
        toggleFilter: function(d){
            this.inactive[d].state = !this.inactive[d].state;
            if (!this.inactive[d].state){
                this.inactive[d].style = 'filter-item-inactive';
            } else {
                this.inactive[d].style = this.inactive[d].init;
            }
        }
    },

    ready: function(){
        for (i=0; i<this.inactive.length; i++){
            if (this.inactive[i].state){
                this.inactive[i].style= 'filter-item-inactive';
            }
            else{
              this.inactive[i].style= this.inactive[i].init;
            }
            
        }
    }
});

var t = new Vue({
    el:'#tips-content',
    data:{
        htext:'Hello wforld!!!'
    },
    ready: function(){
    },
    template:'<c-tip></c-tip>'
});