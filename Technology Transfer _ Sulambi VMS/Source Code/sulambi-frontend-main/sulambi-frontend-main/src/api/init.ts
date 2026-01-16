import axios from "axios";

// Export the API base URL for use in other modules

const API_BASE_URL = import.meta.env.VITE_API_URI || "http://localhost:8000/api";

export { API_BASE_URL };

axios.defaults.headers.common["Content-Type"] = "application/json";
axios.defaults.headers.common.Accept = "application/json";
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token && config.headers) {
    config.headers["Authorization"] = "Bearer " + token;
  } else {
    // Log when token is missing for protected routes
    if (config.url && (config.url.includes("/requirements") || config.url.includes("/accounts") || config.url.includes("/membership"))) {
      console.warn('[API_REQUEST] ⚠️ No token found for protected route:', config.url);
      console.warn('[API_REQUEST] Token in localStorage:', !!token);
    }
  }

  // If data is FormData, remove Content-Type header to let browser/axios set it with boundary
  if (config.data instanceof FormData && config.headers) {
    delete config.headers["Content-Type"];
  }

  config.withCredentials = true;
  config.baseURL = API_BASE_URL;
  
  // Log API requests for debugging
  console.log('[API_REQUEST]', {
    method: config.method?.toUpperCase(),
    url: `${config.baseURL}${config.url}`,
    fullUrl: `${config.baseURL}${config.url}`,
    hasData: !!config.data,
    dataKeys: config.data && typeof config.data === 'object' ? Object.keys(config.data) : 'N/A',
    hasToken: !!token,
    tokenLength: token ? token.length : 0
  });
  
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
    console.error('[API_ERROR]', {
      message: error.message,
      code: error.code,
      url: error.config?.url,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    });
    return Promise.reject(error);
  }
);

export default axios;
