import { reactive, computed } from 'vue'

const state = reactive({
  items: JSON.parse(localStorage.getItem('smart_cart') || '[]'),
})

function persist() {
  localStorage.setItem('smart_cart', JSON.stringify(state.items))
}

export function useCart() {
  const totalCount = computed(() => state.items.reduce((sum, item) => sum + item.quantity, 0))
  const totalAmount = computed(() =>
    state.items.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0),
  )

  function add(dish, quantity = 1) {
    const current = state.items.find((item) => item.id === dish.id)
    if (current) current.quantity += quantity
    else state.items.push({ ...dish, quantity })
    persist()
  }

  function update(id, quantity) {
    const item = state.items.find((entry) => entry.id === id)
    if (item) item.quantity = quantity
    state.items = state.items.filter((entry) => entry.quantity > 0)
    persist()
  }

  function remove(id) {
    state.items = state.items.filter((item) => item.id !== id)
    persist()
  }

  function clear() {
    state.items = []
    persist()
  }

  return { state, totalCount, totalAmount, add, update, remove, clear }
}
