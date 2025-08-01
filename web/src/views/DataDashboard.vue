<template>
  <div class="dashboard">
    <div class="header">
      <h1 class="title">农产品价格可视化大数据展示平台</h1>
      <div class="time">当前时间: {{ currentTime }}</div>
    </div>

    <div class="main-content">
      <!-- 左侧面板 - 修改为独立框架 -->
      <div class="left-panel">
        <!-- 实时农产品统计 -->
        <div class="panel-item">
          <div class="panel-header">实时农产品统计</div>
          <div class="stats-container">
            <div class="digital-counter">
              <!-- 遍历 digits 数组，每个数字都用一个 span 来显示 -->
              <span
                v-for="(digit, index) in digits"
                :key="index"
                class="digit"
              >
                {{ digit }}
              </span>
              <span class="unit">种</span>
            </div>

            <div class="sub-header">农产品产量</div>
            <div id="waterChart" class="water-chart"></div>
          </div>
        </div>

        <!-- 全国地方比例 -->
        <div class="panel-item">
          <div class="panel-header">全国地方比例</div>
          <div class="gender-ratio">
            <div class="gender-label">
              <span>全国: {{ data.national_percentage }}%</span>
              <span>地方: {{ data.local_percentage }}%</span>
            </div>
            <div class="gender-bar">
              <div class="male-bar" style="width: 60%"></div>
              <div class="female-bar" style="width: 40%"></div>
            </div>
          </div>
        </div>

        <!-- 价格比例 -->
        <div class="panel-item" style="flex: 2">  <!-- 增加flex比例 -->
          <div class="panel-header">价格比例</div>
          <div id="ageChart" class="age-chart"></div>
        </div>
      </div>

      <!-- 中间地图区域 -->
      <div class="center-panel">
        <div class="panel-header">区域分布热度图</div>
        <div id="regionChart" class="map-chart"></div>
        <div class="map-legend" style="left: auto; right: 20px">
          <div class="legend-item">
            <span class="legend-color high"></span>
            <span class="legend-label">高</span>
          </div>
          <div class="legend-item">
            <span class="legend-color medium"></span>
            <span class="legend-label">中</span>
          </div>
          <div class="legend-item">
            <span class="legend-color low"></span>
            <span class="legend-label">低</span>
          </div>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <div class="panel-item">
          <div class="panel-header">热门农产品价格排行</div>
          <div class="ranking-list">
            <!-- 遍历 top_items -->
            <div
              class="ranking-item"
              v-for="(item, index) in data.top_items"
              :key="index"
            >
              <!-- NO.X -->
              <span class="rank">NO.{{ index + 1 }}</span>

              <!-- 品种名称 -->
              <span class="area">{{ item.variety }}</span>

              <!-- 进度条：根据 price 大小计算一个宽度比例 -->
              <div class="progress-bar">
                <div class="progress" :style="{ width: computeWidth(item.price) }"></div>
              </div>

              <!-- 价格数值 -->
              <span class="value">{{ item.price }}</span>
            </div>
          </div>
        </div>

        <div class="panel-item">
          <div class="panel-header">年度农产品趋势统计</div>
          <div id="visitorTrendChart" class="trend-chart"></div>
        </div>

        <div class="panel-item">
          <div class="panel-header">品种占比统计</div>
          <div id="platformChart" class="platform-chart"></div>
        </div>
      </div>
    </div>

    <!-- 底部数据指标 -->
    <div class="bottom-panel">
      <!-- 最新数据日期 -->
      <div class="data-card">
        <div class="data-value">2025-03-10</div>
        <div class="data-label">最新数据日期</div>
        <div class="data-unit">更新于 15:30:45</div>
      </div>

      <!-- 最高价格品种 -->
      <div class="data-card">
        <div class="data-value">{{ data.highest_item ? data.highest_item.price : '---' }}</div>
        <div class="data-label">最高价格品种</div>
        <div class="data-unit">{{ data.highest_item ? data.highest_item.variety : '' }}</div>
      </div>

      <!-- 最低价格品种 -->
      <div class="data-card">
        <div class="data-value">{{ data.lowest_item ? data.lowest_item.price : '---' }}</div>
        <div class="data-label">最低价格品种</div>
        <div class="data-unit">{{ data.lowest_item ? data.lowest_item.variety : '' }}</div>
      </div>

      <!-- 平均价格 -->
      <div class="data-card">
        <div class="data-value">{{ data.avg_price ? data.avg_price : '---' }}</div>
        <div class="data-label">平均价格</div>
        <div class="data-unit">元/公斤</div>
      </div>

      <!-- 价格波动趋势 -->
      <div class="data-card">
        <div class="data-value">+2.5%</div>
        <div class="data-label">周环比变化</div>
        <div class="data-unit">较上周</div>
      </div>
    </div>

    <!-- 版权信息 -->
    <div class="footer">
      © 2025 yucn
    </div>
  </div>
</template>

<script>
import { fetchDashboardData } from '@/api';
import * as echarts from 'echarts';
// 导入本地中国地图数据
import chinaJson from '@/assets/map/china.json';
// 导入水型图所需的'echarts-liquidfill'
import 'echarts-liquidfill';

export default {
  data() {
    return {
      data: {},
      currentTime: '',
      timer: null
    };
  },
  computed: {
    digits() {
      // 把 this.data.total_varieties 变成字符串，然后拆分成数组
      // 例如 329692 -> '329692' -> ['3','2','9','6','9','2']
      const num = this.data.total_varieties || 0;
      return String(num).split('');
    }
  },
  async created() {
    this.updateTime();
    this.timer = setInterval(this.updateTime, 1000);
    await this.getDashboardData();
    this.$nextTick(() => {
      this.initCharts();
    });
  },
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    updateTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      this.currentTime = `${year}年${month}月${day}日 ${hours}:${minutes}:${seconds}`;
    },
    async getDashboardData() {
      try {
        const res = await fetchDashboardData();
        this.data = res.data;

        // 检查是否包含品种占比数据
        if (this.data.variety_ratio) {
          this.initVarietyRatioChart(this.data.variety_ratio); // 如果有品种占比数据，初始化图表
        }
      } catch (error) {
        console.error('获取数据失败:', error);
      }
    },
    handleResize() {
      const charts = ['regionChart', 'ageChart', 'visitorTrendChart', 'platformChart', 'waterChart'];
      charts.forEach(id => {
        const chart = echarts.getInstanceByDom(document.getElementById(id));
        if (chart) {
          chart.resize();
        }
      });
    },
      //热门农产品排行
      computeWidth(price) {
      const maxP = this.data.max_price || 1;
      const ratio = price / maxP;
      return (ratio * 100) + '%';
    },

    async initCharts() {
      // 注册中国地图
      echarts.registerMap('china', chinaJson);

      // 优化后的水型图配置
      const waterChart = echarts.init(document.getElementById('waterChart'));
      waterChart.setOption({
        series: [{
          type: 'liquidFill',
          data: [0.5], // 单个波浪表示50%
          radius: '78%',
          outline: {
            show: true,
            borderDistance: 3,
            itemStyle: {
              color: 'transparent',
              borderColor: '#F7B500',
              borderWidth: 2
            }
          },
          color: [{
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(247, 181, 0, 0.8)' },
              { offset: 1, color: 'rgba(247, 181, 0, 0.3)' }
            ]
          }],
          backgroundStyle: {
            color: 'rgba(0, 33, 64, 0.3)',
            borderColor: '#F7B500',
            borderWidth: 1
          },
          label: {
            normal: {
              formatter: '50%',
              textStyle: {
                fontSize: 20, // 缩小字体
                fontWeight: 'bold',
                color: '#F7B500',
                textBorderColor: 'rgba(0, 0, 0, 0.3)',
                textBorderWidth: 2
              },
              position: 'inside',
              verticalAlign: 'middle'
            }
          },
          itemStyle: {
            shadowBlur: 5,
            shadowColor: '#F7B500'
          },
          amplitude: 6,  // 减小波动幅度
          waveLength: '95%',
          period: 5200,
          direction: 'right'
        }]
      });

      // 价格比例图
      const ageChart = echarts.init(document.getElementById('ageChart'));
      ageChart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}%'
        },
        legend: {
          show: false
        },
        color: ['#FF6E76', '#37A2FF', '#7FE77E', '#975FE5'],
        series: [{
          name: '价格比例',
          type: 'pie',
          radius: ['35%', '60%'],  // 调整为环形
          center: ['50%', '50%'],
          itemStyle: {
            borderRadius: 5,
            borderColor: '#001F3F',
            borderWidth: 2
          },
          label: {
            show: true,
            position: 'inside',
            formatter: ({ percent, name }) =>
              `${name}\n${percent}%`,  // 两行显示
            color: '#fff',
            fontSize: 14,
            fontWeight: 'bold',
            lineHeight: 20,
            textBorderColor: 'rgba(0,0,0,0.5)',
            textBorderWidth: 1,
            rich: {
              name: {
                fontSize: 12,
                color: '#00FFFC'
              },
              percent: {
                fontSize: 16,
                color: '#FFEB7B',
                padding: [5, 0, 0, 0]
              }
            }
          },
          labelLine: {
            show: false  // 隐藏引导线
          },
          data: this.data.category_percentage.map(item => ({
          name: item.category,
          value: item.price_percentage  // 选择数量占比作为饼图的值
      }))
  }]
});

      // 地图
      const regionChart = echarts.init(document.getElementById('regionChart'));
      const values = this.data.region_distribution.map(item => item.value);
      const realMin = Math.min(...values);
      const realMax = Math.max(...values);
      regionChart.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{b}<br/>农产品均价: {c}元/公斤'
        },
        visualMap: {
          min: realMin,  // 动态最小值
          max: realMax,  // 动态最大值
          left: 'left',
          bottom: '10%',
          text: ['高', '低'],
          inRange: {
            color: ['#003366', '#006699', '#00FFFC']
          },
          calculable: true,
          textStyle: {
            color: '#fff'
          }
        },
        series: [
          {
            name: '农产品均价',
            type: 'map',
            map: 'china',
            roam: false,
            emphasis: {
              label: {
                show: true
              },
              itemStyle: {
                areaColor: '#00FFFC'
              }
            },
            itemStyle: {
              areaColor: '#001529',
              borderColor: '#00FFFC',
              borderWidth: 1
            },
            // 使用后端返回的真实数据
            data: this.data.region_distribution
          }
        ]
      });

      // 农产品趋势图
  const visitorTrendChart = echarts.init(document.getElementById('visitorTrendChart'));
  visitorTrendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
      axisLine: { lineStyle: { color: '#00FFFC' } },
      axisLabel: { color: '#fff' }
    },
    yAxis: {
      type: 'value',
      name: '元/公斤',
      nameTextStyle: { color: '#00FFFC' },
      axisLine: { lineStyle: { color: '#00FFFC' } },
      splitLine: { lineStyle: { color: 'rgba(0, 255, 252, 0.1)' } },
      axisLabel: { color: '#fff' }
    },
    legend: {
      data: ['2023年', '2024年', '2025年'],
      textStyle: { color: '#00FFFC' },
      right: 10,
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    series: [
      {
        name: '2023年',
        type: 'line',
        data: this.data.yearly_trends['2023'], // 使用从后端获取的2023年数据
        lineStyle: { color: '#36CFFF' }
      },
      {
        name: '2024年',
        type: 'line',
        data: this.data.yearly_trends['2024'], // 使用从后端获取的2024年数据
        lineStyle: { color: '#FF6E76' }
      },
      {
        name: '2025年',
        type: 'line',
        data: this.data.yearly_trends['2025'], // 使用从后端获取的2025年数据
        lineStyle: { color: '#F7B500' }
      }
    ]
  });

      // 品种占比
const platformChart = echarts.init(document.getElementById('platformChart'));
platformChart.setOption({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c}% ({d}%)'
  },
  legend: {
    show: false
  },
  color: ['#FF6E76', '#37A2FF', '#975FE5', '#F7B500'],
  series: [
    {
      name: '品种占比',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      itemStyle: {
        borderRadius: 5,
        borderColor: '#001F3F',
        borderWidth: 2
      },
      label: {
        show: true,
        position: 'outside',
        formatter: '{b}',
        color: '#00FFFC',
        fontSize: 12
      },
      labelLine: {
        length: 15,
        length2: 10,
        lineStyle: {
          color: 'rgba(0, 255, 252, 0.5)'
        }
      },
      data: this.data.category_percentage.map(item => ({
        name: item.category,
        value: item.count_percentage  // 选择数量占比作为饼图的值
      }))
    }
  ]
});




      window.addEventListener('resize', this.handleResize);
    }

  }
};

</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
/* 新增水型图样式 */
.water-chart {
  height: 120px;
  width: 120px;
  margin: 0 auto;
  position: relative;
  background: rgba(0, 33, 64, 0.3);
  border-radius: 50%;
  box-shadow: 0 0 15px rgba(247, 181, 0, 0.3);
  border: 1px solid rgba(247, 181, 0, 0.5);
}

.dashboard {
  width: 100%;
  min-height: 100vh;
  padding: 0;
  min-height: 100vh;
  background-color: #001529; /* 更深的蓝色背景 */
  color: #fff;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(5, 40, 75, 0.8) 0%, rgba(0, 21, 41, 0.8) 100%),
    repeating-linear-gradient(0deg, transparent, transparent 1px, rgba(0, 255, 252, 0.03) 1px, rgba(0, 255, 252, 0.03) 2px);
  font-family: "Microsoft YaHei", sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  padding: 0 20px;
  background: linear-gradient(90deg, rgba(0, 33, 64, 0.7) 0%, rgba(0, 60, 105, 0.7) 50%, rgba(0, 33, 64, 0.7) 100%);
  position: relative;
  border-bottom: 1px solid #00FFFC;
}

.title {
  font-size: 20px;
  color: #00FFFC;
  margin: 0;
}

.time {
  font-size: 14px;
  color: #fff;
}

.main-content {
  flex: 1;
  display: flex;
  padding: 10px;
  gap: 10px;
}

.left-panel, .right-panel {
  width: 25%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.center-panel {
  flex: 1;
  position: relative;
}

.panel-item {
  background: rgba(0, 33, 64, 0.5);
  border: 1px solid #00FFFC;
  border-radius: 5px;
  padding: 10px;
  margin-bottom: 10px;
}

.panel-header {
  color: #00FFFC;
  font-size: 16px;
  padding-bottom: 5px;
  margin-bottom: 10px;
  border-bottom: 1px solid rgba(0, 255, 252, 0.3);
}

.sub-header {
  color: #00FFFC;
  font-size: 14px;
  text-align: center;
  margin: 10px 0;
}

.stats-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.digital-counter {
  display: flex;
  justify-content: center;
  margin: 15px 0 5px;
}

.digit {
  background: #001529;
  color: #00FFFC;
  font-size: 24px;
  padding: 5px 10px;
  margin: 0 2px;
  border-radius: 3px;
  border: 1px solid #00FFFC;
  box-shadow: 0 0 5px rgba(0, 255, 252, 0.3);
}

.unit {
  color: #00FFFC;
  font-size: 24px;
  margin-left: 5px;
  align-self: center;
}

.gender-ratio {
  margin-bottom: 15px;
}

.gender-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  color: #00FFFC;
  font-size: 14px;
}

.gender-bar {
  height: 10px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 5px;
  overflow: hidden;
  display: flex;
}

.male-bar {
  height: 100%;
  background: #37A2FF;
}

.female-bar {
  height: 100%;
  background: #FF6E76;
}

.age-chart {
  height: 260px;  /* 适当增加高度 */
  width: 100%;
  margin: 15px 0;
}

.map-chart {
  width: 100%;
  height: calc(100% - 30px);
}

.map-legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0, 33, 64, 0.7);
  padding: 5px 10px;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-color {
  width: 15px;
  height: 15px;
  border-radius: 3px;
}

.legend-color.high {
  background: #00FFFC;
}

.legend-color.medium {
  background: #006699;
}

.legend-color.low {
  background: #003366;
}

.legend-label {
  color: #00FFFC;
  font-size: 12px;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank {
  color: #00FFFC;
  font-size: 14px;
  width: 40px;
}

.area {
  width: 70px;
  font-size: 14px;
  color: #fff;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #00FFFC, #006699);
}

.value {
  width: 40px;
  font-size: 14px;
  text-align: right;
  color: #00FFFC;
}

.trend-chart, .platform-chart {
  height: 200px;
  width: 100%;
}

.bottom-panel {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 10px;
  height: 70px;
}

.data-card {
  flex: 1;
  background: rgba(0, 33, 64, 0.5);
  border: 1px solid #00FFFC;
  border-radius: 5px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.data-value {
  font-size: 20px;
  font-weight: bold;
  color: #00FFFC;
}

.data-label {
  font-size: 12px;
  color: #fff;
  margin-top: 2px;
}

.data-unit {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
}

.footer {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  padding: 5px 0;
}

@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
  }

  .left-panel, .center-panel, .right-panel {
    width: 100%;
  }

  .map-chart, .trend-chart, .platform-chart {
    height: 300px;
  }

  .bottom-panel {
    flex-wrap: wrap;
  }

  .data-card {
    min-width: 48%;
  }
}

@media (max-width: 768px) {
  .data-card {
    min-width: 100%;
  }
}
</style>
