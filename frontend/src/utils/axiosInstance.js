import axios from "axios";
import { baseUrl } from "../APIBaseURL";

const api = axios.create({
    baseURL: baseUrl
})

export default api;
