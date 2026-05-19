<template>
  <el-card class="table-card">
    <div class="toolbar">
      <h2 class="section-title">分类管理</h2>
      <el-button type="primary" :icon="Plus" @click="open()">新增分类</el-button>
    </div>
    <el-table v-loading="loading" :data="categories">
      <el-table-column prop="id" label="ID" width="90" />
      <el-table-column prop="name" label="分类名称" />
      <el-table-column prop="sort" label="排序" width="100" />
      <el-table-column width="150">
        <template #default="{ row }">
          <el-button link type="primary" @click="open(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="visible" :title="form.id ? '编辑分类' : '新增分类'" width="420px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="visible = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { api } from '../../api/http'

const loading = ref(false)
const visible = ref(false)
const categories = ref([])
const form = reactive({ id: null, name: '', sort: 0 })
const demoCategories = [
  { id: 1, name: '主食套餐', sort: 1 },
  { id: 2, name: '热炒小碗', sort: 2 },
  { id: 3, name: '汤粉面', sort: 3 },
  { id: 4, name: '饮品小吃', sort: 4 },
]

async function load() {
  loading.value = true
  try {
    const records = await api.categories()
    categories.value = records.length ? records : demoCategories
  } catch {
    categories.value = demoCategories
  } finally {
    loading.value = false
  }
}

function open(row = {}) {
  Object.assign(form, { id: row.id || null, name: row.name || '', sort: row.sort || 0 })
  visible.value = true
}

async function save() {
  if (form.id) await api.updateCategory(form)
  else await api.saveCategory(form)
  visible.value = false
  await load()
}

async function remove(id) {
  await ElMessageBox.confirm('确认删除该分类？', '删除分类', { type: 'warning' })
  await api.deleteCategory(id)
  await load()
}

onMounted(load)
</script>
