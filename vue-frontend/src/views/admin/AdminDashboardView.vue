<template>
  <div class="dashboard-page">
    <section class="spark-banner">
      <div>
        <p class="eyebrow">PySpark Batch Pipeline</p>
        <h2>把订单流水转换为备餐决策</h2>
        <p>每日定时读取 MySQL 订单数据，完成客流、高峰、销量与备餐预测四类批处理分析。</p>
      </div>
      <el-steps :active="4" finish-status="success" simple>
        <el-step title="JDBC 读取" />
        <el-step title="DataFrame 聚合" />
        <el-step title="窗口预测" />
        <el-step title="写回结果表" />
      </el-steps>
    </section>

    <div class="stat-grid">
      <el-card class="stat" v-for="item in stats" :key="item.label">
        <span class="muted">{{ item.label }}</span>
        <div class="stat-value">{{ item.value }}</div>
      </el-card>
    </div>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="24" :lg="14">
        <el-card>
          <template #header>
            <div class="toolbar" style="margin-bottom: 0">
              <strong>客流趋势</strong>
              <el-tag type="success">customer_flow.py</el-tag>
            </div>
          </template>
          <div ref="lineRef" class="chart" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card>
          <template #header>
            <div class="toolbar" style="margin-bottom: 0">
              <strong>备餐建议</strong>
              <el-tag type="warning">meal_prediction.py</el-tag>
            </div>
          </template>
          <el-table :data="predictions" height="360">
            <el-table-column prop="dishName" label="菜品" />
            <el-table-column prop="predictedSales" label="预测" width="90" />
            <el-table-column prop="suggestedPrepare" label="建议" width="90" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { api } from '../../api/http'
import { money } from '../../utils/format'

const lineRef = ref()
const predictions = ref([])
const flowRows = ref([])
const summary = ref({ orderCount: 0, salesAmount: 0, peakHour: '--', taskCount: 4 })
const stats = computed(() => [
  { label: '最近订单', value: summary.value.orderCount || 0 },
  { label: '最近销售额', value: money(summary.value.salesAmount) },
  { label: '高峰时段', value: summary.value.peakHour || '--' },
  { label: 'Spark 任务', value: `${summary.value.taskCount || 4} 个` },
])

function normalize(data) {
  if (Array.isArray(data)) return data
  return data?.records || data?.list || data?.data || []
}

onMounted(async () => {
  try {
    summary.value = await api.analysisSummary()
    predictions.value = summary.value.predictions || []
  } catch {
    predictions.value = []
  }
  try {
    flowRows.value = normalize(await api.analysis('customer-flow'))
  } catch {
    flowRows.value = []
  }
  await nextTick()
  const chart = echarts.init(lineRef.value)
  chart.setOption({
    grid: { left: 42, right: 20, top: 30, bottom: 34 },
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    xAxis: { type: 'category', data: flowRows.value.map((row) => row.analysisDate) },
    yAxis: { type: 'value' },
    series: [
      { name: '订单量', type: 'line', smooth: true, areaStyle: {}, data: flowRows.value.map((row) => row.dailyOrders), color: '#0f766e' },
      { name: '客单价', type: 'line', smooth: true, data: flowRows.value.map((row) => row.avgOrderAmount), color: '#d97706' },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>
