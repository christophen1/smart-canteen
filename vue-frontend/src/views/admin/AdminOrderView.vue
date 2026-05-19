<template>
  <el-card class="table-card">
    <div class="toolbar">
      <h2 class="section-title">订单管理</h2>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <el-table v-loading="loading" :data="orders">
      <el-table-column prop="orderNo" label="订单号" min-width="170" />
      <el-table-column prop="userId" label="用户ID" width="100" />
      <el-table-column label="金额" width="120"><template #default="{ row }">{{ money(row.totalAmount) }}</template></el-table-column>
      <el-table-column label="状态" width="150">
        <template #default="{ row }">
          <el-select :model-value="row.status" @change="(value) => setStatus(row.id, value)">
            <el-option v-for="(label, value) in statusText" :key="value" :label="label" :value="Number(value)" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="160" />
      <el-table-column prop="createTime" label="创建时间" min-width="170" />
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { api } from '../../api/http'
import { money, pageRecords, statusText } from '../../utils/format'

const loading = ref(false)
const orders = ref([])
const demoOrders = [
  { id: 101, orderNo: 'SC202605180001', userId: 12, totalAmount: 48, status: 2, remark: '午餐 12:10 取餐', createTime: '2026-05-18 11:42:08' },
  { id: 102, orderNo: 'SC202605180002', userId: 27, totalAmount: 30, status: 1, remark: '少辣', createTime: '2026-05-18 12:05:31' },
  { id: 103, orderNo: 'SC202605180003', userId: 8, totalAmount: 56, status: 3, remark: '窗口自取', createTime: '2026-05-18 12:18:45' },
  { id: 104, orderNo: 'SC202605170018', userId: 19, totalAmount: 26, status: 4, remark: '晚餐', createTime: '2026-05-17 18:17:44' },
]

async function load() {
  loading.value = true
  try {
    const page = await api.adminOrders({ page: 1, size: 100 })
    const records = pageRecords(page)
    orders.value = records.length ? records : demoOrders
  } catch {
    orders.value = demoOrders
  } finally {
    loading.value = false
  }
}

async function setStatus(id, status) {
  await api.adminOrderStatus(id, { status })
  await load()
}

onMounted(load)
</script>
