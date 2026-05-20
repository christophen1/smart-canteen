<template>
  <div class="analysis-page">
    <section class="analysis-hero">
      <div>
        <p class="eyebrow">经营分析</p>
        <h2>{{ config.title }}</h2>
        <p>{{ config.desc }}</p>
      </div>
      <div class="spark-code-card">
        <strong>{{ config.metric }}</strong>
        <span>{{ config.hint }}</span>
      </div>
    </section>

    <el-card>
      <template #header>
        <div class="toolbar" style="margin-bottom: 0">
          <strong>{{ config.chartTitle }}</strong>
          <el-button :icon="Refresh" @click="load">刷新</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" />
    </el-card>
    <el-card class="table-card" style="margin-top: 16px">
      <template #header>
        <strong>{{ config.tableTitle }}</strong>
      </template>
      <el-table :data="rows">
        <el-table-column v-for="column in config.columns" :key="column.prop" :prop="column.prop" :label="column.label" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { Refresh } from '@element-plus/icons-vue'
import { api } from '../../api/http'

const props = defineProps({ type: { type: String, required: true } })
const chartRef = ref()
const rows = ref([])
let chart

const configs = {
  'customer-flow': {
    title: '客流分析',
    chartTitle: '每日订单量与客单价',
    metric: '客流趋势',
    hint: '观察每日订单量、销售额和客单价变化',
    tableTitle: '每日客流明细',
    desc: '按日期汇总订单量、销售额、客单价和消费用户数，用于观察食堂整体客流趋势。',
    columns: [
      { prop: 'analysisDate', label: '日期' },
      { prop: 'dailyOrders', label: '订单量' },
      { prop: 'dailyAmount', label: '销售额' },
      { prop: 'avgOrderAmount', label: '客单价' },
    ],
  },
  'peak-hour': {
    title: '高峰时段识别',
    chartTitle: '分小时订单峰值',
    metric: '高峰时段',
    hint: '定位窗口备餐和排队压力最大的时间段',
    tableTitle: '小时客流明细',
    desc: '按小时统计订单量和销售额，定位午餐、晚餐的排队压力时段。',
    columns: [
      { prop: 'hour', label: '小时' },
      { prop: 'orderCount', label: '订单量' },
      { prop: 'totalAmount', label: '销售额' },
    ],
  },
  'dish-sales': {
    title: '热门菜品 TOP10',
    chartTitle: '菜品销量排行',
    metric: '销量排行',
    hint: '识别近期热销菜品和补货重点',
    tableTitle: '菜品销量明细',
    desc: '按菜品统计销量和销售额，帮助窗口安排热销菜品备餐。',
    columns: [
      { prop: 'dishName', label: '菜品' },
      { prop: 'salesCount', label: '销量' },
      { prop: 'salesAmount', label: '销售额' },
    ],
  },
  prediction: {
    title: '备餐预测',
    chartTitle: '预测销量与建议备餐',
    metric: '备餐建议',
    hint: '根据近期销量给出下一餐备餐参考',
    tableTitle: '备餐建议明细',
    desc: '根据近期销量趋势估算需求，并给出建议备餐量，降低缺餐和浪费。',
    columns: [
      { prop: 'dishName', label: '菜品' },
      { prop: 'predictedSales', label: '预测销量' },
      { prop: 'suggestedPrepare', label: '建议备餐' },
      { prop: 'confidence', label: '置信度' },
    ],
  },
}

const config = computed(() => configs[props.type])

function normalize(data) {
  const records = Array.isArray(data) ? data : data?.records || data?.list || data?.data || []
  if (props.type === 'peak-hour') {
    return records.map((row) => ({
      ...row,
      hour: row.hour != null && !String(row.hour).includes(':') ? `${String(row.hour).padStart(2, '0')}:00` : row.hour,
    }))
  }
  return props.type === 'customer-flow'
    ? records.slice().sort((a, b) => String(a.analysisDate || '').localeCompare(String(b.analysisDate || '')))
    : records
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  const labelKey = props.type === 'peak-hour' ? 'hour' : props.type === 'dish-sales' || props.type === 'prediction' ? 'dishName' : 'analysisDate'
  const firstValueKey = props.type === 'prediction' ? 'predictedSales' : props.type === 'dish-sales' ? 'salesCount' : props.type === 'peak-hour' ? 'orderCount' : 'dailyOrders'
  const secondValueKey = props.type === 'prediction' ? 'suggestedPrepare' : props.type === 'customer-flow' ? 'avgOrderAmount' : null
  chart.setOption({
    grid: { left: 46, right: 24, top: 36, bottom: 40 },
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    xAxis: { type: 'category', data: rows.value.map((row) => row[labelKey]) },
    yAxis: { type: 'value' },
    series: [
      { name: config.value.columns.find((c) => c.prop === firstValueKey)?.label, type: props.type === 'customer-flow' ? 'line' : 'bar', smooth: true, data: rows.value.map((row) => row[firstValueKey]), color: '#0f766e' },
      ...(secondValueKey ? [{ name: config.value.columns.find((c) => c.prop === secondValueKey)?.label, type: 'line', smooth: true, data: rows.value.map((row) => row[secondValueKey]), color: '#d97706' }] : []),
    ],
  })
}

async function load() {
  try {
    rows.value = normalize(await api.analysis(props.type, { page: 1, size: 100 }))
  } catch {
    rows.value = []
  }
  await nextTick()
  renderChart()
}

watch(() => props.type, load)
onMounted(() => {
  load()
  window.addEventListener('resize', () => chart?.resize())
})
</script>
