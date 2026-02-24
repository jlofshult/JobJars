<template>
  <nav class="bg-indigo-600 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <RouterLink to="/" class="flex items-center gap-2 text-white font-bold text-xl hover:opacity-90 transition-opacity">
            <span class="text-2xl">🫙</span>
            <span>JobJars</span>
          </RouterLink>
        </div>

        <!-- Desktop Navigation -->
        <div v-if="authStore.isLoggedIn" class="hidden md:flex items-center gap-6">
          <!-- Parent nav -->
          <template v-if="authStore.isParent">
            <RouterLink
              to="/parent"
              class="text-indigo-100 hover:text-white transition-colors font-medium"
              active-class="text-white border-b-2 border-white pb-0.5"
            >
              Dashboard
            </RouterLink>
            <RouterLink
              to="/parent/chores"
              class="text-indigo-100 hover:text-white transition-colors font-medium"
              active-class="text-white border-b-2 border-white pb-0.5"
            >
              Chores
            </RouterLink>
            <RouterLink
              to="/parent/children"
              class="text-indigo-100 hover:text-white transition-colors font-medium"
              active-class="text-white border-b-2 border-white pb-0.5"
            >
              Children
            </RouterLink>
            <RouterLink
              to="/parent/approvals"
              class="text-indigo-100 hover:text-white transition-colors font-medium"
              active-class="text-white border-b-2 border-white pb-0.5"
            >
              Approvals
            </RouterLink>
          </template>

          <!-- Child nav -->
          <template v-if="authStore.isChild">
            <RouterLink
              to="/child"
              class="text-indigo-100 hover:text-white transition-colors font-medium"
              active-class="text-white border-b-2 border-white pb-0.5"
            >
              My Chores
            </RouterLink>
            <RouterLink
              to="/child/rewards"
              class="text-indigo-100 hover:text-white transition-colors font-medium"
              active-class="text-white border-b-2 border-white pb-0.5"
            >
              My Rewards
            </RouterLink>
            <!-- Balance chip -->
            <span class="flex items-center gap-1 bg-indigo-500 text-white px-3 py-1 rounded-full text-sm font-semibold border border-indigo-400">
              💰 {{ formatBalance(authStore.user?.balance) }}
            </span>
          </template>

          <!-- User info + logout -->
          <div class="flex items-center gap-3 ml-2 pl-4 border-l border-indigo-400">
            <span class="text-indigo-200 text-sm">{{ authStore.user?.name }}</span>
            <button
              @click="handleLogout"
              class="bg-indigo-700 hover:bg-indigo-800 text-white text-sm px-3 py-1.5 rounded-lg transition-colors font-medium"
            >
              Logout
            </button>
          </div>
        </div>

        <!-- Mobile menu button -->
        <div v-if="authStore.isLoggedIn" class="md:hidden">
          <button
            @click="mobileOpen = !mobileOpen"
            class="text-indigo-100 hover:text-white p-2 rounded-lg transition-colors"
          >
            <svg v-if="!mobileOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="authStore.isLoggedIn && mobileOpen" class="md:hidden bg-indigo-700 border-t border-indigo-500">
      <div class="px-4 pt-3 pb-4 space-y-2">
        <!-- Parent mobile nav -->
        <template v-if="authStore.isParent">
          <RouterLink to="/parent" @click="mobileOpen = false" class="block text-indigo-100 hover:text-white py-2 font-medium">Dashboard</RouterLink>
          <RouterLink to="/parent/chores" @click="mobileOpen = false" class="block text-indigo-100 hover:text-white py-2 font-medium">Chores</RouterLink>
          <RouterLink to="/parent/children" @click="mobileOpen = false" class="block text-indigo-100 hover:text-white py-2 font-medium">Children</RouterLink>
          <RouterLink to="/parent/approvals" @click="mobileOpen = false" class="block text-indigo-100 hover:text-white py-2 font-medium">Approvals</RouterLink>
        </template>

        <!-- Child mobile nav -->
        <template v-if="authStore.isChild">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-indigo-200 text-sm">{{ authStore.user?.name }}</span>
            <span class="flex items-center gap-1 bg-indigo-500 text-white px-2 py-0.5 rounded-full text-sm font-semibold">
              💰 {{ formatBalance(authStore.user?.balance) }}
            </span>
          </div>
          <RouterLink to="/child" @click="mobileOpen = false" class="block text-indigo-100 hover:text-white py-2 font-medium">My Chores</RouterLink>
          <RouterLink to="/child/rewards" @click="mobileOpen = false" class="block text-indigo-100 hover:text-white py-2 font-medium">My Rewards</RouterLink>
        </template>

        <div class="pt-2 border-t border-indigo-600">
          <span class="block text-indigo-300 text-sm mb-2">{{ authStore.user?.name }}</span>
          <button
            @click="handleLogout"
            class="w-full text-left bg-indigo-800 hover:bg-indigo-900 text-white text-sm px-3 py-2 rounded-lg transition-colors font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()
const router = useRouter()
const mobileOpen = ref(false)

function formatBalance(val) {
  if (val == null) return '0.00'
  return Number(val).toFixed(2)
}

function handleLogout() {
  authStore.logout()
  mobileOpen.value = false
  router.push('/login')
}
</script>
