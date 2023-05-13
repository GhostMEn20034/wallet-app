import axios from 'axios'
import dayjs from 'dayjs'
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
        let date = new Date()
        let current_date = new Date(date.toUTCString()).getTime()
        let isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;
        if(!isExpired) {
            console.log(`user exp ` + `${user.exp}`)
            console.log(`current date ` + `${current_date / 1000}`)
        
            return req
        } else {
            console.log(new Date(user.exp * 1000) > current_date)
            console.log(user.exp)
            console.log(`Now ---- ${current_date}`);
            console.log(`User exp ---- ${new Date(user.exp * 1000)}`)
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