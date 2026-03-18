import axios from "./init";

const basePath = "/reports";

export const getAllReports = () => {
  return axios.get(`${basePath}/`);
};

/** Public endpoint for landing page / carousel (no auth). */
export const getPublicReports = () => {
  return axios.get(`${basePath}/public`);
};

export const getReportAnalytics = (
  eventId: number,
  type: "external" | "internal"
) => {
  return axios.get(`${basePath}/analytics/${type}/${eventId}`);
};

export const createReport = (
  eventId: number,
  type: "external" | "internal",
  reportData: FormData
) => {
  return axios.post(`${basePath}/${type}/${eventId}`, reportData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const updateReport = (
  reportId: number,
  type: "external" | "internal",
  reportData: FormData
) => {
  return axios.put(`${basePath}/${type}/${reportId}`, reportData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const deleteReport = (
  reportId: number,
  type: "external" | "internal"
) => {
  return axios.delete(`${basePath}/${type}/${reportId}`);
};


