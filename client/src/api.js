import axios from "axios";

// backend URL (Render)
const API_BASE_URL = process.env.REACT_APP_API_URL;

// axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

export default api;
