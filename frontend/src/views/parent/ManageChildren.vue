<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-extrabold text-gray-900">Manage Children 👨‍👩‍👧</h1>
        <p class="text-gray-500 mt-1">Add and manage your children's accounts.</p>
      </div>
      <button
        @click="openAddModal"
        class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-5 py-2.5 rounded-xl shadow-md hover:shadow-lg transition-all flex items-center gap-2"
      >
        <span class="text-lg">+</span> Add Child
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

    <!-- Children list -->
    <div v-else>
      <div v-if="children.length === 0" class="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
        <div class="text-6xl mb-4">👶</div>
        <p class="text-xl font-bold text-gray-500">No children yet</p>
        <p class="text-gray-400 mt-1">Click "Add Child" to create your first child account!</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="child in children"
          :key="child.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
        >
          <!-- Avatar + name -->
          <div class="flex items-center gap-4 mb-4">
            <div class="w-14 h-14 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white text-2xl font-bold shadow-md">
              {{ child.name.charAt(0).toUpperCase() }}
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-800">{{ child.name }}</h3>
              <p class="text-sm text-gray-500">@{{ child.username }}</p>
            </div>
          </div>

          <!-- Stats -->
          <div class="flex items-center gap-3 mb-4">
            <div class="flex-1 bg-purple-50 rounded-xl p-3 text-center">
              <div class="text-xs text-purple-500 font-medium mb-0.5">Age</div>
              <div class="text-xl font-extrabold text-purple-700">{{ child.age }}</div>
            </div>
            <div class="flex-1 bg-green-50 rounded-xl p-3 text-center">
              <div class="text-xs text-green-500 font-medium mb-0.5">Balance</div>
              <div class="text-xl font-extrabold text-green-700">💰 {{ Number(child.balance || 0).toFixed(2) }}</div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="openEditModal(child)"
              class="flex-1 text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 font-semibold py-2 rounded-xl text-sm transition-colors"
            >
              Edit
            </button>
            <button
              @click="confirmDelete(child)"
              class="flex-1 text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 font-semibold py-2 rounded-xl text-sm transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Child Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-bold text-gray-800">{{ editingChild ? 'Edit Child' : 'Add Child' }}</h2>
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

          <form @submit.prevent="saveChild" class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Name <span class="text-red-500">*</span></label>
              <input
                v-model="form.name"
                type="text"
                placeholder="e.g. Emma"
                required
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Username <span class="text-red-500">*</span></label>
              <input
                v-model="form.username"
                type="text"
                placeholder="e.g. emma123"
                required
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Password
                <span v-if="!editingChild" class="text-red-500">*</span>
                <span v-else class="text-gray-400 font-normal">(leave blank to keep current)</span>
              </label>
              <input
                v-model="form.password"
                type="password"
                :required="!editingChild"
                placeholder="Enter password"
                autocomplete="new-password"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Age <span class="text-red-500">*</span></label>
              <input
                v-model.number="form.age"
                type="number"
                min="1"
                max="18"
                placeholder="e.g. 10"
                required
                class="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
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
                <span v-else>{{ editingChild ? 'Save Changes' : 'Add Child' }}</span>
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
          <h3 class="text-lg font-bold text-gray-800">Delete Child Account?</h3>
          <p class="text-gray-500 mt-1">
            Are you sure you want to delete <strong>{{ deleteTarget.name }}</strong>'s account? This cannot be undone.
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
import { getChildren, createChild, updateChild, deleteChild } from '../../api/index.js'

const loading = ref(true)
const error = ref('')
const children = ref([])

const showModal = ref(false)
const editingChild = ref(null)
const formLoading = ref(false)
const formError = ref('')
const deleteTarget = ref(null)

const defaultForm = () => ({
  name: '',
  username: '',
  password: '',
  age: ''
})

const form = ref(defaultForm())

async function fetchChildren() {
  loading.value = true
  error.value = ''
  try {
    const res = await getChildren()
    children.value = res.data
  } catch {
    error.value = 'Failed to load children. Please refresh.'
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  editingChild.value = null
  form.value = defaultForm()
  formError.value = ''
  showModal.value = true
}

function openEditModal(child) {
  editingChild.value = child
  form.value = {
    name: child.name,
    username: child.username,
    password: '',
    age: child.age
  }
  formError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingChild.value = null
  formError.value = ''
}

async function saveChild() {
  formError.value = ''
  formLoading.value = true
  try {
    const payload = {
      name: form.value.name,
      username: form.value.username,
      age: Number(form.value.age)
    }
    if (form.value.password) {
      payload.password = form.value.password
    }
    if (!editingChild.value) {
      if (!form.value.password) {
        formError.value = 'Password is required for new child accounts.'
        formLoading.value = false
        return
      }
    }

    if (editingChild.value) {
      await updateChild(editingChild.value.id, payload)
    } else {
      await createChild(payload)
    }
    closeModal()
    await fetchChildren()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Failed to save. Please try again.'
  } finally {
    formLoading.value = false
  }
}

function confirmDelete(child) {
  deleteTarget.value = child
}

async function executeDelete() {
  formLoading.value = true
  try {
    await deleteChild(deleteTarget.value.id)
    deleteTarget.value = null
    await fetchChildren()
  } catch {
    error.value = 'Failed to delete child account.'
    deleteTarget.value = null
  } finally {
    formLoading.value = false
  }
}

onMounted(fetchChildren)
</script>
