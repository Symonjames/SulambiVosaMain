import axios from "./init";

const basePath = "/requirements";

export const getAllRequirements = () => {
  return axios.get(`${basePath}/`);
};

export const uploadRequirements = (
  eventId: number,
  multiPartData: FormData
) => {
  return axios.post(`${basePath}/${eventId}`, multiPartData);
};

/** Public endpoint: join a public event as temporary volunteer (no auth). */
export const uploadRequirementsPublicEvent = (
  eventId: number,
  eventType: "external" | "internal",
  multiPartData: FormData
) => {
  return axios.post(`${basePath}/public-event/${eventId}/join`, multiPartData);
};

export const acceptRequirement = (id: number) => {
  return axios.patch(`${basePath}/accept/${id}`);
};

export const rejectRequirement = (id: number) => {
  return axios.patch(`${basePath}/reject/${id}`);
};
