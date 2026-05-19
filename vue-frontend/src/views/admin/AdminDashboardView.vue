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
import { nextTick, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { money } from '../../utils/format'

const lineRef = ref()
const predictions = ref([
  { dishName: '红烧牛肉饭', predictedSales: 86, suggestedPrepare: 104 },
  { dishName: '番茄鸡蛋面', predictedSales: 72, suggestedPrepare: 87 },
  { dishName: '香煎鸡腿套餐', predictedSales: 68, suggestedPrepare: 82 },
])
const stats = [
  { label: '今日订单', value: 238 },
  { label: '今日销售额', value: money(4628) },
  { label: '高峰时段', value: '12:00' },
  { label: 'Spark 任务', value: '4 个' },
]

onMounted(async () => {
  await nextTick()
  const chart = echarts.init(lineRef.value)
  chart.setOption({
    grid: { left: 42, right: 20, top: 30, bottom: 34 },
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [
      { name: '订单量', type: 'line', smooth: true, areaStyle: {}, data: [186, 205, 234, 218, 252, 176, 164], color: '#0f766e' },
      { name: '客单价', type: 'line', smooth: true, data: [18.6, 19.2, 19.8, 18.9, 20.1, 17.8, 18.4], color: '#d97706' },
    ],
  })
  window.addEventListener('resize', () => chart.resize())
})
</script>
