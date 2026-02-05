import axios from "./init";

const basePath = "/events";

export const getAllEvents = () => {
  return axios.get(`${basePath}/`);
};

export const getOneEvent = (id: number, type: "external" | "internal") => {
  return axios.get(`${basePath}/${type}/${id}`);
};

export const getAllPublicEvents = () => {
  return axios.get(`${basePath}/public`);
};

export const createExternalEvent = (formData: any) => {
  return axios.post(`${basePath}/external`, formData);
};

export const createInternalEvent = (formData: any) => {
  return axios.post(`${basePath}/internal`, formData);
};

export const submitExternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/external/submit/${eventId}`);
};

export const analyzeExternalEvent = (eventId: number) => {
  return axios.get(`${basePath}/external/analyze/${eventId}`);
};

export const analyzeInternalEvent = (eventId: number) => {
  return axios.get(`${basePath}/internal/analyze/${eventId}`);
};

export const acceptExternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/external/accept/${eventId}`);
};

export const rejectExternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/external/reject/${eventId}`);
};

export const submitInternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/internal/submit/${eventId}`);
};

export const acceptInternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/internal/accept/${eventId}`);
};

export const rejectInternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/internal/reject/${eventId}`);
};

export const publicizeExternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/external/to-public/${eventId}`);
};

export const publicizeInternalEvent = (eventId: number) => {
  return axios.patch(`${basePath}/internal/to-public/${eventId}`);
};

export const updateExternalEvent = (eventId: number, data: any) => {
  return axios.put(`${basePath}/external/${eventId}`, data);
};

export const updateInternalEvent = (eventId: number, data: any) => {
  return axios.put(`${basePath}/internal/${eventId}`, data);
};

export const updateSignatories = (signatoryId: number, payload: any) => {
  return axios.put(`${basePath}/signatories/${signatoryId}`, payload);
};

export const getSignatory = (signatoryId: number) => {
  return axios.get(`${basePath}/signatories/${signatoryId}`);
};
