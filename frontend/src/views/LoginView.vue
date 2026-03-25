<template>
  <section class="auth-shell">
    <div class="auth-hero">
      <p class="kicker">Secure Workspace</p>
      <h1>先登录，再进入你的岗位工作台</h1>
      <p class="subtle">
        每个账号拥有独立的岗位历史记录和检索结果，避免不同用户之间的数据混用。
      </p>
    </div>

    <div class="auth-panel">
      <div class="tab-row">
        <button :class="['tab-btn', { active: mode === 'login' }]" @click="mode = 'login'">登录</button>
        <button :class="['tab-btn', { active: mode === 'register' }]" @click="mode = 'register'">注册</button>
      </div>

      <label>
        用户名
        <input v-model.trim="form.username" placeholder="至少 3 个字符" />
      </label>

      <label>
        密码
        <input v-model="form.password" type="password" placeholder="至少 6 个字符" />
      </label>

      <div class="action-row">
        <button class="btn-primary" :disabled="isPending('auth')" @click="submit">
          {{ isPending("auth") ? "处理中..." : mode === "login" ? "登录并进入" : "注册并进入" }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { bootstrap, login, register } from "../lib/api";
import { appState, finishTask, isPending, pushNotice, setSession, startTask } from "../state";

const router = useRouter();
const mode = ref("login");
const form = reactive({
  username: "",
  password: ""
});

async function submit() {
  startTask("auth", mode.value === "login" ? "正在登录账号" : "正在注册账号");
  try {
    const action = mode.value === "login" ? login : register;
    const authData = await action({
      username: form.username,
      password: form.password
    });
    setSession(authData.token, authData.user);

    const data = await bootstrap();
    appState.bootstrap.llmConfigured = Boolean(data.llm_configured);
    appState.bootstrap.historyCount = Number(data.history_count || 0);
    appState.bootstrap.userCount = Number(data.user_count || 0);

    pushNotice("success", mode.value === "login" ? "登录成功。" : "注册成功，已进入工作台。");
    router.replace({ name: "home" });
  } catch (err) {
    const tips = err.payload?.suggestions?.length ? ` 建议：${err.payload.suggestions.join("；")}` : "";
    pushNotice("error", `${err.message}${tips}`);
  } finally {
    finishTask("auth");
  }
}
</script>
