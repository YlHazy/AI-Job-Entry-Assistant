<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <p class="brand-kicker">JOB INTAKE ASSISTANT</p>
        <h1>岗位录入助手</h1>
        <p>把岗位信息变成可追踪、可回查、可复用的数据。</p>
      </div>

      <nav class="menu">
        <RouterLink to="/">总览</RouterLink>
        <RouterLink to="/workspace">工作台</RouterLink>
        <RouterLink to="/history">历史库</RouterLink>
        <RouterLink to="/settings">设置</RouterLink>
      </nav>

      <div class="meta">
        <p>历史记录 {{ appState.bootstrap.historyCount }}</p>
        <p>分析模式 {{ appState.bootstrap.llmConfigured ? "Qwen" : "规则回退" }}</p>
      </div>
    </aside>

    <div class="workspace">
      <header class="topbar">
        <p>当前状态</p>
        <strong>{{ activeStatusText }}</strong>
      </header>

      <section class="notice-stack">
        <article
          v-for="notice in appState.notices"
          :key="notice.id"
          class="notice"
          :class="`notice-${notice.type}`"
          @click="dismissNotice(notice.id)"
        >
          {{ notice.text }}
        </article>
      </section>

      <main class="view-frame">
        <RouterView v-slot="{ Component }">
          <Transition name="view-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <Transition name="fade">
      <div v-if="showBlockingLoading" class="loading-overlay">
        <div class="loading-card">
          <div class="spinner"></div>
          <p>{{ appState.activeTask || "处理中..." }}</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { RouterLink, RouterView } from "vue-router";
import { bootstrap } from "./lib/api";
import { appState, dismissNotice, finishTask, pushNotice, startTask } from "./state";

const showBlockingLoading = computed(() => Boolean(appState.pending.analyze || appState.pending.write));

const activeStatusText = computed(() => {
  if (showBlockingLoading.value) {
    return appState.activeTask || "处理中";
  }
  if (appState.pending.history) {
    return "正在刷新历史记录";
  }
  if (appState.pending.bootstrap) {
    return "正在初始化";
  }
  return "空闲";
});

onMounted(async () => {
  startTask("bootstrap", "正在加载启动信息");
  try {
    const data = await bootstrap();
    appState.bootstrap.llmConfigured = Boolean(data.llm_configured);
    appState.bootstrap.historyCount = Number(data.history_count || 0);
  } catch (err) {
    pushNotice("error", `启动信息加载失败：${err.message}`);
  } finally {
    finishTask("bootstrap");
  }
});
</script>
