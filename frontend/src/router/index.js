import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/", name: "home", component: () => import("../views/HomeView.vue") },
  { path: "/workspace", name: "workspace", component: () => import("../views/WorkspaceView.vue") },
  { path: "/history", name: "history", component: () => import("../views/HistoryView.vue") },
  { path: "/settings", name: "settings", component: () => import("../views/SettingsView.vue") }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
