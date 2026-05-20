<template>
  <el-container class="admin-layout">
    <el-aside width="228px" class="admin-aside">
      <div class="admin-brand">智慧食堂后台</div>
      <el-menu router background-color="#102a43" text-color="#cbd5e1" active-text-color="#ffffff" :default-active="$route.path">
        <el-menu-item index="/admin/dashboard"><el-icon><DataBoard /></el-icon><span>运营工作台</span></el-menu-item>
        <el-menu-item index="/admin/category"><el-icon><Collection /></el-icon><span>分类管理</span></el-menu-item>
        <el-menu-item index="/admin/dish"><el-icon><Dish /></el-icon><span>菜品管理</span></el-menu-item>
        <el-menu-item index="/admin/order"><el-icon><Tickets /></el-icon><span>订单管理</span></el-menu-item>
        <el-menu-item index="/admin/user"><el-icon><User /></el-icon><span>用户管理</span></el-menu-item>
        <el-sub-menu index="/admin/analysis">
          <template #title><el-icon><TrendCharts /></el-icon><span>经营分析</span></template>
          <el-menu-item index="/admin/analysis/flow">客流分析</el-menu-item>
          <el-menu-item index="/admin/analysis/peak">高峰时段</el-menu-item>
          <el-menu-item index="/admin/analysis/dish">菜品销量</el-menu-item>
          <el-menu-item index="/admin/analysis/prediction">备餐预测</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="topbar admin-topbar" style="position: static">
        <div>
          <strong>{{ title }}</strong>
          <div class="muted admin-subtitle">订单、菜品、客流与备餐协同管理</div>
        </div>
        <el-space>
          <el-button :icon="House" @click="$router.push('/home')">用户端</el-button>
          <el-button :icon="SwitchButton" @click="logout">退出</el-button>
        </el-space>
      </el-header>
      <el-main class="admin-main"><RouterView /></el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Collection, DataBoard, Dish, House, SwitchButton, Tickets, TrendCharts, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const titles = {
  '/admin/dashboard': '运营工作台',
  '/admin/category': '分类管理',
  '/admin/dish': '菜品管理',
  '/admin/order': '订单管理',
  '/admin/user': '用户管理',
  '/admin/analysis/flow': '客流分析',
  '/admin/analysis/peak': '高峰时段',
  '/admin/analysis/dish': '菜品销量',
  '/admin/analysis/prediction': '备餐预测',
}
const title = computed(() => titles[route.path] || '管理后台')

function logout() {
  localStorage.removeItem('smart_token')
  localStorage.removeItem('smart_user')
  router.push('/admin/login')
}
</script>
