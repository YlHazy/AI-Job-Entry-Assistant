<template>
  <section class="page-workspace">
    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">Input</p>
          <h2>岗位分析输入</h2>
        </div>
        <span class="badge" v-if="isAnalyzePending">分析中</span>
      </header>

      <div class="tab-row">
        <button
          v-for="option in modes"
          :key="option"
          :class="['tab-btn', { active: form.mode === option }]"
          :disabled="isAnalyzePending"
          @click="form.mode = option"
        >
          {{ modeLabels[option] }}
        </button>
      </div>

      <div class="form-grid">
        <label>
          来源平台
          <input v-model.trim="form.sourcePlatform" placeholder="例如：BOSS 直聘、官网、公众号" />
        </label>
        <label>
          来源链接（可选）
          <input v-model="form.sourceUrl" placeholder="支持中文路径与带引号粘贴" />
        </label>
      </div>

      <label v-if="form.mode === 'text'">
        JD 文本
        <textarea v-model="form.rawText" rows="8" placeholder="粘贴岗位 JD 原文"></textarea>
      </label>

      <label v-if="form.mode === 'url'">
        岗位链接
        <input v-model="form.sourceUrl" placeholder="https://..." />
      </label>

      <label v-if="form.mode === 'image'">
        岗位截图
        <input type="file" accept="image/*" :disabled="isAnalyzePending" @change="onFileChange" />
      </label>

      <div class="action-row">
        <button class="btn-primary" :disabled="isAnalyzePending" @click="submitAnalyze">
          {{ isAnalyzePending ? "正在分析..." : "开始分析" }}
        </button>
      </div>
    </section>

    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">Result</p>
          <h2>结构化结果</h2>
        </div>
        <span class="badge" v-if="appState.duplicate?.is_duplicate">疑似重复</span>
      </header>

      <p v-if="!appState.record" class="subtle">分析后可在这里二次编辑字段。</p>
      <template v-else>
        <div class="form-grid">
          <label>公司<input v-model="appState.record.company" /></label>
          <label>岗位名称<input v-model="appState.record.job_title" /></label>
          <label>岗位类别<input v-model="appState.record.role_category" /></label>
          <label>方向<input v-model="appState.record.match_direction" /></label>
          <label>地点<input v-model="appState.record.location" /></label>
          <label>优先级<input v-model="appState.record.priority" /></label>
        </div>
        <label>主要差距<textarea v-model="appState.record.main_gap" rows="3"></textarea></label>
        <label>摘要备注<textarea v-model="appState.record.short_note" rows="3"></textarea></label>
      </template>
    </section>

    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">Write</p>
          <h2>写入 Excel</h2>
        </div>
        <span class="badge" v-if="isWritePending">写入中</span>
      </header>
      <div class="form-grid">
        <label>
          Excel 路径
          <input v-model="writeForm.excelPath" placeholder="例如：D:\求职\Day1_求职看板.xlsx" />
        </label>
        <label>
          Sheet 名称（可选）
          <input v-model="writeForm.sheetName" placeholder="留空自动识别" />
        </label>
      </div>
      <div class="action-row">
        <button class="btn-primary" :disabled="isWritePending || !appState.record" @click="submitWrite">
          {{ isWritePending ? "写入中..." : "写入 Excel" }}
        </button>
      </div>
    </section>

    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">Trace</p>
          <h2>执行轨迹</h2>
        </div>
      </header>
      <p v-if="!appState.steps.length" class="subtle">暂无轨迹，开始分析后会显示每一步执行结果。</p>
      <details v-for="(step, idx) in appState.steps" :key="idx" class="trace-item">
        <summary>{{ idx + 1 }}. {{ step.name }}</summary>
        <p>{{ step.summary }}</p>
        <pre>{{ step.output }}</pre>
      </details>
    </section>
  </section>
</template>

<script setup>
import { computed, reactive } from "vue";
import { analyze, writeExcel } from "../lib/api";
import { appState, finishTask, isPending, pushNotice, startTask } from "../state";

const modes = ["text", "url", "image"];
const modeLabels = { text: "文本", url: "链接", image: "截图" };

const form = reactive({
  mode: "text",
  sourcePlatform: "",
  sourceUrl: "",
  rawText: "",
  imageFile: null
});

const writeForm = reactive({
  excelPath: "",
  sheetName: ""
});

const isAnalyzePending = computed(() => isPending("analyze"));
const isWritePending = computed(() => isPending("write"));

function onFileChange(event) {
  form.imageFile = event.target.files?.[0] || null;
}

async function submitAnalyze() {
  if (isAnalyzePending.value) return;
  startTask("analyze", "正在分析岗位信息");
  try {
    const data = await analyze({
      mode: form.mode,
      sourcePlatform: form.sourcePlatform,
      sourceUrl: form.sourceUrl,
      rawText: form.rawText,
      imageFile: form.imageFile
    });
    appState.record = data.record;
    appState.steps = data.steps || [];
    appState.duplicate = data.duplicate || null;
    if (appState.duplicate?.is_duplicate) {
      pushNotice("warn", `检测到疑似重复：${appState.duplicate.reason || "请检查历史记录"}`);
    } else {
      pushNotice("success", "分析完成，已生成结构化结果。");
    }
  } catch (err) {
    const tips = err.payload?.suggestions?.length ? ` 建议：${err.payload.suggestions.join("；")}` : "";
    pushNotice("error", `${err.message}${tips}`);
  } finally {
    finishTask("analyze");
  }
}

async function submitWrite() {
  if (isWritePending.value) return;
  if (!appState.record) {
    pushNotice("error", "没有可写入的数据，请先完成分析。");
    return;
  }
  startTask("write", "正在写入 Excel");
  try {
    const data = await writeExcel({
      record: appState.record,
      excel_path: writeForm.excelPath,
      sheet_name: writeForm.sheetName
    });
    pushNotice("success", `写入成功：${data.saved_path}`);
    appState.bootstrap.historyCount += 1;
  } catch (err) {
    const tips = err.payload?.suggestions?.length ? ` 建议：${err.payload.suggestions.join("；")}` : "";
    pushNotice("error", `${err.message}${tips}`);
  } finally {
    finishTask("write");
  }
}
</script>
