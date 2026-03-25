import { reactive } from "vue";
import { getStoredAuthToken, setAuthToken } from "./lib/api";

export const appState = reactive({
  auth: {
    token: getStoredAuthToken(),
    user: null,
    ready: false
  },
  bootstrap: {
    llmConfigured: false,
    historyCount: 0,
    userCount: 0
  },
  pending: {
    bootstrap: null,
    analyze: null,
    write: null,
    history: null,
    auth: null
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

export function setSession(token, user) {
  appState.auth.token = token || "";
  appState.auth.user = user || null;
  appState.auth.ready = true;
  setAuthToken(appState.auth.token);
}

export function clearSession() {
  appState.auth.token = "";
  appState.auth.user = null;
  appState.auth.ready = true;
  resetWorkspaceState();
  setAuthToken("");
}

export function markAuthReady() {
  appState.auth.ready = true;
}

export function resetWorkspaceState() {
  appState.bootstrap.llmConfigured = false;
  appState.bootstrap.historyCount = 0;
  appState.bootstrap.userCount = 0;
  appState.record = null;
  appState.steps = [];
  appState.duplicate = null;
  appState.historyRows = [];
  appState.selectedHistory = null;
}
