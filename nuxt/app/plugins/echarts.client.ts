import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, RadarChart, ScatterChart, GraphChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  RadarComponent,
  DataZoomComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

export default defineNuxtPlugin((nuxtApp) => {
  // Register ECharts components
  use([
    CanvasRenderer,
    PieChart,
    BarChart,
    RadarChart,
    ScatterChart,
    GraphChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    RadarComponent,
    DataZoomComponent,
    ToolboxComponent
  ])

  // Register VChart globally
  nuxtApp.vueApp.component('VChart', VChart)
})
