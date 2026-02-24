<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Welcome header -->
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900">
        Welcome back, {{ authStore.user?.name }}! 👋
      </h1>
      <p class="text-gray-500 mt-1">Here's what's happening in your household.</p>
    </div>

    <!-- Error alert -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6">
      {{ error }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-16">
      <svg class="animate-spin h-10 w-10 text-indigo-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
    </div>

    <template v-else>
      <!-- Stats cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col items-center text-center">
          <div class="text-4xl mb-2">📋</div>
          <div class="text-3xl font-extrabold text-indigo-600">{{ stats.totalChores }}</div>
          <div class="text-sm font-medium text-gray-500 mt-1">Total Chores</div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col items-center text-center">
          <div class="text-4xl mb-2">✅</div>
          <div class="text-3xl font-extrabold text-green-600">{{ stats.activeChores }}</div>
          <div class="text-sm font-medium text-gray-500 mt-1">Active Chores</div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col items-center text-center">
          <div class="text-4xl mb-2">👧</div>
          <div class="text-3xl font-extrabold text-purple-600">{{ stats.totalChildren }}</div>
          <div class="text-sm font-medium text-gray-500 mt-1">Children</div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col items-center text-center">
          <div class="text-4xl mb-2">⏳</div>
          <div class="text-3xl font-extrabold text-amber-600">{{ stats.pendingApprovals }}</div>
          <div class="text-sm font-medium text-gray-500 mt-1">Pending Approvals</div>
        </div>
      </div>

      <!-- Quick links + pending section -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Quick links -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 class="text-lg font-bold text-gray-800 mb-4">Quick Actions</h2>
          <div class="space-y-3">
            <RouterLink
              to="/parent/chores"
              class="flex items-center gap-3 p-3 rounded-xl bg-indigo-50 hover:bg-indigo-100 transition-colors group"
            >
              <span class="text-2xl">📋</span>
              <div>
                <div class="font-semibold text-indigo-700 group-hover:text-indigo-800">Manage Chores</div>
                <div class="text-xs text-indigo-500">Add, edit, or remove chores</div>
              </div>
            </RouterLink>
            <RouterLink
              to="/parent/children"
              class="flex items-center gap-3 p-3 rounded-xl bg-purple-50 hover:bg-purple-100 transition-colors group"
            >
              <span class="text-2xl">👨‍👩‍👧</span>
              <div>
                <div class="font-semibold text-purple-700 group-hover:text-purple-800">Manage Children</div>
                <div class="text-xs text-purple-500">Add or update child accounts</div>
              </div>
            </RouterLink>
            <RouterLink
              to="/parent/approvals"
              class="flex items-center gap-3 p-3 rounded-xl bg-amber-50 hover:bg-amber-100 transition-colors group"
            >
              <span class="text-2xl">✅</span>
              <div>
                <div class="font-semibold text-amber-700 group-hover:text-amber-800">Approvals</div>
                <div class="text-xs text-amber-500">Review completed chores & rewards</div>
              </div>
            </RouterLink>
          </div>
        </div>

        <!-- Pending approvals list -->
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-bold text-gray-800">Recent Pending Approvals</h2>
            <RouterLink to="/parent/approvals" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium">View all →</RouterLink>
          </div>

          <div v-if="pendingAssignments.length === 0" class="text-center py-8 text-gray-400">
            <div class="text-4xl mb-2">🎉</div>
            <p class="font-medium">No pending approvals!</p>
            <p class="text-sm">All caught up.</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="assignment in pendingAssignments.slice(0, 5)"
              :key="assignment.id"
              class="flex items-center justify-between p-3 rounded-xl bg-amber-50 border border-amber-100"
            >
              <div class="flex items-center gap-3">
                <span class="text-2xl">{{ assignment.chore?.icon || '⭐' }}</span>
                <div>
                  <div class="font-semibold text-gray-800 text-sm">{{ assignment.chore?.title }}</div>
                  <div class="text-xs text-gray-500">{{ assignment.child_name }} · {{ formatDate(assignment.completed_at) }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-green-600 bg-green-100 px-2 py-1 rounded-full">
                  +{{ assignment.chore?.value?.toFixed(2) }} pts
                </span>
                <span class="text-xs font-semibold text-amber-700 bg-amber-100 px-2 py-1 rounded-full">Pending</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '../../stores/auth.js'
import { getChores, getAssignments, getChildren } from '../../api/index.js'

const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const chores = ref([])
const assignments = ref([])
const children = ref([])

const pendingAssignments = computed(() =>
  assignments.value.filter(a => a.status === 'pending_approval')
)

const stats = computed(() => ({
  totalChores: chores.value.length,
  activeChores: chores.value.filter(c => c.is_active).length,
  totalChildren: children.value.length,
  pendingApprovals: pendingAssignments.value.length
}))

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [choresRes, assignmentsRes, childrenRes] = await Promise.all([
      getChores(),
      getAssignments(),
      getChildren()
    ])
    chores.value = choresRes.data
    assignments.value = assignmentsRes.data
    children.value = childrenRes.data
  } catch (err) {
    error.value = 'Failed to load dashboard data. Please refresh.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
