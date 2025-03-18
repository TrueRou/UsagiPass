import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import Notification from './components/widgets/Notification.vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.component('Notification', Notification)

app.mount('#app')
