<template>
  <div class="price-sales-analysis">
    <div class="row">
      <el-card class="chart-card">
        <h2>城市价格最大值分析</h2>
        <base-chart :option="cityChartOption" height="400px" />
      </el-card>
      <el-card class="chart-card">
        <h2>类型价格平均值分析</h2>
        <base-chart :option="categoryChartOption" height="400px" />
      </el-card>
    </div>

    <div class="row">
      <el-card class="chart-card">
        <h2>平均价格时间趋势分析</h2>
        <base-chart :option="monthlyChartOption" height="400px" />
      </el-card>
      <el-card class="chart-card">
        <h2>价格区间占比分析</h2>
        <base-chart :option="priceRangeChartOption" height="400px" />
      </el-card>
    </div>

    <div class="row">
      <el-card class="chart-card">
        <h2>品种价格平均值分析</h2>
        <base-chart :option="varietyLineChartOption" height="400px" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getPriceSalesAnalysis } from '@/api'
import type { EChartsOption } from 'echarts'

const cityChartOption = ref<EChartsOption>({})
const categoryChartOption = ref<EChartsOption>({})
const monthlyChartOption = ref<EChartsOption>({})
const priceRangeChartOption = ref<EChartsOption>({})
const varietyLineChartOption = ref<EChartsOption>({})

onMounted(async () => {
  try {
    const res = await getPriceSalesAnalysis()
    if (res.data.code === 0) {
      const {
        city_max_price,
        category_avg_price,
        monthly_avg_price,
        price_range_distribution,
        variety_avg_price
      } = res.data.data
      updateCharts(city_max_price, category_avg_price, monthly_avg_price, price_range_distribution, variety_avg_price)
    }
  } catch (err) {
    console.error('获取价格和月销量分析数据失败', err)
  }
})

function updateCharts(cityData: any[], categoryData: any[], monthlyData: any[], priceRangeData: any[], varietyData: any[]) {
  cityChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: cityData.map(item => item.name),
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [{
      name: '最高价格',
      type: 'bar',
      data: cityData.map(item => item.value),
      itemStyle: { color: '#5470C6' }
    }]
  }

  categoryChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: categoryData.map(item => item.name),
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [{
      name: '平均价格',
      type: 'bar',
      data: categoryData.map(item => item.value),
      itemStyle: { color: '#91CC75' }
    }]
  }

  monthlyChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: monthlyData.map(item => item.name),
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [{
      name: '月均价格',
      type: 'line',
      data: monthlyData.map(item => item.value),
      itemStyle: { color: '#5470C6' },
      smooth: true,
      areaStyle: {}
    }]
  }

  priceRangeChartOption.value = {
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { fontSize: 12 }
    },
    series: [{
      name: '价格区间',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      data: priceRangeData,
      label: { formatter: '{b}: {c} ({d}%)' }
    }]
  }

  varietyLineChartOption.value = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: varietyData.map(item => item.name),
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [{
      name: '平均价格',
      type: 'line',
      data: varietyData.map(item => item.value),
      itemStyle: { color: '#D14A61' },
      smooth: true
    }]
  }
}
</script>

<style scoped>
.price-sales-analysis {
  padding: 20px;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.chart-card {
  flex: 1;
  min-width: 48%;
  box-sizing: border-box;
  transition: transform 0.3s;
}

.chart-card:hover {
  transform: scale(1.01);
}

.chart-card h2 {
  font-size: 18px;
  margin-bottom: 20px;
  text-align: center;
}
</style>
