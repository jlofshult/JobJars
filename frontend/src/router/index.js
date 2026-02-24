import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

import LoginView from '../views/LoginView.vue'
import ParentDashboard from '../views/parent/ParentDashboard.vue'
import ManageChores from '../views/parent/ManageChores.vue'
import ManageChildren from '../views/parent/ManageChildren.vue'
import ApprovalsView from '../views/parent/ApprovalsView.vue'
import ChildDashboard from '../views/child/ChildDashboard.vue'
import RewardsView from '../views/child/RewardsView.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/parent',
    name: 'parent-dashboard',
    component: ParentDashboard,
    meta: { requiresAuth: true, role: 'parent' }
  },
  {
    path: '/parent/chores',
    name: 'parent-chores',
    component: ManageChores,
    meta: { requiresAuth: true, role: 'parent' }
  },
  {
    path: '/parent/children',
    name: 'parent-children',
    component: ManageChildren,
    meta: { requiresAuth: true, role: 'parent' }
  },
  {
    path: '/parent/approvals',
    name: 'parent-approvals',
    component: ApprovalsView,
    meta: { requiresAuth: true, role: 'parent' }
  },
  {
    path: '/child',
    name: 'child-dashboard',
    component: ChildDashboard,
    meta: { requiresAuth: true, role: 'child' }
  },
  {
    path: '/child/rewards',
    name: 'child-rewards',
    component: RewardsView,
    meta: { requiresAuth: true, role: 'child' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (!authStore.isLoggedIn) {
    await authStore.loadUser()
  }

  if (to.meta.requiresAuth) {
    if (!authStore.isLoggedIn) {
      return next('/login')
    }
    if (to.meta.role && authStore.user?.role !== to.meta.role) {
      if (authStore.isParent) {
        return next('/parent')
      } else if (authStore.isChild) {
        return next('/child')
      }
      return next('/login')
    }
  }

  if (to.meta.requiresGuest && authStore.isLoggedIn) {
    if (authStore.isParent) {
      return next('/parent')
    } else if (authStore.isChild) {
      return next('/child')
    }
  }

  next()
})

export default router
