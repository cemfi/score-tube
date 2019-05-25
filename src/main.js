import Vue from 'vue';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import { Ripple } from 'vuetify/lib/directives';
import App from './App.vue';


Vue.config.productionTip = false;
Vue.use(Vuetify, {
  theme: {
    primary: '#222831',
    accent: '#f96d00',
  },
});

new Vue({
  render: h => h(App),
  directives: {
    Ripple,
  },
}).$mount('#app');
