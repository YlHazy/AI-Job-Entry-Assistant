<template>
  <RouterView v-if="route.meta.authPage" />

  <div v-else class="shell">
    <aside class="sidebar">
      <div class="brand">
        <p class="brand-kicker">JOB INTAKE ASSISTANT</p>
        <h1>岗位录入助手</h1>
        <p>用清晰的流程管理岗位分析、录入和回查。</p>
      </div>

      <section class="account-card" v-if="appState.auth.user">
        <p class="account-label">当前账号</p>
        <strong>{{ appState.auth.user.username }}</strong>
        <button class="ghost-btn" :disabled="isPending('auth')" @click="handleLogout">
          退出登录
        </button>
      </section>

      <nav class="menu">
        <RouterLink to="/">总览</RouterLink>
        <RouterLink to="/workspace">岗位录入</RouterLink>
        <RouterLink to="/history">历史记录</RouterLink>
        <RouterLink to="/settings">账号与设置</RouterLink>
      </nav>

      <div class="meta">
        <p>我的记录 {{ appState.bootstrap.historyCount }}</p>
        <p>注册用户 {{ appState.bootstrap.userCount }}</p>
        <p>分析模式 {{ appState.bootstrap.llmConfigured ? "Qwen" : "规则回退" }}</p>
      </div>
    </aside>

    <div class="workspace">
      <header class="topbar">
        <div>
          <p>当前状态</p>
          <strong>{{ activeStatusText }}</strong>
        </div>
        <div class="status-chip">{{ appState.auth.user?.username || "未登录" }}</div>
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
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter, RouterLink, RouterView } from "vue-router";
import { bootstrap, fetchCurrentUser, logout } from "./lib/api";
import {
  appState,
  clearSession,
  dismissNotice,
  finishTask,
  isPending,
  markAuthReady,
  pushNotice,
  startTask
} from "./state";

const route = useRoute();
const router = useRouter();

const showBlockingLoading = computed(() => Boolean(appState.pending.analyze || appState.pending.write));

const activeStatusText = computed(() => {
  if (showBlockingLoading.value) return appState.activeTask || "处理中";
  if (appState.pending.auth) return "正在校验账号状态";
  if (appState.pending.history) return "正在刷新历史记录";
  if (appState.pending.bootstrap) return "正在载入工作区";
  return "空闲";
});

onMounted(async () => {
  window.addEventListener("auth-expired", handleAuthExpired);
  if (!appState.auth.token) {
    markAuthReady();
    if (!route.meta.authPage) {
      router.replace({ name: "login" });
    }
    return;
  }

  startTask("auth", "正在恢复登录状态");
  try {
    const authData = await fetchCurrentUser();
    appState.auth.user = authData.user;
    markAuthReady();
    await loadBootstrap();
    if (route.meta.authPage) {
      router.replace({ name: "home" });
    }
  } catch (err) {
    clearSession();
    pushNotice("error", `登录状态恢复失败：${err.message}`);
    if (!route.meta.authPage) {
      router.replace({ name: "login" });
    }
  } finally {
    finishTask("auth");
  }
});

onUnmounted(() => {
  window.removeEventListener("auth-expired", handleAuthExpired);
});

async function loadBootstrap() {
  startTask("bootstrap", "正在加载工作台信息");
  try {
    const data = await bootstrap();
    appState.bootstrap.llmConfigured = Boolean(data.llm_configured);
    appState.bootstrap.historyCount = Number(data.history_count || 0);
    appState.bootstrap.userCount = Number(data.user_count || 0);
  } catch (err) {
    pushNotice("error", `启动信息加载失败：${err.message}`);
  } finally {
    finishTask("bootstrap");
  }
}

async function handleLogout() {
  startTask("auth", "正在退出登录");
  try {
    await logout();
  } catch {
    // Even if logout request fails, we still clear local session to avoid a stuck UI.
  } finally {
    clearSession();
    finishTask("auth");
    router.replace({ name: "login" });
  }
}

function handleAuthExpired() {
  clearSession();
  pushNotice("warn", "登录状态已过期，请重新登录。");
  router.replace({ name: "login" });
}
</script>
