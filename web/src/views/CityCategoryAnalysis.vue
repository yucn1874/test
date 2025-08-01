<template>
  <div class="city-category-analysis">
    <el-card>
      <div class="chart-header">
        <h2>城市（省份）和分类分析</h2>
        <div class="year-timeline">
          <el-button @click="prevYear" icon="ArrowLeft" size="small" />
          <span
            v-for="year in years"
            :key="year"
            :class="['year-item', { active: selectedYear === year }]"
            @click="setYear(year)"
          >{{ year }}</span>
          <el-button @click="nextYear" icon="ArrowRight" size="small" />

        </div>
      </div>
      <base-chart :option="chartOption" class="analysis-chart" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCityCategoryAnalysis } from '@/api'
import type { EChartsOption } from 'echarts'

const years = [2023, 2024, 2025]
const selectedYear = ref(2023)
const chartOption = ref<EChartsOption>({})
const autoplayTimer = ref<any>(null)
const rawData = ref<any>(null)

const colorMap: Record<string, string> = {
  '水产品': '#5470C6',
  '水果': '#91CC75',
  '畜禽产品': '#FAC858',
  '蔬菜': '#EE6666'
}
const categoryColor = (name: string) => colorMap[name] || '#ccc'

onMounted(() => {
  loadChartData()
})

function setYear(year: number) {
  selectedYear.value = year
  loadChartData()
}

function prevYear() {
  const index = years.indexOf(selectedYear.value)
  if (index > 0) setYear(years[index - 1])
}

function nextYear() {
  const index = years.indexOf(selectedYear.value)
  if (index < years.length - 1) setYear(years[index + 1])
}

function toggleAutoPlay() {
  if (autoplayTimer.value) {
    clearInterval(autoplayTimer.value)
    autoplayTimer.value = null
  } else {
    autoplayTimer.value = setInterval(() => {
      const index = years.indexOf(selectedYear.value)
      if (index < years.length - 1) {
        setYear(years[index + 1])
      } else {
        clearInterval(autoplayTimer.value)
        autoplayTimer.value = null
      }
    }, 2000)
  }
}

async function loadChartData() {
  try {
    const res = await getCityCategoryAnalysis(selectedYear.value)
    if (res.data.code === 0) {
      rawData.value = res.data.data
      buildChartOption()
    }
  } catch (err) {
    console.error('获取城市和分类分析数据失败', err)
  }
}

function buildChartOption() {
  const { xAxis, series, pie, categories } = rawData.value

  const cleanBarSeries = series.map((s: any) => ({
    ...s,
    type: 'bar',
    stack: undefined,
    label: {
      show: true,
      position: 'top',
      fontSize: 10,
      formatter: (params: any) => (params.value > 0 ? params.value : '')
    },
    barGap: 0,
    barCategoryGap: '70%',
    barWidth: 15,
    itemStyle: {
      color: categoryColor(s.name)
    }
  }))

  const pieSeries = {
    type: 'pie',
    name: '分类比例',
    radius: ['25%', '35%'],
    center: ['75%', '30%'],
    label: {
      formatter: '{b}\n{d}%',
      fontSize: 12
    },
    data: pie.map((item: any) => ({
      ...item,
      itemStyle: { color: categoryColor(item.name) }
    }))
  }

  chartOption.value = {
    title: {
      text: `城市分类统计（${selectedYear.value} 年）`,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    color: categories.map(c => categoryColor(c)),
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      top: 40,
      data: categories,
      textStyle: {
        fontSize: 13,
        color: '#333'
      }
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxis,
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [...cleanBarSeries, pieSeries]
  }
}
</script>

<style scoped>
.city-category-analysis {
  padding: 20px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.analysis-chart {
  width: 100%;
  min-height: 600px;
}

.year-timeline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.year-item {
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 14px;
  background: #f4f4f4;
  transition: all 0.2s;
}

.year-item.active {
  background-color: #409EFF;
  color: white;
  font-weight: bold;
}
</style>
