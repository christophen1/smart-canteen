import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('smart_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload && typeof payload.code !== 'undefined') {
      if (payload.code === 200) return payload.data
      if (response.config?.silent) return Promise.reject(payload)
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(payload)
    }
    return payload
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('smart_token')
      router.push('/login')
    }
    if (!error.config?.silent) {
      ElMessage.error(error.response?.data?.message || error.message || '网络异常')
    }
    return Promise.reject(error)
  },
)

export default http

export const api = {
  login: (data) => http.post('/user/login', data),
  register: (data) => http.post('/user/register', data),
  userInfo: () => http.get('/user/info'),
  updateUserInfo: (data) => http.put('/user/info', data),
  categories: () => http.get('/category/list', { silent: true }),
  dishes: (params) => http.get('/dish/page', { params, silent: true }),
  dish: (id) => http.get(`/dish/${id}`, { silent: true }),
  submitOrder: (data) => http.post('/order', data),
  myOrders: (params) => http.get('/order/page', { params, silent: true }),
  orderDetail: (id) => http.get(`/order/${id}`),
  cancelOrder: (id) => http.put(`/order/${id}/cancel`),
  adminUsers: (params) => http.get('/admin/user/page', { params, silent: true }),
  adminUserStatus: (data) => http.put('/admin/user/status', data, { silent: true }),
  saveCategory: (data) => http.post('/admin/category', data),
  updateCategory: (data) => http.put('/admin/category', data),
  deleteCategory: (id) => http.delete(`/admin/category/${id}`),
  saveDish: (data) => http.post('/admin/dish', data),
  updateDish: (data) => http.put('/admin/dish', data),
  deleteDish: (id) => http.delete(`/admin/dish/${id}`),
  dishStatus: (data) => http.put('/admin/dish/status', data),
  adminOrders: (params) => http.get('/admin/order/page', { params, silent: true }),
  adminOrderStatus: (id, data) => http.put(`/admin/order/${id}/status`, data, { silent: true }),
  analysis: (type) => http.get(`/analysis/${type}`, { silent: true }),
}
