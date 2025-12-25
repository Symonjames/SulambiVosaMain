import axios from "./init";

const basePath = "/feedback";

export const getEventFeedback = async (
  eventType: "external" | "internal",
  eventId: number
) => {
  return axios.get(`${basePath}/${eventType}/${eventId}`);
};

export const submitFeedback = async (
  eventType: "external" | "internal",
  eventId: number,
  feedback: string
) => {
  return axios.post(`${basePath}/${eventType}/${eventId}`, { feedback });
};

export const updateFeedback = async (feedbackId: number, feedback: string) => {
  return axios.put(`${basePath}/${feedbackId}`, { feedback });
};
