import axios from 'axios'
import jwt_decode from "jwt-decode";
import { useContext } from 'react'
import AuthContext from '../context/AuthContext'
import { baseUrl } from '../APIBaseURL';


const useAxios = () => {
    const {logoutUser, authTokens, setUser, setAuthTokens} = useContext(AuthContext)

    const axiosInstance = axios.create({
        baseURL: baseUrl,
        headers:{Authorization: `Bearer ${authTokens?.access_token}`}
    });


    axiosInstance.interceptors.request.use(async req => {
    
        const user = jwt_decode(authTokens.access_token);
        let current_date = Date.now();
        if(user.exp * 1000 > current_date) {
            return req
        } else {
            console.log("Expired")
            try {
                let response = await axios.post(`${baseUrl}/auth/token/refresh`, {
                    refresh_token: authTokens.refresh_token
                });
            
                localStorage.setItem('authTokens', JSON.stringify(response.data))
                
                setAuthTokens(response.data)
                setUser(jwt_decode(response.data.access_token))
                
                req.headers.Authorization = `Bearer ${response.data.access_token}`
                return req
            } catch (error) {
                if (error.response.status === 401) {
                    logoutUser()
                    return Promise.reject("Session expired")
                } else {
                    logoutUser()
                    return Promise.reject("Entered invalid token")
                }
            }
        }

    })
    
    return axiosInstance
}

export default useAxios;