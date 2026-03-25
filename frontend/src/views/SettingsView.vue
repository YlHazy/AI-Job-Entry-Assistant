<template>
  <section class="page-settings">
    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">Account</p>
          <h2>账号与工作区说明</h2>
        </div>
      </header>
      <p class="subtle">当前登录账号：{{ appState.auth.user?.username }}</p>
      <p class="subtle">岗位历史记录、去重判断和统计都按当前用户隔离。</p>
    </section>

    <section class="panel">
      <h3>环境变量</h3>
      <pre>OPENAI_API_KEY=你的百炼 API Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JOB_AGENT_MODEL=qwen-plus</pre>
    </section>

    <section class="panel">
      <h3>数据与隐私</h3>
      <ul class="flat-list">
        <li>前端不会默认保存你的 Excel 路径。</li>
        <li>历史记录只对当前登录用户可见。</li>
        <li>写入 Excel 仍然由你手动指定目标路径。</li>
      </ul>
    </section>

    <section class="panel">
      <h3>常见失败原因</h3>
      <ul class="flat-list">
        <li>写入失败：目标 Excel 正在被 Excel 或 WPS 占用。</li>
        <li>链接抓取失败：目标站点登录限制或反爬策略导致内容不可达。</li>
        <li>OCR 失败：本地缺少 Tesseract OCR 引擎。</li>
        <li>鉴权失败：登录过期或 token 失效，需要重新登录。</li>
      </ul>
    </section>
  </section>
</template>

<script setup>
import { appState } from "../state";
</script>
