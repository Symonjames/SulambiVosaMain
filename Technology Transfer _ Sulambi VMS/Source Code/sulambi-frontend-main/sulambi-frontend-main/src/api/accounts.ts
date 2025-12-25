import axios from "./init";

const basePath = "/accounts";

export const getAllAccounts = () => {
  return axios.get(`${basePath}/`);
};

export const getAllAdminAccounts = () => {
  return axios.get(`${basePath}/admin`);
};

export const getAllOfficerAccounts = () => {
  return axios.get(`${basePath}/officer`);
};

export const createNewAccount = (
  accountType: "admin" | "officer",
  data: { username: string; password: string }
) => {
  return axios.post(`${basePath}/${accountType}`, data);
};

export const deleteAccount = (id: number) => {
  return axios.delete(`${basePath}/${id}`);
};

export const updateAccount = (
  id: number,
  data: { username: string; password: string }
) => {
  return axios.put(`${basePath}/${id}`, data);
};
