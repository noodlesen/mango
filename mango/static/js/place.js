
var f = new Vue({
    el: '#cont',
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