<template>
  <main class="app-shell canteen-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/home"><span class="brand-mark">餐</span>智慧食堂</RouterLink>
      <el-space wrap>
        <el-input v-model="keyword" placeholder="搜索菜品" clearable :prefix-icon="Search" @change="loadDishes" />
        <el-badge :value="totalCount" :hidden="!totalCount">
          <el-button :icon="ShoppingCart" @click="$router.push('/cart')">购物车</el-button>
        </el-badge>
        <el-button :icon="Tickets" @click="$router.push('/orders')">我的订单</el-button>
        <el-button type="primary" plain :icon="DataAnalysis" @click="$router.push('/admin/analysis/prediction')">Spark 看板</el-button>
      </el-space>
    </header>

    <section class="canteen-hero">
      <div>
        <p class="eyebrow">Smart Canteen</p>
        <h1>校园点餐与备餐预测一体化</h1>
        <p class="hero-copy">
          学生在线点餐形成订单数据，PySpark 离线批处理每日汇总客流、高峰时段、热门菜品与次日备餐建议。
        </p>
        <el-space wrap>
          <el-button type="primary" size="large" :icon="ShoppingBag" @click="scrollToMenu">开始点餐</el-button>
          <el-button size="large" :icon="TrendCharts" @click="$router.push('/admin/dashboard')">查看运营后台</el-button>
        </el-space>
      </div>
      <div class="hero-panel">
        <div class="hero-panel-title">今日 Spark 预测</div>
        <div v-for="item in sparkCards" :key="item.label" class="spark-mini-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>
    </section>

    <section ref="menuRef" class="page">
      <div class="toolbar">
        <div>
          <h2 class="section-title">今日菜品</h2>
          <span class="muted">按分类浏览、搜索并加入购物车</span>
        </div>
        <el-tag type="success" size="large">实时接口数据</el-tag>
      </div>
      <el-tabs v-model="activeCategory" @tab-change="loadDishes">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane v-for="category in categories" :key="category.id" :label="category.name" :name="String(category.id)" />
      </el-tabs>
      <div v-loading="loading" class="grid">
        <el-card v-for="dish in dishes" :key="dish.id" class="dish-card" shadow="hover" :body-style="{ padding: 0 }">
          <img class="dish-image" :src="dish.image || fallbackImage" :alt="dish.name" />
          <div class="dish-body">
            <div class="dish-name-row">
              <strong>{{ dish.name }}</strong>
              <span class="price">{{ money(dish.price) }}</span>
            </div>
            <span class="muted">{{ dish.categoryName || '校园风味' }}</span>
            <p class="dish-desc">{{ dish.description || '窗口现做，适合午晚餐高峰快速取餐。' }}</p>
            <el-space>
              <el-button :icon="View" @click="$router.push(`/dish/${dish.id}`)">详情</el-button>
              <el-button type="primary" :icon="Plus" @click="addDish(dish)">加入</el-button>
            </el-space>
          </div>
        </el-card>
      </div>
      <el-empty v-if="!loading && !dishes.length" description="暂无菜品" />
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Plus, Search, ShoppingBag, ShoppingCart, Tickets, TrendCharts, View } from '@element-plus/icons-vue'
import { api } from '../api/http'
import { useCart } from '../stores/cart'
import { money, pageRecords } from '../utils/format'

const fallbackImage = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'
const sparkCards = ref([
  { label: '客流峰值', value: '12:00' },
  { label: '预测订单', value: '238 单' },
  { label: '需补备餐', value: '3 项' },
])

const loading = ref(false)
const keyword = ref('')
const activeCategory = ref('')
const categories = ref([])
const dishes = ref([])
const menuRef = ref()
const { add, totalCount } = useCart()

async function loadCategories() {
  try {
    categories.value = await api.categories()
  } catch {
    categories.value = []
  }
}

async function loadDishes() {
  loading.value = true
  try {
    const page = await api.dishes({ page: 1, size: 100, keyword: keyword.value || undefined })
    dishes.value = pageRecords(page)
  } catch {
    dishes.value = []
  } finally {
    dishes.value = activeCategory.value
      ? dishes.value.filter((dish) => String(dish.categoryId) === activeCategory.value)
      : dishes.value
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const summary = await api.analysisSummary()
    const predictions = summary.predictions || []
    sparkCards.value = [
      { label: '客流峰值', value: summary.peakHour || '--' },
      { label: '最近订单', value: `${summary.orderCount || 0} 单` },
      { label: '需补备餐', value: `${predictions.length} 项` },
    ]
  } catch {
    sparkCards.value = [
      { label: '客流峰值', value: '--' },
      { label: '最近订单', value: '0 单' },
      { label: '需补备餐', value: '0 项' },
    ]
  }
}

function addDish(dish) {
  add(dish)
  ElMessage.success('已加入购物车')
}

function scrollToMenu() {
  menuRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadDishes(), loadSummary()])
})
</script>
