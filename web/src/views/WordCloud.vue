<template>
  <div class="wordcloud-page">
    <h2>品种词云图</h2>
    <div ref="varietyChart" style="width: 100%; height: 400px;"></div>

    <h2>城市词云图</h2>
    <div ref="areaChart" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { onMounted, ref } from 'vue'
import { fetchVarietyWordcloud, fetchAreaWordcloud } from '@/api'

const varietyChart = ref(null)
const areaChart = ref(null)

const initWordCloud = (element, data) => {
  const chart = echarts.init(element)
  const option = {
    tooltip: {},
    series: [{
      type: 'wordCloud',
      gridSize: 8,
      sizeRange: [12, 50],
      rotationRange: [-90, 90],
      shape: 'triangle',  // 改成心形（你也可以尝试其他形状，如 diamond）
      textStyle: {
        normal: {
          color: () => `rgb(${[
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160),
            Math.round(Math.random() * 160)
          ].join(',')})`
        }
      },
      data
    }]
  }
  chart.setOption(option)
}


onMounted(async () => {
  const varietyRes = await fetchVarietyWordcloud()
  const varietyData = varietyRes.data.data.map(item => ({
    name: item.variety,
    value: item.count
  }))
  initWordCloud(varietyChart.value, varietyData)

  const areaRes = await fetchAreaWordcloud()
  const areaData = areaRes.data.data.map(item => ({
    name: item.province,
    value: item.count
  }))
  initWordCloud(areaChart.value, areaData)
})
</script>

<style scoped>
.wordcloud-page {
  padding: 20px;
}
</style>
