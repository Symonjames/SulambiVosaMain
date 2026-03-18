import axios from "./init";

const basePath = "/evaluation";

export const getAllEvaluation = () => {
  return axios.get(`${basePath}/`);
};

export const getPersonalEvaluation = () => {
  return axios.get(`${basePath}/personal`);
};

export const getExternalEvaluations = (eventId: number) => {
  return axios.get(`${basePath}/event/external/${eventId}`);
};

export const getInternalEvaluations = (eventId: number) => {
  return axios.get(`${basePath}/event/internal/${eventId}`);
};

export const checkReqIdValidity = (requirementId: string) => {
  return axios.get(`${basePath}/validity/${requirementId}`);
};

export const createEvaluation = (
  requirementId: string,
  evaluationData: any
) => {
  return axios.post(`${basePath}/${requirementId}`, evaluationData);
};
