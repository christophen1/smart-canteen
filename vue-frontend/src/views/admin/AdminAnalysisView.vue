<template>
  <div class="analysis-page">
    <section class="analysis-hero">
      <div>
        <p class="eyebrow">Spark 分析任务</p>
        <h2>{{ config.title }}</h2>
        <p>{{ config.desc }}</p>
      </div>
      <div class="spark-code-card">
        <strong>{{ config.script }}</strong>
        <span>读取 MySQL -> DataFrame 转换 -> 写回分析结果表</span>
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
        <strong>分析结果表：{{ config.tableName }}</strong>
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
    script: 'customer_flow.py',
    tableName: 'customer_flow_analysis',
    desc: '按日期聚合订单量、销售额、客单价和消费用户数，用于观察食堂整体客流趋势。',
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
    script: 'peak_hour.py',
    tableName: 'peak_hour_analysis',
    desc: '从 create_time 中提取小时维度，定位午餐和晚餐的排队压力时段。',
    columns: [
      { prop: 'hour', label: '小时' },
      { prop: 'orderCount', label: '订单量' },
      { prop: 'totalAmount', label: '销售额' },
    ],
  },
  'dish-sales': {
    title: '热门菜品 TOP10',
    chartTitle: '菜品销量排行',
    script: 'dish_sales.py',
    tableName: 'dish_sales_analysis',
    desc: 'JOIN orders 与 order_item，按菜品分组统计销量和销售额，辅助窗口备餐。',
    columns: [
      { prop: 'dishName', label: '菜品' },
      { prop: 'salesCount', label: '销量' },
      { prop: 'salesAmount', label: '销售额' },
    ],
  },
  prediction: {
    title: '备餐预测',
    chartTitle: '预测销量与建议备餐',
    script: 'meal_prediction.py',
    tableName: 'meal_prediction',
    desc: '基于近 7 天销量移动平均预测次日销量，并乘以 1.2 安全系数生成建议备餐量。',
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
  if (Array.isArray(data)) return data
  return data?.records || data?.list || data?.data || []
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
    rows.value = normalize(await api.analysis(props.type))
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
