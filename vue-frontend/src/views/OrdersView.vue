<template>
  <main class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/home"><span class="brand-mark">餐</span>智慧食堂</RouterLink>
      <el-button :icon="ShoppingBag" @click="$router.push('/home')">继续点餐</el-button>
    </header>
    <section class="page">
      <div class="toolbar">
        <h2 class="section-title">我的订单</h2>
        <el-button :icon="Refresh" @click="load">刷新</el-button>
      </div>
      <el-card class="table-card">
        <el-table v-loading="loading" :data="orders">
          <el-table-column prop="orderNo" label="订单号" min-width="170" />
          <el-table-column label="金额" width="120">
            <template #default="{ row }">{{ money(row.totalAmount) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }"><el-tag :type="statusType[row.status]">{{ statusText[row.status] }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" min-width="170" />
          <el-table-column width="120">
            <template #default="{ row }">
              <el-button v-if="row.status === 1" link type="danger" @click="cancel(row.id)">取消</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Refresh, ShoppingBag } from '@element-plus/icons-vue'
import { api } from '../api/http'
import { money, pageRecords, statusText, statusType } from '../utils/format'

const loading = ref(false)
const orders = ref([])
async function load() {
  loading.value = true
  try {
    const page = await api.myOrders({ page: 1, size: 100 })
    orders.value = pageRecords(page)
  } catch {
    orders.value = []
  } finally {
    loading.value = false
  }
}

async function cancel(id) {
  await ElMessageBox.confirm('确认取消该订单？', '取消订单', { type: 'warning' })
  await api.cancelOrder(id)
  await load()
}

onMounted(load)
</script>
