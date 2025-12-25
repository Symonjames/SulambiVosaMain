import axios from "./init";

const basePath = "/requirements";

export const getAllRequirements = () => {
  return axios.get(`${basePath}/`);
};

export const uploadRequirements = (
  eventId: number,
  multiPartData: FormData
) => {
  // The axios interceptor will automatically remove Content-Type for FormData
  // so axios/browser can set multipart/form-data with boundary automatically
  return axios.post(`${basePath}/${eventId}`, multiPartData);
};

export const acceptRequirement = (id: number) => {
  return axios.patch(`${basePath}/accept/${id}`);
};

export const rejectRequirement = (id: number) => {
  return axios.patch(`${basePath}/reject/${id}`);
};
