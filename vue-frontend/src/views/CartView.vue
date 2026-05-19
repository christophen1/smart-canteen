<template>
  <main class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/home"><span class="brand-mark">餐</span>智慧食堂</RouterLink>
      <el-button :icon="Tickets" @click="$router.push('/orders')">我的订单</el-button>
    </header>
    <section class="page">
      <div class="toolbar">
        <h2 class="section-title">购物车</h2>
        <strong class="price">{{ money(totalAmount) }}</strong>
      </div>
      <el-card class="table-card">
        <el-table :data="state.items" empty-text="购物车为空">
          <el-table-column label="菜品" min-width="180">
            <template #default="{ row }">
              <strong>{{ row.name }}</strong>
              <div class="muted">{{ row.categoryName }}</div>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120">
            <template #default="{ row }">{{ money(row.price) }}</template>
          </el-table-column>
          <el-table-column label="数量" width="180">
            <template #default="{ row }">
              <el-input-number :model-value="row.quantity" :min="0" :max="99" @change="(value) => update(row.id, value)" />
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="{ row }">{{ money(row.price * row.quantity) }}</template>
          </el-table-column>
          <el-table-column width="80">
            <template #default="{ row }">
              <el-button link type="danger" :icon="Delete" @click="remove(row.id)" />
            </template>
          </el-table-column>
        </el-table>
        <el-input v-model="remark" type="textarea" :rows="3" placeholder="备注口味、取餐时间等" style="margin: 18px 0" />
        <el-button type="primary" size="large" :disabled="!state.items.length" :loading="loading" @click="submit">提交订单</el-button>
      </el-card>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Tickets } from '@element-plus/icons-vue'
import { api } from '../api/http'
import { useCart } from '../stores/cart'
import { money } from '../utils/format'

const router = useRouter()
const { state, totalAmount, update, remove, clear } = useCart()
const remark = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await api.submitOrder({
      remark: remark.value,
      items: state.items.map((item) => ({ dishId: item.id, quantity: item.quantity })),
    })
    clear()
    ElMessage.success('订单已提交')
    router.push('/orders')
  } finally {
    loading.value = false
  }
}
</script>
