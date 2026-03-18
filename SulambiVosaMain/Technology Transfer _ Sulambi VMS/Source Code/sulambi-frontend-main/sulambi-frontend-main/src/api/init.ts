import axios from "axios";

// Export the API base URL for use in other modules

// In dev: default to /api so requests go through Vite proxy to the local backend.
// Set VITE_USE_ABSOLUTE_API_IN_DEV=true only when you intentionally want a non-local API in dev.
const requestedApiBase = String(import.meta.env.VITE_API_URI || "").trim();
const useAbsoluteApiInDev =
  String(import.meta.env.VITE_USE_ABSOLUTE_API_IN_DEV || "").toLowerCase() ===
  "true";

const API_BASE_URL = import.meta.env.DEV && !useAbsoluteApiInDev
  ? "/api"
  : requestedApiBase || "http://localhost:8000/api";

// If API source changes (for example remote -> local), clear stale cached API payloads.
if (typeof window !== "undefined") {
  try {
    const scopeKey = "__api_cache_scope__";
    const previousScope = window.localStorage.getItem(scopeKey);
    if (previousScope && previousScope !== API_BASE_URL) {
      Object.keys(window.localStorage).forEach((key) => {
        if (key.startsWith("api_cache_")) {
          window.localStorage.removeItem(key);
        }
      });
    }
    window.localStorage.setItem(scopeKey, API_BASE_URL);
  } catch {
    // Ignore storage access issues (private mode, SSR tests, etc.)
  }
}

export { API_BASE_URL };

axios.defaults.headers.common["Content-Type"] = "application/json";
axios.defaults.headers.common.Accept = "application/json";
axios.interceptors.request.use((config) => {
  // Auth uses httpOnly cookie (session_token); no token in localStorage or headers
  config.withCredentials = true;
  config.baseURL = API_BASE_URL;

  // If data is FormData, remove Content-Type header to let browser/axios set it with boundary
  if (config.data instanceof FormData && config.headers) {
    delete config.headers["Content-Type"];
  }

  return config;
});

// Add response interceptor for error logging
axios.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log('[API_RESPONSE]', {
        status: response.status,
        url: response.config.url,
        data: response.data
      });
    }
    return response;
  },
  (error) => {
    const status = error.response?.status;
    const msg = (error.response?.data as any)?.message ?? '';
    const authMsg = /not authenticated|unauthorized|token invalid|session expired|session invalid|not permitted|authentication required/i.test(String(msg));
    const isAuth403 = status === 403 && authMsg;
    if (isAuth403) {
      // Silent: expected when not logged in or cookie not sent
    } else {
      console.error('[API_ERROR]', {
        message: error.message,
        code: error.code,
        url: error.config?.url,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      });
    }
    return Promise.reject(error);
  }
);

export default axios;
