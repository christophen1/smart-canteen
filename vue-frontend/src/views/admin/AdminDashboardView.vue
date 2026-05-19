<template>
  <div class="dashboard-page">
    <section class="spark-banner">
      <div>
        <p class="eyebrow">运营概览</p>
        <h2>用订单数据安排出餐节奏</h2>
        <p>汇总近期订单、客流峰值、菜品销量和备餐建议，帮助窗口提前安排备餐与补货。</p>
      </div>
      <el-steps :active="4" finish-status="success" simple>
        <el-step title="订单汇总" />
        <el-step title="客流识别" />
        <el-step title="销量排行" />
        <el-step title="备餐建议" />
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
              <el-tag type="success">最近 30 天</el-tag>
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
              <el-tag type="warning">今日参考</el-tag>
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
import { money, pageRecords } from '../../utils/format'

const lineRef = ref()
const predictions = ref([])
const flowRows = ref([])
const summary = ref({ orderCount: 0, salesAmount: 0, peakHour: '--', taskCount: 4 })
const stats = computed(() => [
  { label: '最近订单', value: summary.value.orderCount || 0 },
  { label: '最近销售额', value: money(summary.value.salesAmount) },
  { label: '高峰时段', value: summary.value.peakHour || '--' },
  { label: '分析模块', value: `${summary.value.taskCount || 4} 个` },
])

function normalize(data) {
  if (Array.isArray(data)) return data
  return data?.records || data?.list || data?.data || []
}

function sortByDate(rows, key) {
  return rows.slice().sort((a, b) => String(a[key] || '').localeCompare(String(b[key] || '')))
}

function displayHour(hour) {
  if (hour == null) return '--'
  const text = String(hour)
  return text.includes(':') ? text : `${text.padStart(2, '0')}:00`
}

async function loadSummaryFromAnalysis() {
  const [predictionPage, peakPage, flowPage] = await Promise.all([
    api.analysis('prediction', { page: 1, size: 100 }),
    api.analysis('peak-hour', { page: 1, size: 24 }),
    api.analysis('customer-flow', { page: 1, size: 30 }),
  ])
  predictions.value = pageRecords(predictionPage)
  const peakRows = pageRecords(peakPage)
  flowRows.value = sortByDate(pageRecords(flowPage), 'analysisDate')
  const latestFlow = flowRows.value[flowRows.value.length - 1]
  const peak = peakRows.reduce((best, row) => (Number(row.orderCount || 0) > Number(best?.orderCount || 0) ? row : best), null)
  summary.value = {
    orderCount: latestFlow?.dailyOrders || 0,
    salesAmount: latestFlow?.dailyAmount || 0,
    peakHour: displayHour(peak?.hour),
    taskCount: 4,
  }
}

onMounted(async () => {
  try {
    summary.value = await api.analysisSummary()
    predictions.value = summary.value.predictions || []
  } catch {
    try {
      await loadSummaryFromAnalysis()
    } catch {
      predictions.value = []
      flowRows.value = []
    }
  }
  if (!flowRows.value.length) {
    try {
      flowRows.value = sortByDate(normalize(await api.analysis('customer-flow', { page: 1, size: 30 })), 'analysisDate')
    } catch {
      flowRows.value = []
    }
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
