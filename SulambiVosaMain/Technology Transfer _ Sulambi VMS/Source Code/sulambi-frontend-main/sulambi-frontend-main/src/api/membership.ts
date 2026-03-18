import axios from "./init";

const basePath = "/membership";

export const getAllMembers = () => {
  return axios.get(`${basePath}/`);
};

export const approveMembership = (id: number) => {
  return axios.patch(`${basePath}/approve/${id}`);
};

export const rejectMembership = (id: number) => {
  return axios.patch(`${basePath}/reject/${id}`);
};

export const activateMember = (id: number) => {
  return axios.patch(`${basePath}/activate/${id}`);
};

export const deactivateMember = (id: number) => {
  return axios.patch(`${basePath}/deactivate/${id}`);
};
