import { createRouter, createWebHistory } from 'vue-router/auto'
import type { RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router/auto'
import { useUserStore } from '@/store/user'
import { 
  DataLine, 
  Document, 
  Lock,
  Edit,
  View,
  User,
  Setting,
  Notebook
} from '@element-plus/icons-vue'
import type { Component } from 'vue'
import DataDashboard from '@/views/DataDashboard.vue';
import PriceTable from '@/views/PriceTable.vue'; // 注意导入路径
import CityCategoryAnalysis from '@/views/CityCategoryAnalysis.vue'
import WordCloud from '@/views/WordCloud.vue'


// 扩展 RouteMeta 类型
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: string[]
    title?: string
    icon?: Component
    hidden?: boolean
  }
}

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: {
      requiresAuth: true,
      title: '仪表盘',
      icon: 'Monitor'
    },
    children: [
      {
        path: '/',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          icon: 'Monitor'
        }
      },
        // 新增数据大屏的路由配置
      {
        path: '/dashboard/data',
        name: 'DataDashboard',
        component: DataDashboard,
        meta: {
          title: '数据大屏',
          icon: DataLine
        }
      }
    ]
  },
  {
    path: '/price',
    component: () => import('@/views/Layout.vue'),
    meta: {
      requiresAuth: true,
      title: '价格管理',
      icon: 'Files'
    },
    children: [
      {
        path: '/price-table',
        name: 'PriceTable',
        component: () => import('@/views/PriceTable.vue'),
        meta: {
          title: '价格数据管理',
          requiresAuth: true,
          icon: 'Files'
        }
      }
    ]
  },
  // 将城市和分类分析放到 Layout 内
  {
    path: '/analysis',
    component: () => import('@/views/Layout.vue'),
    meta: {
      requiresAuth: true,
      title: '数据分析',
      icon: 'Histogram'
    },
    children: [
      {
        path: '/city-category-analysis',
        name: 'CityCategoryAnalysis',
        component: () => import('@/views/CityCategoryAnalysis.vue'),
        meta: {
          title: '城市和分类分析',
          icon: 'Histogram'
        }
      },
      {
      path: '/price-sales',
      name: 'PriceSalesAnalysis',
      component: () => import('@/views/PriceSalesAnalysis.vue'),
      meta: {
          title: '价格和月销量分析',
          icon: 'TrendCharts'
        }
      }
    ]
  },
  {
  path: '/wordcloud',
  component: () => import('@/views/Layout.vue'),
  meta: {
    requiresAuth: true,
    title: '词云图',
    icon: 'PieChart'
  },
  children: [
    {
      path: '/wordcloud',
      name: 'WordCloud',
      component: () => import('@/views/WordCloud.vue'),
      meta: {
        title: '词云图',
        icon: 'PieChart'
      }
    }
  ]
},
{
  path: '/forecast',
  component: () => import('@/views/Layout.vue'),
  meta: {
    requiresAuth: true,
    title: '价格预测',
    icon: 'Connection'
  },
  children: [
    {
      path: '/forecast',
      name: 'Forecast',
      component: () => import('@/views/Forecast.vue'),
      meta: {
        title: '价格预测',
        icon: 'Connection'
      }
    }
  ]
},

  {
    path: '/auth/users',
    name: 'Auth',
    component: () => import('@/views/Layout.vue'),
    meta: { 
      title: '权限管理',
      icon: Lock,
      roles: ['admin', 'superuser']
    },
    children: [
      {
        path: '/auth/users',
        name: 'Users',
        component: () => import('@/views/auth/Users.vue'),
        meta: {
          title: '用户管理',
          icon: User
        }
      },
    ]
  },
  {
    path: '/oauth/callback',
    name: 'OAuthCallback',
    component: () => import('@/views/auth/OAuthCallback.vue'),
    meta: {
      title: '第三方登录',
      requiresAuth: false
    }
  },
  {
    path: '/system/oauth',
    name: 'System',
    component: () => import('@/views/Layout.vue'),
    meta: {
      title: '系统管理',
      requiresAuth: true,
      roles: ['superuser']
    },
  //  children: [
  //    {
  //      path: '/system/oauth',
  //      name: 'SystemOAuth',
  //      component: () => import('@/views/auth/OAuthConfig.vue'),
  //      meta: {
  //        title: '第三方登录配置',
  //        icon: Setting
  //      }
  //    }
  //  ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')

  // 等待用户信息初始化
  await userStore.initialize()

  if (to.meta.requiresAuth && !token) {
    // 需要登录但未登录，跳转到登录页
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.includes(userStore.user?.role)) {
    // 需要特定角色权限但没有权限，重定向到首页
    next('/')
  } else {
    next()
  }
})

export default router 
