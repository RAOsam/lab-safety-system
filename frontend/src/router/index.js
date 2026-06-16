import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ImageInspect from '../views/ImageInspect.vue'
import InspectionManage from '../views/InspectionManage.vue'

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/image', name: 'ImageInspect', component: ImageInspect },
    { path: '/inspection', name: 'InspectionManage', component: InspectionManage }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router