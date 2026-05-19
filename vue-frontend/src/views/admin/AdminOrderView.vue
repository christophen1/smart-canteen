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
async function load() {
  loading.value = true
  try {
    const page = await api.adminOrders({ page: 1, size: 100 })
    orders.value = pageRecords(page)
  } catch {
    orders.value = []
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
