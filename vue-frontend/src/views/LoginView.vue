<template>
  <main class="auth-page">
    <section class="auth-visual">
      <h1>智慧食堂</h1>
      <p>在线点餐、订单追踪与校园食堂数据分析一体化。</p>
    </section>
    <section class="auth-panel">
      <el-tabs v-model="mode" stretch>
        <el-tab-pane label="登录" name="login" />
        <el-tab-pane label="注册" name="register" />
      </el-tabs>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model.trim="form.username" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="submit">
          {{ mode === 'login' ? '登录' : '注册并登录' }}
        </el-button>
      </el-form>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { api } from '../api/http'

const router = useRouter()
const mode = ref('login')
const loading = ref(false)
const formRef = ref()
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '请输入至少 6 位密码', trigger: 'blur' }],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    if (mode.value === 'register') {
      await api.register(form)
      ElMessage.success('注册成功')
    }
    const res = await api.login(form)
    localStorage.setItem('smart_token', res.token)
    localStorage.setItem('smart_user', JSON.stringify(res.user))
    router.push(res.user?.role === 1 ? '/admin/dashboard' : '/home')
  } finally {
    loading.value = false
  }
}
</script>
