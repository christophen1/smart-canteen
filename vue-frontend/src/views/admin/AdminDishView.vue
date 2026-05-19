<template>
  <el-card class="table-card">
    <div class="toolbar">
      <el-space><h2 class="section-title">菜品管理</h2><el-input v-model="keyword" placeholder="搜索菜品" clearable @change="load" /></el-space>
      <el-button type="primary" :icon="Plus" @click="open()">新增菜品</el-button>
    </div>
    <el-table v-loading="loading" :data="dishes">
      <el-table-column prop="name" label="菜品" min-width="150" />
      <el-table-column prop="categoryName" label="分类" width="120" />
      <el-table-column label="价格" width="110"><template #default="{ row }">{{ money(row.price) }}</template></el-table-column>
      <el-table-column label="状态" width="110"><template #default="{ row }"><el-switch :model-value="row.status === 1" @change="(v) => setStatus(row, v)" /></template></el-table-column>
      <el-table-column width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="visible" :title="form.id ? '编辑菜品' : '新增菜品'" width="560px">
      <el-form :model="form" label-width="86px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类"><el-select v-model="form.categoryId" style="width: 100%"><el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" /></el-select></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="图片"><el-input v-model="form.image" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="上架"><el-switch v-model="isOn" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="visible = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api } from '../../api/http'
import { money, pageRecords } from '../../utils/format'

const loading = ref(false)
const visible = ref(false)
const keyword = ref('')
const dishes = ref([])
const categories = ref([])
const form = reactive({ id: null, name: '', categoryId: null, price: 0, image: '', description: '', status: 1 })
const isOn = computed({ get: () => form.status === 1, set: (value) => (form.status = value ? 1 : 0) })

async function load() {
  loading.value = true
  try {
    const page = await api.adminDishes({ page: 1, size: 100, keyword: keyword.value || undefined })
    dishes.value = pageRecords(page)
  } catch {
    dishes.value = []
  } finally {
    loading.value = false
  }
}

function open(row = {}) {
  Object.assign(form, { id: row.id || null, name: row.name || '', categoryId: row.categoryId || null, price: Number(row.price || 0), image: row.image || '', description: row.description || '', status: row.status ?? 1 })
  visible.value = true
}

async function save() {
  if (form.id) await api.updateDish(form)
  else await api.saveDish(form)
  visible.value = false
  await load()
}

async function setStatus(row, value) {
  await api.dishStatus({ id: row.id, status: value ? 1 : 0 })
  await load()
}

async function remove(id) {
  await ElMessageBox.confirm('确认删除该菜品？', '删除菜品', { type: 'warning' })
  await api.deleteDish(id)
  await load()
}

onMounted(async () => {
  try {
    categories.value = await api.categories()
  } catch {
    categories.value = []
  }
  await load()
})
</script>
