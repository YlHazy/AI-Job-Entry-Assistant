const REQUEST_TIMEOUT_MS = 20000;
const TOKEN_KEY = "job-intake-token";

let authToken = window.localStorage.getItem(TOKEN_KEY) || "";

function toApiError(payload, fallbackMessage) {
  if (payload?.error?.message) {
    const err = new Error(payload.error.message);
    err.payload = payload.error;
    err.requestId = payload.request_id || "";
    return err;
  }
  const err = new Error(fallbackMessage);
  err.payload = payload?.error || { code: "UNKNOWN", message: fallbackMessage, suggestions: [] };
  err.requestId = payload?.request_id || "";
  return err;
}

function buildHeaders(headers = {}, withAuth = true) {
  const nextHeaders = new Headers(headers);
  if (withAuth && authToken) {
    nextHeaders.set("Authorization", `Bearer ${authToken}`);
  }
  return nextHeaders;
}

function notifyAuthExpired() {
  setAuthToken("");
  window.dispatchEvent(new CustomEvent("auth-expired"));
}

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const rawText = await response.text();
  let payload = null;

  if (contentType.includes("application/json")) {
    try {
      payload = JSON.parse(rawText);
    } catch {
      throw new Error(`后端 JSON 解析失败（HTTP ${response.status}）。`);
    }
  } else {
    const snippet = (rawText || "").replace(/\s+/g, " ").trim().slice(0, 140);
    throw new Error(
      `后端返回了非 JSON 响应（HTTP ${response.status}，Content-Type: ${contentType || "unknown"}）。` +
      `${snippet ? ` 响应片段：${snippet}` : ""}`
    );
  }

  if (!response.ok || !payload.ok) {
    throw toApiError(payload, "请求失败，请稍后重试。");
  }
  return payload.data;
}

async function request(url, init = {}, options = {}) {
  const { timeoutMs = REQUEST_TIMEOUT_MS, withAuth = true } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...init,
      headers: buildHeaders(init.headers, withAuth),
      signal: controller.signal
    });
    return await parseResponse(response);
  } catch (error) {
    if (error.payload?.code === "UNAUTHORIZED") {
      notifyAuthExpired();
    }
    if (error.name === "AbortError") {
      throw new Error("请求超时，请检查网络或稍后重试。");
    }
    if (error.payload) {
      throw error;
    }
    throw new Error(`网络请求失败：${error.message || "未知错误"}`);
  } finally {
    clearTimeout(timer);
  }
}

export function getStoredAuthToken() {
  return authToken;
}

export function setAuthToken(token) {
  authToken = token || "";
  if (authToken) {
    window.localStorage.setItem(TOKEN_KEY, authToken);
  } else {
    window.localStorage.removeItem(TOKEN_KEY);
  }
}

export async function register(payload) {
  return request(
    "/api/auth/register",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    },
    { withAuth: false }
  );
}

export async function login(payload) {
  return request(
    "/api/auth/login",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    },
    { withAuth: false }
  );
}

export async function fetchCurrentUser() {
  return request("/api/auth/me");
}

export async function logout() {
  return request("/api/auth/logout", { method: "POST" });
}

export async function bootstrap() {
  return request("/api/bootstrap");
}

export async function analyze(payload) {
  const formData = new FormData();
  formData.append("mode", payload.mode);
  formData.append("source_platform", payload.sourcePlatform || "");
  formData.append("source_url", payload.sourceUrl || "");
  formData.append("raw_text", payload.rawText || "");
  if (payload.imageFile) {
    formData.append("image_file", payload.imageFile);
  }
  return request("/api/analyze", { method: "POST", body: formData }, { timeoutMs: 45000 });
}

export async function writeExcel(payload) {
  return request("/api/write", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function searchHistory(params) {
  const query = new URLSearchParams({
    query: params.query || "",
    priority: params.priority || "",
    match_direction: params.matchDirection || "",
    limit: String(params.limit || 50)
  });
  return request(`/api/history?${query.toString()}`);
}

export async function getHistoryDetail(id) {
  return request(`/api/history/${id}`);
}
