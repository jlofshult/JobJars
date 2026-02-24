<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900">Approvals ✅</h1>
      <p class="text-gray-500 mt-1">Review completed chores and reward requests from your children.</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6">
      {{ error }}
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-100 p-1 rounded-xl mb-6 w-fit">
      <button
        @click="activeTab = 'chores'"
        :class="activeTab === 'chores' ? 'bg-white shadow text-indigo-700 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="px-5 py-2 rounded-lg text-sm font-semibold transition-all"
      >
        Chore Approvals
        <span v-if="pendingAssignments.length > 0" class="ml-1.5 bg-amber-100 text-amber-700 text-xs font-bold px-1.5 py-0.5 rounded-full">
          {{ pendingAssignments.length }}
        </span>
      </button>
      <button
        @click="activeTab = 'rewards'"
        :class="activeTab === 'rewards' ? 'bg-white shadow text-indigo-700 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="px-5 py-2 rounded-lg text-sm font-semibold transition-all"
      >
        Reward Requests
        <span v-if="pendingRedemptions.length > 0" class="ml-1.5 bg-amber-100 text-amber-700 text-xs font-bold px-1.5 py-0.5 rounded-full">
          {{ pendingRedemptions.length }}
        </span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center items-center py-16">
      <svg class="animate-spin h-10 w-10 text-indigo-500" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
    </div>

    <template v-else>
      <!-- Chore Approvals tab -->
      <div v-if="activeTab === 'chores'">
        <div v-if="pendingAssignments.length === 0" class="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
          <div class="text-6xl mb-4">🎉</div>
          <p class="text-xl font-bold text-gray-500">All caught up!</p>
          <p class="text-gray-400 mt-1">No chores waiting for approval.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="assignment in pendingAssignments"
            :key="assignment.id"
            class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
          >
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div class="flex items-center gap-4">
                <span class="text-4xl">{{ assignment.chore?.icon || '⭐' }}</span>
                <div>
                  <h3 class="font-bold text-gray-800 text-lg">{{ assignment.chore?.title }}</h3>
                  <div class="flex flex-wrap items-center gap-2 mt-1">
                    <span class="text-sm text-gray-500">👧 {{ assignment.child_name }}</span>
                    <span class="text-gray-300">·</span>
                    <span class="text-sm text-gray-500">Completed {{ formatDate(assignment.completed_at) }}</span>
                    <span class="text-gray-300">·</span>
                    <span class="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">
                      +{{ Number(assignment.chore?.value || 0).toFixed(2) }} pts
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="bg-amber-100 text-amber-700 text-xs font-semibold px-2.5 py-1 rounded-full">Pending Approval</span>
                <button
                  @click="handleApproveAssignment(assignment.id)"
                  :disabled="processingId === assignment.id"
                  class="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold px-4 py-2 rounded-xl text-sm transition-colors"
                >
                  <span v-if="processingId === assignment.id">...</span>
                  <span v-else>Approve ✓</span>
                </button>
                <button
                  @click="openRejectModal(assignment)"
                  :disabled="processingId === assignment.id"
                  class="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-semibold px-4 py-2 rounded-xl text-sm transition-colors"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reward Requests tab -->
      <div v-if="activeTab === 'rewards'">
        <div v-if="pendingRedemptions.length === 0" class="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
          <div class="text-6xl mb-4">💰</div>
          <p class="text-xl font-bold text-gray-500">No reward requests!</p>
          <p class="text-gray-400 mt-1">Your children haven't requested any rewards yet.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="redemption in pendingRedemptions"
            :key="redemption.id"
            class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
          >
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div class="flex items-center gap-4">
                <span class="text-4xl">🎁</span>
                <div>
                  <h3 class="font-bold text-gray-800 text-lg">{{ redemption.description }}</h3>
                  <div class="flex flex-wrap items-center gap-2 mt-1">
                    <span class="text-sm text-gray-500">👧 {{ redemption.child_name }}</span>
                    <span class="text-gray-300">·</span>
                    <span class="bg-indigo-100 text-indigo-700 text-sm font-bold px-2 py-0.5 rounded-full">
                      💰 {{ Number(redemption.amount).toFixed(2) }} pts
                    </span>
                    <span class="text-gray-300">·</span>
                    <span class="text-sm text-gray-500">{{ formatDate(redemption.created_at) }}</span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="bg-amber-100 text-amber-700 text-xs font-semibold px-2.5 py-1 rounded-full">Pending</span>
                <button
                  @click="handleApproveRedemption(redemption.id)"
                  :disabled="processingId === redemption.id"
                  class="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold px-4 py-2 rounded-xl text-sm transition-colors"
                >
                  <span v-if="processingId === redemption.id">...</span>
                  <span v-else>Approve ✓</span>
                </button>
                <button
                  @click="handleRejectRedemption(redemption.id)"
                  :disabled="processingId === redemption.id"
                  class="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-semibold px-4 py-2 rounded-xl text-sm transition-colors"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Reject reason modal -->
    <div v-if="rejectTarget" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-2">Reject Chore Completion</h3>
        <p class="text-gray-500 text-sm mb-4">
          Rejecting <strong>{{ rejectTarget.chore?.title }}</strong> for {{ rejectTarget.child_name }}. Please provide a reason.
        </p>
        <textarea
          v-model="rejectReason"
          rows="3"
          placeholder="e.g. The dishes aren't fully washed, please redo them."
          class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-400 resize-none mb-4 text-sm"
        ></textarea>
        <div class="flex gap-3">
          <button @click="rejectTarget = null; rejectReason = ''" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2.5 rounded-xl transition-colors">
            Cancel
          </button>
          <button
            @click="confirmReject"
            :disabled="!rejectReason.trim() || processingId === rejectTarget?.id"
            class="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-semibold py-2.5 rounded-xl transition-colors"
          >
            <span v-if="processingId === rejectTarget?.id">Rejecting...</span>
            <span v-else>Reject</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  getAssignments,
  approveAssignment,
  rejectAssignment,
  getRedemptions,
  approveRedemption,
  rejectRedemption
} from '../../api/index.js'

const loading = ref(true)
const error = ref('')
const activeTab = ref('chores')
const assignments = ref([])
const redemptions = ref([])
const processingId = ref(null)

const rejectTarget = ref(null)
const rejectReason = ref('')

const pendingAssignments = computed(() =>
  assignments.value.filter(a => a.status === 'pending_approval')
)

const pendingRedemptions = computed(() =>
  redemptions.value.filter(r => r.status === 'pending')
)

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [assignRes, redemptRes] = await Promise.all([
      getAssignments(),
      getRedemptions()
    ])
    assignments.value = assignRes.data
    redemptions.value = redemptRes.data
  } catch {
    error.value = 'Failed to load approvals. Please refresh.'
  } finally {
    loading.value = false
  }
}

async function handleApproveAssignment(id) {
  processingId.value = id
  try {
    await approveAssignment(id)
    await fetchData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to approve. Please try again.'
  } finally {
    processingId.value = null
  }
}

function openRejectModal(assignment) {
  rejectTarget.value = assignment
  rejectReason.value = ''
}

async function confirmReject() {
  if (!rejectReason.value.trim()) return
  processingId.value = rejectTarget.value.id
  try {
    await rejectAssignment(rejectTarget.value.id, rejectReason.value.trim())
    rejectTarget.value = null
    rejectReason.value = ''
    await fetchData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to reject. Please try again.'
    rejectTarget.value = null
  } finally {
    processingId.value = null
  }
}

async function handleApproveRedemption(id) {
  processingId.value = id
  try {
    await approveRedemption(id)
    await fetchData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to approve redemption.'
  } finally {
    processingId.value = null
  }
}

async function handleRejectRedemption(id) {
  processingId.value = id
  try {
    await rejectRedemption(id)
    await fetchData()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to reject redemption.'
  } finally {
    processingId.value = null
  }
}

onMounted(fetchData)
</script>
