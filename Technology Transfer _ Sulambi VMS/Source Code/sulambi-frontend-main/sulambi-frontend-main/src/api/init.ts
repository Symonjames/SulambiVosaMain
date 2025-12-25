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
  }

  // If data is FormData, remove Content-Type header to let browser/axios set it with boundary
  if (config.data instanceof FormData && config.headers) {
    delete config.headers["Content-Type"];
  }

  config.withCredentials = true;
  config.baseURL = API_BASE_URL;
  return config;
});

export default axios;
