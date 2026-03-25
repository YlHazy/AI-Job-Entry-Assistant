<template>
  <section class="panel page-home">
    <header>
      <p class="kicker">Overview</p>
      <h2>更顺滑的岗位录入工作流</h2>
      <p class="subtle">
        输入岗位内容，自动结构化分析，必要时人工校正，再写入任意格式的 Excel 看板。
      </p>
    </header>

    <div class="home-actions">
      <RouterLink class="action" to="/workspace">
        <span>开始分析岗位</span>
        <small>文本 / 链接 / 截图</small>
      </RouterLink>
      <RouterLink class="action" to="/history">
        <span>查看历史记录</span>
        <small>搜索和去重回查</small>
      </RouterLink>
      <RouterLink class="action" to="/settings">
        <span>查看配置说明</span>
        <small>环境变量和排错指南</small>
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from "vue-router";
</script>
