import axios from "axios";

// Export the API base URL for use in other modules

const API_BASE_URL = import.meta.env.VITE_API_URI || "http://localhost:8000/api";

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
    console.log('[API_RESPONSE]', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    // 403 on /auth/me is expected when not logged in; don't log as error
    const url = error.config?.url ?? '';
    const isAuthMe403 = error.response?.status === 403 && (url === '/me' || url.endsWith('/auth/me') || url.includes('/auth/me'));
    if (isAuthMe403) {
      // Silent: session check returned not authenticated (normal when not logged in)
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
