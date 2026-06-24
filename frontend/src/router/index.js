import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ImageInspect from '../views/ImageInspect.vue'
import InspectionManage from '../views/InspectionManage.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import UserManage from '../views/UserManage.vue'

const routes = [
    { path: '/', name: 'Home', component: Home },
    { path: '/image', name: 'ImageInspect', component: ImageInspect },
    { path: '/inspection', name: 'InspectionManage', component: InspectionManage },
    { path: '/login', name: 'Login', component: Login },
    { path: '/register', name: 'Register', component: Register },
    { path: '/users', name: 'UserManage', component: UserManage }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router