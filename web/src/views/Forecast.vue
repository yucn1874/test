<template>
  <div class="p-8 max-w-5xl mx-auto">
    <h2 class="text-3xl font-bold mb-6 text-gray-800">
      农产品价格预测
    </h2>
    <div class="flex items-center gap-4 mb-8">
      <el-input
        v-model="variety"
        placeholder="请输入品种名"
        clearable
        style="width: 200px;"
      />
      <el-button type="primary" @click="getForecast">
        预测
      </el-button>
      <el-button
        v-if="forecastData.length > 0"
        type="info"
        @click="exportChart"
      >导出图表
      </el-button>
    </div>

    <div v-if="forecastData.length > 0" class="bg-white rounded-lg shadow-lg p-6">
      <!-- 保持原有图表不变 -->
      <div id="forecast-chart" class="w-full" style="height: 400px;"></div>

      <!-- 将下方的文字改为表格形式，并在价格列标题中添加单位 -->
      <h3 class="text-xl font-semibold mt-8 mb-4 text-gray-700">未来一周价格：</h3>
      <el-table
        :data="forecastData"
        border
        style="width: 100%"
        class="table-striped"
      >
        <el-table-column
          prop="date"
          label="日期"
          width="180"
        />
        <el-table-column
          prop="predicted_price"
          label="预测价格（元/公斤）"
        >
          <template #default="{ row }">
            <span class="font-medium text-blue-700">{{ row.predicted_price }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { fetchForecast } from '@/api'

const variety = ref('')
const forecastData = ref([])
let chartInstance = null

const getForecast = async () => {
  if (!variety.value) return
  try {
    const res = await fetchForecast(variety.value)
    forecastData.value = res.data.forecast || []
    await nextTick()
    renderChart()
  } catch (err) {
    console.error('预测失败:', err)
  }
}

const renderChart = () => {
  const chartDom = document.getElementById('forecast-chart')
  // 如果已有实例，先销毁
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartDom)

  const option = {
    title: {
      text: `${variety.value} 未来7天价格预测`,
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: '#ccc',
      borderWidth: 1,
      textStyle: {
        color: '#333'
      },
      formatter: function (params) {
        const data = params[0];
        return `${data.name}<br/>${data.seriesName}: <strong>${data.value}</strong> 元/公斤`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: forecastData.value.map(item => item.date),
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      axisLabel: {
        color: '#666'
      }
    },
    yAxis: {
      type: 'value',
      name: '价格（元/公斤）',
      nameTextStyle: {
        color: '#666'
      },
      axisLine: {
        show: true,
        lineStyle: {
          color: '#ddd'
        }
      },
      splitLine: {
        lineStyle: {
          color: '#eee'
        }
      }
    },
    series: [
      {
        name: '预测价格',
        type: 'line',
        smooth: true,
        data: forecastData.value.map(item => item.predicted_price),
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#3b82f6'
        },
        lineStyle: {
          width: 3,
          color: '#3b82f6'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {offset: 0, color: 'rgba(59, 130, 246, 0.3)'},
              {offset: 1, color: 'rgba(59, 130, 246, 0.05)'}
            ]
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)

  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize()
  })
}

// 导出图表为图片的函数
const exportChart = () => {
  if (!chartInstance) return

  try {
    // 获取图表的数据URL
    const dataURL = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2, // 提高导出图片的清晰度
      backgroundColor: '#fff'
    })

    // 创建下载链接
    const link = document.createElement('a')
    link.download = `${variety.value}价格预测_${new Date().toLocaleDateString()}.png`
    link.href = dataURL
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    console.error('导出图表失败:', err)
  }
}
</script>

<style scoped>
input {
  outline: none;
}

button {
  font-weight: 500;
  transition: all 0.2s ease;
}

button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(1px);
}

/* 表格样式美化 */
:deep(.el-table th) {
  background-color: #f3f4f6;
  color: #374151;
  font-weight: 600;
}

:deep(.el-table--border) {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
}

/* 添加斑马纹效果 */
:deep(.table-striped .el-table__row:nth-child(odd)) {
  background-color: #f9fafb;
}

:deep(.el-table__row:hover) {
  background-color: #f3f4f6 !important;
}
</style>