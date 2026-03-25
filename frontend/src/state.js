import { reactive } from "vue";

export const appState = reactive({
  bootstrap: {
    llmConfigured: false,
    historyCount: 0
  },
  pending: {
    bootstrap: null,
    analyze: null,
    write: null,
    history: null
  },
  notices: [],
  activeTask: "",
  record: null,
  steps: [],
  duplicate: null,
  historyRows: [],
  selectedHistory: null
});

export function pushNotice(type, text, ttl = 5500) {
  const id = Date.now() + Math.random();
  appState.notices.unshift({ id, type, text });
  if (appState.notices.length > 4) {
    appState.notices.pop();
  }
  if (ttl > 0) {
    setTimeout(() => dismissNotice(id), ttl);
  }
}

export function dismissNotice(id) {
  const index = appState.notices.findIndex((item) => item.id === id);
  if (index >= 0) {
    appState.notices.splice(index, 1);
  }
}

export function startTask(name, message) {
  appState.pending[name] = Date.now();
  appState.activeTask = message || appState.activeTask;
}

export function finishTask(name) {
  appState.pending[name] = null;
  const hasPending = Object.values(appState.pending).some(Boolean);
  if (!hasPending) {
    appState.activeTask = "";
  }
}

export function isPending(name) {
  return Boolean(appState.pending[name]);
}
