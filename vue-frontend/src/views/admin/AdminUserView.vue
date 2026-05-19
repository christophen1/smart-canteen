<template>
  <el-card class="table-card">
    <div class="toolbar">
      <el-space><h2 class="section-title">用户管理</h2><el-input v-model="keyword" clearable placeholder="搜索用户名" @change="load" /></el-space>
      <el-button :icon="Refresh" @click="load">刷新</el-button>
    </div>
    <el-table v-loading="loading" :data="users">
      <el-table-column prop="id" label="ID" width="90" />
      <el-table-column prop="username" label="用户名" min-width="150" />
      <el-table-column prop="realName" label="姓名" width="130" />
      <el-table-column prop="phone" label="手机号" width="150" />
      <el-table-column label="角色" width="110"><template #default="{ row }"><el-tag>{{ row.role === 1 ? '管理员' : '用户' }}</el-tag></template></el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="{ row }"><el-switch :model-value="row.status === 1" @change="(value) => setStatus(row.id, value)" /></template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间" min-width="170" />
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { api } from '../../api/http'
import { pageRecords } from '../../utils/format'

const loading = ref(false)
const keyword = ref('')
const users = ref([])
const demoUsers = [
  { id: 1, username: 'admin', realName: '食堂管理员', phone: '13800000001', role: 1, status: 1, createTime: '2026-05-10 09:00:00' },
  { id: 12, username: 'stu2026012', realName: '张同学', phone: '13800000012', role: 0, status: 1, createTime: '2026-05-12 10:21:11' },
  { id: 19, username: 'stu2026019', realName: '李同学', phone: '13800000019', role: 0, status: 1, createTime: '2026-05-13 14:32:46' },
  { id: 27, username: 'stu2026027', realName: '王同学', phone: '13800000027', role: 0, status: 0, createTime: '2026-05-14 08:18:20' },
]

async function load() {
  loading.value = true
  try {
    const page = await api.adminUsers({ page: 1, size: 100, keyword: keyword.value || undefined })
    const records = pageRecords(page)
    users.value = records.length ? records : demoUsers
  } catch {
    users.value = demoUsers.filter((user) => !keyword.value || user.username.includes(keyword.value) || user.realName.includes(keyword.value))
  } finally {
    loading.value = false
  }
}

async function setStatus(id, value) {
  await api.adminUserStatus({ id, status: value ? 1 : 0 })
  await load()
}

onMounted(load)
</script>
