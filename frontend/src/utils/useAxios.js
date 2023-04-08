import axios from 'axios'
import jwt_decode from "jwt-decode";
import dayjs from 'dayjs'
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'
import { baseUrl } from '../APIBaseURL';


const useAxios = () => {
    const {authTokens, setUser, setAuthTokens} = useContext(AuthContext)

    const axiosInstance = axios.create({
        baseURL: baseUrl,
        headers:{Authorization: `Bearer ${authTokens?.access_token}`}
    });


    axiosInstance.interceptors.request.use(async req => {
    
        const user = jwt_decode(authTokens.access_token)
        const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;
    
        if(!isExpired) return req
    
        const response = await axios.post(`${baseUrl}/auth/token/refresh`, {
            refresh_token: authTokens.refresh_token
          });
    
        localStorage.setItem('authTokens', JSON.stringify(response.data))
        
        setAuthTokens(response.data)
        setUser(jwt_decode(response.data.access_token))
        
        req.headers.Authorization = `Bearer ${response.data.access_token}`
        return req
    })
    
    return axiosInstance
}

export default useAxios;