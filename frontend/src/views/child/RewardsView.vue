<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-gray-900">My Rewards 🎁</h1>
      <p class="text-gray-500 mt-1">Redeem your earned points for awesome rewards!</p>
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
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Left column: balance + redeem form -->
        <div class="space-y-5">
          <!-- Balance card -->
          <div class="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl text-center">
            <div class="text-4xl mb-2">💰</div>
            <div class="text-sm font-medium opacity-80 mb-1">Current Balance</div>
            <div class="text-5xl font-extrabold mb-1">{{ Number(balance).toFixed(2) }}</div>
            <div class="text-sm opacity-70">points available</div>
          </div>

          <!-- Redeem form -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 class="text-lg font-bold text-gray-800 mb-4">🎉 Redeem Rewards</h2>

            <!-- Success message -->
            <div v-if="redeemSuccess" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl mb-4 text-sm flex items-center gap-2">
              <span>✅</span> Your redemption request has been sent to your parent!
            </div>

            <!-- Form error -->
            <div v-if="formError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4 text-sm">
              {{ formError }}
            </div>

            <form @submit.prevent="handleRedeem" class="space-y-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">
                  Amount (max: {{ Number(balance).toFixed(2) }}) <span class="text-red-500">*</span>
                </label>
                <input
                  v-model.number="redeemForm.amount"
                  type="number"
                  min="0.01"
                  :max="balance"
                  step="0.01"
                  placeholder="e.g. 10.00"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-1">
                  What do you want? <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="redeemForm.description"
                  rows="3"
                  placeholder="e.g. I want to go to the movies!"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none text-sm"
                ></textarea>
              </div>
              <button
                type="submit"
                :disabled="redeemLoading || balance <= 0"
                class="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 disabled:opacity-60 text-white font-bold py-3 rounded-xl transition-all shadow-md hover:shadow-lg"
              >
                <span v-if="redeemLoading">Sending request...</span>
                <span v-else-if="balance <= 0">No balance to redeem</span>
                <span v-else>Request Reward 🎁</span>
              </button>
            </form>
          </div>
        </div>

        <!-- Right column: history -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Redemption history -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 class="text-lg font-bold text-gray-800 mb-4">📜 Redemption History</h2>

            <div v-if="redemptions.length === 0" class="text-center py-8 text-gray-400">
              <div class="text-4xl mb-2">🎁</div>
              <p class="font-medium">No reward requests yet.</p>
              <p class="text-sm">Earn some points and redeem them above!</p>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="redemption in redemptions"
                :key="redemption.id"
                class="flex items-center gap-4 p-4 rounded-xl bg-gray-50 border border-gray-100"
              >
                <span class="text-3xl">🎁</span>
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">{{ redemption.description }}</div>
                  <div class="text-sm text-gray-500 mt-0.5">{{ formatDate(redemption.created_at) }}</div>
                </div>
                <div class="text-right">
                  <div class="font-bold text-indigo-700">{{ Number(redemption.amount).toFixed(2) }} pts</div>
                  <span :class="statusClass(redemption.status)" class="text-xs font-semibold px-2 py-0.5 rounded-full mt-1 inline-block">
                    {{ statusLabel(redemption.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Completed chores history -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 class="text-lg font-bold text-gray-800 mb-4">🏆 Completed Chores</h2>

            <div v-if="approvedAssignments.length === 0" class="text-center py-8 text-gray-400">
              <div class="text-4xl mb-2">🌟</div>
              <p class="font-medium">No completed chores yet.</p>
              <p class="text-sm">Complete chores to earn points!</p>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="assignment in approvedAssignments"
                :key="assignment.id"
                class="flex items-center gap-4 p-4 rounded-xl bg-green-50 border border-green-100"
              >
                <span class="text-3xl">{{ assignment.chore?.icon || '⭐' }}</span>
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">{{ assignment.chore?.title }}</div>
                  <div class="text-sm text-gray-500 mt-0.5">Approved {{ formatDate(assignment.approved_at) }}</div>
                </div>
                <div class="text-right">
                  <div class="font-bold text-green-700">+{{ Number(assignment.chore?.value || 0).toFixed(2) }} pts</div>
                  <span class="text-xs font-semibold bg-green-100 text-green-700 px-2 py-0.5 rounded-full mt-1 inline-block">Approved</span>
                </div>
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
import { useAuthStore } from '../../stores/auth.js'
import { getBalance, getRedemptions, requestRedemption, getAssignments, getMe } from '../../api/index.js'

const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const balance = ref(0)
const redemptions = ref([])
const assignments = ref([])

const redeemLoading = ref(false)
const formError = ref('')
const redeemSuccess = ref(false)

const redeemForm = ref({
  amount: '',
  description: ''
})

const approvedAssignments = computed(() =>
  assignments.value.filter(a => a.status === 'approved')
)

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function statusClass(status) {
  switch (status) {
    case 'approved': return 'bg-green-100 text-green-700'
    case 'rejected': return 'bg-red-100 text-red-700'
    case 'pending': return 'bg-amber-100 text-amber-700'
    default: return 'bg-gray-100 text-gray-600'
  }
}

function statusLabel(status) {
  switch (status) {
    case 'approved': return '✅ Approved'
    case 'rejected': return '❌ Rejected'
    case 'pending': return '⏳ Pending'
    default: return status
  }
}

async function fetchData() {
  loading.value = true
  error.value = ''
  try {
    const [balanceRes, redemptionsRes, assignmentsRes] = await Promise.all([
      getBalance(),
      getRedemptions(),
      getAssignments()
    ])
    balance.value = balanceRes.data.balance
    redemptions.value = redemptionsRes.data
    assignments.value = assignmentsRes.data
  } catch {
    error.value = 'Failed to load rewards data. Please refresh.'
  } finally {
    loading.value = false
  }
}

async function handleRedeem() {
  formError.value = ''
  redeemSuccess.value = false

  const amount = Number(redeemForm.value.amount)
  if (!amount || amount <= 0) {
    formError.value = 'Please enter a valid amount.'
    return
  }
  if (amount > balance.value) {
    formError.value = `Amount cannot exceed your balance of ${Number(balance.value).toFixed(2)} pts.`
    return
  }
  if (!redeemForm.value.description.trim()) {
    formError.value = 'Please describe what you want.'
    return
  }

  redeemLoading.value = true
  try {
    await requestRedemption(amount, redeemForm.value.description.trim())
    redeemForm.value = { amount: '', description: '' }
    redeemSuccess.value = true
    await fetchData()
    // Update user balance in auth store
    try {
      const meRes = await getMe()
      authStore.user = meRes.data
      localStorage.setItem('jobjars_user', JSON.stringify(meRes.data))
    } catch {
      // Non-critical
    }
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Failed to submit redemption request.'
  } finally {
    redeemLoading.value = false
  }
}

onMounted(fetchData)
</script>
