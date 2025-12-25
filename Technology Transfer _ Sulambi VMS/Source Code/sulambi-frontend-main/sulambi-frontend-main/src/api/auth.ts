import { MembershipType } from "../interface/types";
import axios from "./init";

const basePath = "/auth";

export const login = (username: string, password: string) => {
  return axios.post(`${basePath}/login`, {
    username,
    password,
  });
};

export const register = (membershipData: MembershipType) => {
  return axios.post(`${basePath}/register`, membershipData);
};

export const logout = (usertoken: string) => {
  return axios.delete(`${basePath}/logout/${usertoken}`);
};
