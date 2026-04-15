import { createRouter, createWebHistory } from 'vue-router'
import { isMobile } from '@/utils/device'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/ListView.vue'),
      beforeEnter: (to, _from, next) => {
        if (isMobile()) return next('/m/')
        next()
      },
    },
    {
      path: '/product/:id',
      component: () => import('@/views/DetailView.vue'),
      beforeEnter: (to, _from, next) => {
        if (isMobile()) return next(`/m/product/${to.params.id}`)
        next()
      },
    },
    // 手機端路由
    {
      path: '/m/',
      component: () => import('@/views/mobile/MobileListView.vue'),
    },
    {
      path: '/m/product/:id',
      component: () => import('@/views/mobile/MobileDetailView.vue'),
    },
    // 404 回首頁
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

export default router
