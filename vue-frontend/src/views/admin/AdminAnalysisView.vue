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
          <el-space>
            <el-date-picker
              v-if="props.type !== 'prediction'"
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DD"
              :shortcuts="dateShortcuts"
              style="width: 260px"
              @change="load"
            />
            <el-date-picker
              v-else
              v-model="predictDate"
              type="date"
              placeholder="选择预测日期"
              value-format="YYYY-MM-DD"
              style="width: 160px"
              @change="load"
            />
            <el-button :icon="Refresh" @click="load">刷新</el-button>
          </el-space>
        </div>
      </template>
      <div v-if="rows.length === 0" class="chart chart-empty">
        <el-empty description="暂无数据，请先运行 PySpark 分析" />
      </div>
      <div v-else ref="chartRef" class="chart" />
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { Refresh } from '@element-plus/icons-vue'
import { api } from '../../api/http'

const props = defineProps({ type: { type: String, required: true } })
const chartRef = ref()
const rows = ref([])
let chart

// 日期筛选
function fmt(d) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` }
function daysAgo(n) { const d = new Date(); d.setDate(d.getDate() - n); return d }
const dateRange = ref([fmt(daysAgo(7)), fmt(new Date())])
const predictDate = ref(fmt(new Date()))
const dateShortcuts = [
  { text: '最近7天', value: () => [daysAgo(7), new Date()] },
  { text: '最近30天', value: () => [daysAgo(30), new Date()] },
  { text: '最近90天', value: () => [daysAgo(90), new Date()] },
]

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
      { prop: 'totalUsers', label: '消费用户数' },
    ],
  },
  'peak-hour': {
    title: '高峰时段识别',
    chartTitle: '各时段日均订单量',
    metric: '高峰时段',
    hint: '定位窗口备餐和排队压力最大的时间段',
    tableTitle: '时段客流明细',
    desc: '跨所有日期按小时取日均订单量与销售额，识别午/晚餐的高峰时段。',
    columns: [
      { prop: 'analysisDate', label: '分析日期' },
      { prop: 'hour', label: '小时' },
      { prop: 'orderCount', label: '日均订单量' },
      { prop: 'totalAmount', label: '日均销售额' },
    ],
  },
  'dish-sales': {
    title: '热门菜品 TOP10',
    chartTitle: '菜品日均销量排行',
    metric: '销量排行',
    hint: '识别近期热销菜品和补货重点',
    tableTitle: '菜品销量明细',
    desc: '跨所有日期取日均销量与销售额，展示 TOP10 畅销菜品。',
    columns: [
      { prop: 'analysisDate', label: '分析日期' },
      { prop: 'dishName', label: '菜品' },
      { prop: 'salesCount', label: '日均销量' },
      { prop: 'salesAmount', label: '日均销售额' },
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
      { prop: 'predictDate', label: '预测日期' },
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
  if (records.length === 0) return []
  return records.map((row) => {
    const r = { ...row }
    // 截取 MM-DD 用于图表标签
    const dateStr = String(r.analysisDate || r.predictDate || '')
    if (dateStr.length >= 10) r._d = dateStr.slice(5) // "MM-DD"
    else r._d = dateStr
    // 小时格式化
    if (r.hour != null && !String(r.hour).includes(':')) {
      r._h = String(r.hour).padStart(2, '0') + ':00'
    } else {
      r._h = r.hour
    }
    return r
  })
}

function renderChart() {
  if (!chartRef.value || rows.value.length === 0) return
  // 每次都重新初始化，避免 ECharts 实例挂在已销毁的 DOM 上导致空白
  disposeChart()
  chart = echarts.init(chartRef.value)

  let xData
  if (props.type === 'peak-hour') {
    xData = rows.value.map((r) => r._h)
  } else if (props.type === 'dish-sales') {
    xData = rows.value.map((r) => r.dishName)
  } else if (props.type === 'prediction') {
    xData = rows.value.map((r) => r.dishName)
  } else {
    // customer-flow: 日期就够了，不会重复
    xData = rows.value.map((r) => r._d)
  }

  const firstValueKey = props.type === 'prediction' ? 'predictedSales' : props.type === 'dish-sales' ? 'salesCount' : props.type === 'peak-hour' ? 'orderCount' : 'dailyOrders'
  const secondValueKey = props.type === 'prediction' ? 'suggestedPrepare' : props.type === 'customer-flow' ? 'avgOrderAmount' : null

  chart.setOption({
    grid: { left: 46, right: 24, top: 36, bottom: props.type === 'dish-sales' ? 60 : 40 },
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    xAxis: { type: 'category', data: xData, axisLabel: props.type === 'dish-sales' ? { rotate: 30 } : undefined },
    yAxis: { type: 'value' },
    series: [
      { name: config.value.columns.find((c) => c.prop === firstValueKey)?.label, type: props.type === 'customer-flow' ? 'line' : 'bar', smooth: true, data: rows.value.map((row) => row[firstValueKey]), color: '#0f766e' },
      ...(secondValueKey ? [{ name: config.value.columns.find((c) => c.prop === secondValueKey)?.label, type: 'line', smooth: true, data: rows.value.map((row) => row[secondValueKey]), color: '#d97706' }] : []),
    ],
  })
}

async function load() {
  try {
    const params = { page: 1, size: 100 }
    if (props.type === 'prediction') {
      if (predictDate.value) params.predictDate = predictDate.value
    } else {
      if (dateRange.value?.length === 2) {
        params.startDate = dateRange.value[0]
        params.endDate = dateRange.value[1]
      }
    }
    const data = await api.analysis(props.type, params)
    rows.value = normalize(data)
  } catch (e) {
    console.error('分析数据加载失败:', e)
    rows.value = []
  }
  await nextTick()
  if (rows.value.length === 0) {
    disposeChart()
  } else {
    renderChart()
  }
}

function disposeChart() {
  if (chart && !chart.isDisposed()) {
    chart.dispose()
  }
  chart = null
}

watch(() => props.type, load)
onMounted(() => {
  load()
  window.addEventListener('resize', () => chart?.resize())
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', () => chart?.resize())
  disposeChart()
})
</script>

<style scoped>
.chart {
  width: 100%;
  height: 420px;
}
.chart.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
