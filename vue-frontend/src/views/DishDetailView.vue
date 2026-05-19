<template>
  <main class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/home"><span class="brand-mark">餐</span>智慧食堂</RouterLink>
      <el-button :icon="ShoppingCart" @click="$router.push('/cart')">购物车</el-button>
    </header>
    <section class="page">
      <el-card v-loading="loading">
        <el-row :gutter="28">
          <el-col :xs="24" :md="11">
            <img class="dish-image" :src="dish.image || fallbackImage" :alt="dish.name" />
          </el-col>
          <el-col :xs="24" :md="13">
            <h2>{{ dish.name }}</h2>
            <p class="muted">{{ dish.description || '清爽现做，适合校园午晚餐。' }}</p>
            <p class="price" style="font-size: 28px">{{ money(dish.price) }}</p>
            <el-form label-position="top">
              <el-form-item label="数量">
                <el-input-number v-model="quantity" :min="1" :max="99" />
              </el-form-item>
              <el-button type="primary" size="large" :icon="Plus" @click="addDish">加入购物车</el-button>
            </el-form>
          </el-col>
        </el-row>
      </el-card>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, ShoppingCart } from '@element-plus/icons-vue'
import { api } from '../api/http'
import { useCart } from '../stores/cart'
import { money } from '../utils/format'

const fallbackImage = 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1000&q=80'
const route = useRoute()
const router = useRouter()
const { add } = useCart()
const loading = ref(false)
const dish = ref({})
const quantity = ref(1)
const demoDishes = {
  1: { id: 1, categoryName: '主食套餐', name: '红烧牛肉饭', price: 18, description: 'Spark 预测今日销量 86 份，建议备餐 104 份，午餐高峰前优先补货。', image: '/demo/beef-rice.png' },
  2: { id: 2, categoryName: '主食套餐', name: '香煎鸡腿套餐', price: 20, description: '近 7 日午餐时段持续热销，适合窗口提前备餐。', image: '/demo/chicken-set.png' },
  3: { id: 3, categoryName: '汤粉面', name: '番茄鸡蛋面', price: 12, description: '移动平均销量稳定，晚餐时段需求较平缓。', image: '/demo/tomato-noodle.png' },
  4: { id: 4, categoryName: '热炒小碗', name: '麻婆豆腐', price: 10, description: '晚餐订单占比更高，Spark 分析建议 17:30 前完成补货。', image: '/demo/mapo-tofu.png' },
}

function addDish() {
  add(dish.value, quantity.value)
  ElMessage.success('已加入购物车')
  router.push('/cart')
}

onMounted(async () => {
  loading.value = true
  try {
    dish.value = await api.dish(route.params.id)
  } catch {
    dish.value = demoDishes[route.params.id] || demoDishes[1]
  } finally {
    loading.value = false
  }
})
</script>
