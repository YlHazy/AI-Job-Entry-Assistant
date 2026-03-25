<template>
  <section class="page-settings">
    <section class="panel">
      <header class="section-head">
        <div>
          <p class="kicker">Settings</p>
          <h2>环境与排错说明</h2>
        </div>
      </header>
      <p class="subtle">
        前端不会保存你的个人路径。Excel 路径在写入时临时输入，支持中文路径和被引号包裹的粘贴格式。
      </p>
    </section>

    <section class="panel">
      <h3>环境变量</h3>
      <pre>OPENAI_API_KEY=你的百炼 API Key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
JOB_AGENT_MODEL=qwen-plus</pre>
    </section>

    <section class="panel">
      <h3>常见失败原因</h3>
      <ul class="flat-list">
        <li>写入失败：目标 Excel 正在被 Excel/WPS 占用。</li>
        <li>链接抓取失败：目标站点登录限制或反爬策略导致内容不可达。</li>
        <li>OCR 失败：本地缺少 Tesseract OCR 引擎。</li>
      </ul>
    </section>
  </section>
</template>
