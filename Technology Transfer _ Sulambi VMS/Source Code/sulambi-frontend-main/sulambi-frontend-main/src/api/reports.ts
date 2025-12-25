import axios from "./init";

const basePath = "/reports";

export const getAllReports = () => {
  return axios.get(`${basePath}/`);
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

export const deleteReport = (
  reportId: number,
  type: "external" | "internal"
) => {
  return axios.delete(`${basePath}/${type}/${reportId}`);
};


