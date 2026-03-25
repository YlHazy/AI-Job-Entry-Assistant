<template>
  <section class="page-history">
    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">History</p>
          <h2>历史检索</h2>
        </div>
        <span class="badge" v-if="isHistoryPending">加载中</span>
      </header>

      <div class="form-grid">
        <label>
          关键词
          <input v-model.trim="filters.query" placeholder="公司 / 岗位 / 备注" />
        </label>
        <label>
          优先级
          <select v-model="filters.priority">
            <option value="">全部</option>
            <option value="高">高</option>
            <option value="中">中</option>
            <option value="低">低</option>
          </select>
        </label>
        <label>
          方向
          <select v-model="filters.matchDirection">
            <option value="">全部</option>
            <option value="AI Agent 开发">AI Agent 开发</option>
            <option value="AI 产品">AI 产品</option>
            <option value="双向都可">双向都可</option>
            <option value="不推荐">不推荐</option>
          </select>
        </label>
      </div>

      <div class="action-row">
        <button class="btn-primary" :disabled="isHistoryPending" @click="loadHistory">
          {{ isHistoryPending ? "查询中..." : "查询历史" }}
        </button>
      </div>
    </section>

    <section class="panel">
      <header class="section-head">
        <h2>结果列表</h2>
        <p class="subtle">共 {{ appState.historyRows.length }} 条</p>
      </header>

      <p v-if="!appState.historyRows.length && !isHistoryPending" class="subtle">暂无记录。</p>
      <div class="table-wrap" v-else>
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>公司</th>
              <th>岗位</th>
              <th>方向</th>
              <th>优先级</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in appState.historyRows"
              :key="row.id"
              :class="{ selected: appState.selectedHistory?.id === row.id }"
              @click="loadDetail(row.id)"
            >
              <td>{{ row.id }}</td>
              <td>{{ row.company }}</td>
              <td>{{ row.job_title }}</td>
              <td>{{ row.match_direction }}</td>
              <td>{{ row.priority }}</td>
              <td>{{ row.created_at }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel" v-if="appState.selectedHistory">
      <header class="section-head">
        <h2>记录详情 #{{ appState.selectedHistory.id }}</h2>
      </header>
      <pre>{{ appState.selectedHistory }}</pre>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive } from "vue";
import { getHistoryDetail, searchHistory } from "../lib/api";
import { appState, finishTask, isPending, pushNotice, startTask } from "../state";

const filters = reactive({
  query: "",
  priority: "",
  matchDirection: ""
});

const isHistoryPending = computed(() => isPending("history"));

onMounted(loadHistory);

async function loadHistory() {
  if (isHistoryPending.value) return;
  startTask("history", "正在查询历史记录");
  try {
    const data = await searchHistory(filters);
    appState.historyRows = data.rows || [];
  } catch (err) {
    pushNotice("error", err.message);
  } finally {
    finishTask("history");
  }
}

async function loadDetail(id) {
  try {
    const data = await getHistoryDetail(id);
    appState.selectedHistory = data.row;
  } catch (err) {
    pushNotice("error", err.message);
  }
}
</script>
