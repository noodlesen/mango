

// AIRPORTS INSTANCE ========================================

var airports = new Vue({
    el: '#airports-section',
    data:{
        airports:[]
    },
    ready:function(){
        this.airports = airports.list;
    },
    template:'<section>\
                <div class="section-header"><h2>Аэропорты рядом</h2></div>\
                <div class="section-body">\
                    <div class="airport-card" v-for="a in airports">\
                        <div class="airport-card-code"><i class="demo-icon icon-flight">&#xe800;</i>{{a.code}}</div>\
                        <div class="airport-card-desc">\
                            {{a.name}}\
                        </div>\
                    </div>\
                </div>\
                </section>'
});


// SUBSCRIBE 2 PLACE

var placeSubscribe = new Vue({
    el: '#place-subscribe',
    data: {
        subscribed: false,
        placeId: 0
    },
    methods: {
        toggle: function(){
            var self = this;
            var action = this.subscribed ? 'unsubscribe' : 'subscribe';
            getResults('/place-subscribe', 'json', {cmd: action, pid: this.placeId}, function(res){
                if (res.status=='ok'){
                    self.subscribed = !self.subscribed;        
                }
            });
            
        }
    },
    computed:{
        msg: function(){
            return this.subscribed ? 'Вы подписаны':'Подписаться';
        }
    },
    ready: function(){
        this.subscribed = subscribed=='True' ? true : false;
        this.placeId = place_id;
    }
});