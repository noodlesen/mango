

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



