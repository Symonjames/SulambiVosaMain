import axios from "./init";

const basePath = "/dashboard";

export const getDashboardSummary = () => {
  return axios.get(`${basePath}/`);
};

export const getDashboardMemberDetails = () => {
  return axios.get(`${basePath}/active-member`);
};

export const getDashboardAnalytics = () => {
  // Add cache-busting timestamp to ensure fresh data
  return axios.get(`${basePath}/analytics`, {
    params: {
      _t: Date.now() // Cache buster
    }
  });
};

export const getEventDetails = (
  eventId: number,
  eventType: "external" | "internal"
) => {
  return axios.get(`${basePath}/event/${eventType}/${eventId}`);
};
