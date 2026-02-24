<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900">Manage Chores 📋</h1>
        <p class="text-gray-500 mt-1">Create and manage chores for your children.</p>
      </div>
      <button
        @click="openAddModal"
        class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-5 py-2.5 rounded-xl shadow-md hover:shadow-lg transition-all flex items-center gap-2"
      >
        <span class="text-lg">+</span> Add Chore
      </button>
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

    <!-- Chore list -->
    <div v-else>
      <div v-if="chores.length === 0" class="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
        <div class="text-6xl mb-4">📋</div>
        <p class="text-xl font-bold text-gray-500">No chores yet</p>
        <p class="text-gray-400 mt-1">Click "Add Chore" to create your first chore!</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="chore in chores"
          :key="chore.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3">
              <span class="text-3xl">{{ chore.icon || '⭐' }}</span>
              <div>
                <h3 class="font-bold text-gray-800">{{ chore.title }}</h3>
                <p class="text-sm text-gray-500 mt-0.5 line-clamp-2">{{ chore.description }}</p>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 mb-4">
            <span
              :class="chore.chore_type === 'repetitive' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'"
              class="text-xs font-semibold px-2.5 py-1 rounded-full"
            >
              {{ chore.chore_type === 'repetitive' ? '🔄 Repetitive' : '1️⃣ One-Time' }}
            </span>
            <span class="bg-green-100 text-green-700 text-xs font-semibold px-2.5 py-1 rounded-full">
              💰 {{ Number(chore.value).toFixed(2) }} pts
            </span>
            <span class="bg-gray-100 text-gray-600 text-xs font-semibold px-2.5 py-1 rounded-full">
              Ages {{ chore.age_min }}{{ chore.age_max ? `–${chore.age_max}` : '+' }}
            </span>
          </div>

          <div class="flex items-center justify-between">
            <!-- Active toggle -->
            <div class="flex items-center gap-2">
              <button
                @click="toggleActive(chore)"
                :class="chore.is_active ? 'bg-green-500' : 'bg-gray-300'"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
              >
                <span
                  :class="chore.is_active ? 'translate-x-6' : 'translate-x-1'"
                  class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm"
                ></span>
              </button>
              <span class="text-sm font-medium" :class="chore.is_active ? 'text-green-600' : 'text-gray-400'">
                {{ chore.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>

            <!-- Actions -->
            <div class="flex gap-2">
              <button
                @click="openEditModal(chore)"
                class="text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              >
                Edit
              </button>
              <button
                @click="confirmDelete(chore)"
                class="text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chore Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-screen overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-800">{{ editingChore ? 'Edit Chore' : 'Add New Chore' }}</h2>
            <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Form error -->
          <div v-if="formError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-4 text-sm">
            {{ formError }}
          </div>

          <form @submit.prevent="saveChore" class="space-y-4">
            <!-- Icon + Title row -->
            <div class="flex gap-3">
              <div class="w-24">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Icon</label>
                <input
                  v-model="form.icon"
                  type="text"
                  placeholder="⭐"
                  maxlength="4"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400 text-2xl text-center"
                />
              </div>
              <div class="flex-1">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Title <span class="text-red-500">*</span></label>
                <input
                  v-model="form.title"
                  type="text"
                  placeholder="e.g. Wash the dishes"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Description</label>
              <textarea
                v-model="form.description"
                rows="2"
                placeholder="Describe what needs to be done..."
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Reward Value (points) <span class="text-red-500">*</span></label>
              <input
                v-model.number="form.value"
                type="number"
                min="0.01"
                step="0.01"
                placeholder="5.00"
                required
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">Chore Type <span class="text-red-500">*</span></label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="form.chore_type" value="one-time" class="text-indigo-600" />
                  <span class="font-medium text-gray-700">1️⃣ One-Time</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" v-model="form.chore_type" value="repetitive" class="text-indigo-600" />
                  <span class="font-medium text-gray-700">🔄 Repetitive</span>
                </label>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="flex-1">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Min Age <span class="text-red-500">*</span></label>
                <input
                  v-model.number="form.age_min"
                  type="number"
                  min="1"
                  max="18"
                  placeholder="5"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
              <div class="flex-1">
                <label class="block text-sm font-semibold text-gray-700 mb-1">Max Age <span class="text-gray-400">(optional)</span></label>
                <input
                  v-model.number="form.age_max"
                  type="number"
                  min="1"
                  max="18"
                  placeholder="18"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
            </div>

            <div class="flex items-center gap-3 pt-1">
              <button
                type="button"
                @click="form.is_active = !form.is_active"
                :class="form.is_active ? 'bg-green-500' : 'bg-gray-300'"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
              >
                <span
                  :class="form.is_active ? 'translate-x-6' : 'translate-x-1'"
                  class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow-sm"
                ></span>
              </button>
              <span class="text-sm font-medium text-gray-700">Active (visible to children)</span>
            </div>

            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="closeModal"
                class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2.5 rounded-xl transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="formLoading"
                class="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold py-2.5 rounded-xl transition-colors"
              >
                <span v-if="formLoading">Saving...</span>
                <span v-else>{{ editingChore ? 'Save Changes' : 'Create Chore' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete confirm modal -->
    <div v-if="deleteTarget" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div class="text-center mb-5">
          <div class="text-4xl mb-3">🗑️</div>
          <h3 class="text-lg font-bold text-gray-800">Delete Chore?</h3>
          <p class="text-gray-500 mt-1">
            Are you sure you want to delete <strong>"{{ deleteTarget.title }}"</strong>? This cannot be undone.
          </p>
        </div>
        <div class="flex gap-3">
          <button @click="deleteTarget = null" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2.5 rounded-xl transition-colors">
            Cancel
          </button>
          <button @click="executeDelete" :disabled="formLoading" class="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-semibold py-2.5 rounded-xl transition-colors">
            <span v-if="formLoading">Deleting...</span>
            <span v-else>Delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getChores, createChore, updateChore, deleteChore } from '../../api/index.js'

const loading = ref(true)
const error = ref('')
const chores = ref([])

const showModal = ref(false)
const editingChore = ref(null)
const formLoading = ref(false)
const formError = ref('')
const deleteTarget = ref(null)

const defaultForm = () => ({
  title: '',
  description: '',
  icon: '⭐',
  value: '',
  chore_type: 'one-time',
  age_min: 5,
  age_max: '',
  is_active: true
})

const form = ref(defaultForm())

async function fetchChores() {
  loading.value = true
  error.value = ''
  try {
    const res = await getChores()
    chores.value = res.data
  } catch {
    error.value = 'Failed to load chores. Please refresh.'
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  editingChore.value = null
  form.value = defaultForm()
  formError.value = ''
  showModal.value = true
}

function openEditModal(chore) {
  editingChore.value = chore
  form.value = {
    title: chore.title,
    description: chore.description || '',
    icon: chore.icon || '⭐',
    value: chore.value,
    chore_type: chore.chore_type,
    age_min: chore.age_min,
    age_max: chore.age_max || '',
    is_active: chore.is_active
  }
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingChore.value = null
  formError.value = ''
}

async function saveChore() {
  formError.value = ''
  formLoading.value = true
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      icon: form.value.icon || '⭐',
      value: Number(form.value.value),
      chore_type: form.value.chore_type,
      age_min: Number(form.value.age_min),
      age_max: form.value.age_max ? Number(form.value.age_max) : null,
      is_active: form.value.is_active
    }

    if (editingChore.value) {
      await updateChore(editingChore.value.id, payload)
    } else {
      await createChore(payload)
    }
    closeModal()
    await fetchChores()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Failed to save chore. Please try again.'
  } finally {
    formLoading.value = false
  }
}

async function toggleActive(chore) {
  try {
    await updateChore(chore.id, { is_active: !chore.is_active })
    chore.is_active = !chore.is_active
  } catch {
    error.value = 'Failed to update chore status.'
  }
}

function confirmDelete(chore) {
  deleteTarget.value = chore
}

async function executeDelete() {
  formLoading.value = true
  try {
    await deleteChore(deleteTarget.value.id)
    deleteTarget.value = null
    await fetchChores()
  } catch {
    error.value = 'Failed to delete chore. Please try again.'
    deleteTarget.value = null
  } finally {
    formLoading.value = false
  }
}

onMounted(fetchChores)
</script>
