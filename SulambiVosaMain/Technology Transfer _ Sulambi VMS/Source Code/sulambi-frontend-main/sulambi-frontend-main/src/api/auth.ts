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

/** Logout using httpOnly cookie (no token in URL). Backend clears cookie. */
export const logout = () => {
  return axios.delete(`${basePath}/logout`);
};

/** Get current session from httpOnly cookie. Used to restore accountDetails without storing token. */
export const getMe = () => {
  return axios.get(`${basePath}/me`);
};
