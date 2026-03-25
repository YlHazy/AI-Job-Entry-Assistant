<template>
  <section class="page-home">
    <section class="panel hero-panel">
      <p class="kicker">Dashboard</p>
      <h2>欢迎回来，{{ appState.auth.user?.username }}</h2>
      <p class="subtle">从这里可以快速进入岗位录入、历史检索和账号配置。</p>
    </section>

    <section class="home-actions">
      <RouterLink class="action" to="/workspace">
        <span>开始录入岗位</span>
        <small>文本、链接、截图三种模式</small>
      </RouterLink>
      <RouterLink class="action" to="/history">
        <span>查看我的历史</span>
        <small>仅展示当前账号的数据</small>
      </RouterLink>
      <RouterLink class="action" to="/settings">
        <span>账号与环境</span>
        <small>查看配置和排错说明</small>
      </RouterLink>
    </section>

    <section class="stats-grid">
      <article class="panel stat-panel">
        <p class="account-label">我的岗位记录</p>
        <strong>{{ appState.bootstrap.historyCount }}</strong>
      </article>
      <article class="panel stat-panel">
        <p class="account-label">注册用户数</p>
        <strong>{{ appState.bootstrap.userCount }}</strong>
      </article>
      <article class="panel stat-panel">
        <p class="account-label">AI 模式</p>
        <strong>{{ appState.bootstrap.llmConfigured ? "Qwen" : "规则回退" }}</strong>
      </article>
    </section>
  </section>
</template>

<script setup>
import { RouterLink } from "vue-router";
import { appState } from "../state";
</script>
