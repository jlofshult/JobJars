<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Welcome header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900">
          Hey, {{ authStore.user?.name }}! 🌟
        </h1>
        <p class="text-gray-500 mt-1">Pick some chores and earn rewards!</p>
      </div>
      <div class="flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-5 py-3 rounded-2xl shadow-lg">
        <span class="text-2xl">💰</span>
        <div>
          <div class="text-xs font-medium opacity-80">My Balance</div>
          <div class="text-2xl font-extrabold">{{ Number(authStore.user?.balance || 0).toFixed(2) }} pts</div>
        </div>
      </div>
    </div>

    <!-- Error -->
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
      <!-- Waiting for Approval -->
      <div v-if="waitingAssignments.length > 0" class="mb-8">
        <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span>⏳</span> Waiting for Approval
        </h2>
        <div class="space-y-3">
          <div
            v-for="assignment in waitingAssignments"
            :key="assignment.id"
            class="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-center gap-4"
          >
            <span class="text-3xl">{{ assignment.chore?.icon || '⭐' }}</span>
            <div class="flex-1">
              <h3 class="font-bold text-gray-800">{{ assignment.chore?.title }}</h3>
              <p class="text-sm text-amber-600 mt-0.5">Completed {{ formatDate(assignment.completed_at) }} · waiting for parent approval</p>
            </div>
            <span class="bg-amber-100 text-amber-700 text-xs font-bold px-3 py-1.5 rounded-full flex-shrink-0">
              +{{ Number(assignment.chore?.value || 0).toFixed(2) }} pts
            </span>
          </div>
        </div>
      </div>

      <!-- My Active Chores -->
      <div class="mb-8">
        <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span>🔥</span> My Active Chores
          <span v-if="activeAssignments.length > 0" class="text-sm font-semibold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
            {{ activeAssignments.length }}
          </span>
        </h2>

        <div v-if="activeAssignments.length === 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center text-gray-400">
          <div class="text-4xl mb-2">📭</div>
          <p class="font-medium">No active chores yet.</p>
          <p class="text-sm">Pick a chore from the list below to get started!</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="assignment in activeAssignments"
            :key="assignment.id"
            class="bg-white rounded-2xl shadow-sm border border-indigo-100 p-5 hover:shadow-md transition-shadow"
          >
            <div class="flex items-start gap-4 mb-4">
              <span class="text-4xl">{{ assignment.chore?.icon || '⭐' }}</span>
              <div class="flex-1">
                <h3 class="font-bold text-gray-800 text-lg">{{ assignment.chore?.title }}</h3>
                <p class="text-sm text-gray-500 mt-0.5">{{ assignment.chore?.description }}</p>
                <div class="flex gap-2 mt-2">
                  <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">
                    +{{ Number(assignment.chore?.value || 0).toFixed(2) }} pts
                  </span>
                  <span class="bg-gray-100 text-gray-600 text-xs font-semibold px-2 py-0.5 rounded-full">
                    Claimed {{ formatDate(assignment.claimed_at) }}
                  </span>
                </div>
              </div>
            </div>
            <button
              @click="handleComplete(assignment.id)"
              :disabled="processingId === assignment.id"
              class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-bold py-3 rounded-xl transition-colors shadow-md hover:shadow-lg"
            >
              <span v-if="processingId === assignment.id">Marking done...</span>
              <span v-else>Mark Complete ✓</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Available Chores -->
      <div>
        <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
          <span>✨</span> Available Chores
        </h2>

        <div v-if="availableChores.length === 0" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center text-gray-400">
          <div class="text-4xl mb-2">🎉</div>
          <p class="font-medium">You've claimed all available chores!</p>
          <p class="text-sm">Check back later for more.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <div
            v-for="chore in availableChores"
            :key="chore.id"
            class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow group"
          >
            <div class="flex items-start gap-3 mb-4">
              <span class="text-4xl">{{ chore.icon || '⭐' }}</span>
              <div class="flex-1">
                <h3 class="font-bold text-gray-800 group-hover:text-indigo-700 transition-colors">{{ chore.title }}</h3>
                <p class="text-sm text-gray-500 mt-0.5 line-clamp-2">{{ chore.description }}</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-2 mb-4">
              <span class="bg-green-100 text-green-700 text-sm font-bold px-3 py-1 rounded-full">
                💰 +{{ Number(chore.value).toFixed(2) }} pts
              </span>
              <span
                :class="chore.chore_type === 'repetitive' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'"
                class="text-xs font-semibold px-2.5 py-1 rounded-full"
              >
                {{ chore.chore_type === 'repetitive' ? '🔄 Repetitive' : '1️⃣ One-Time' }}
              </span>
              <span class="bg-gray-100 text-gray-600 text-xs font-semibold px-2.5 py-1 rounded-full">
                Ages {{ chore.age_min }}{{ chore.age_max ? `–${chore.age_max}` : '+' }}
              </span>
            </div>
            <button
              @click="handleClaim(chore.id)"
              :disabled="processingId === chore.id"
              class="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 disabled:opacity-60 text-white font-bold py-2.5 rounded-xl transition-all shadow-md hover:shadow-lg text-sm"
            >
              <span v-if="processingId === chore.id">Claiming...</span>
              <span v-else>Pick This Chore! 🙋</span>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth.js'
import { getChores, getAssignments, claimChore, completeAssignment, getMe } from '../../api/index.js'

const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const chores = ref([])
const assignments = ref([])
const processingId = ref(null)

// Assignments with in_progress status
const activeAssignments = computed(() =>
  assignments.value.filter(a => a.status === 'in_progress')
)

// Assignments waiting for parent approval
const waitingAssignments = computed(() =>
  assignments.value.filter(a => a.status === 'pending_approval')
)

// Chores not yet claimed (not in active or waiting assignments)
const claimedChoreIds = computed(() => {
  const active = assignments.value
    .filter(a => a.status === 'in_progress' || a.status === 'pending_approval')
    .map(a => a.chore_id)
  return new Set(active)
})

const availableChores = computed(() =>
  chores.value.filter(c => !claimedChoreIds.value.has(c.id))
)

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [choresRes, assignmentsRes] = await Promise.all([
      getChores(),
      getAssignments()
    ])
    chores.value = choresRes.data
    assignments.value = assignmentsRes.data
  } catch {
    error.value = 'Failed to load data. Please refresh.'
  } finally {
    loading.value = false
  }
}

async function refreshBalance() {
  try {
    const meRes = await getMe()
    authStore.user = meRes.data
    localStorage.setItem('jobjars_user', JSON.stringify(meRes.data))
  } catch {
    // Non-critical, silently fail
  }
}

async function handleClaim(choreId) {
  processingId.value = choreId
  error.value = ''
  try {
    await claimChore(choreId)
    await fetchData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to claim chore. Please try again.'
  } finally {
    processingId.value = null
  }
}

async function handleComplete(assignmentId) {
  processingId.value = assignmentId
  error.value = ''
  try {
    await completeAssignment(assignmentId)
    await fetchData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to mark chore as complete.'
  } finally {
    processingId.value = null
  }
}

onMounted(async () => {
  await fetchData()
  await refreshBalance()
})
</script>
