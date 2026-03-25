import { createRouter, createWebHistory } from "vue-router";
import { getStoredAuthToken } from "../lib/api";

const routes = [
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: { guestOnly: true, authPage: true }
  },
  { path: "/", name: "home", component: () => import("../views/HomeView.vue"), meta: { requiresAuth: true } },
  {
    path: "/workspace",
    name: "workspace",
    component: () => import("../views/WorkspaceView.vue"),
    meta: { requiresAuth: true }
  },
  {
    path: "/history",
    name: "history",
    component: () => import("../views/HistoryView.vue"),
    meta: { requiresAuth: true }
  },
  {
    path: "/settings",
    name: "settings",
    component: () => import("../views/SettingsView.vue"),
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const hasToken = Boolean(getStoredAuthToken());
  if (to.meta.requiresAuth && !hasToken) {
    return { name: "login" };
  }
  if (to.meta.guestOnly && hasToken) {
    return { name: "home" };
  }
  return true;
});

export default router;
