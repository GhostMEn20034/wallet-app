import axios from "axios";
import { createContext, useState, useEffect } from "react";
import jwt_decode from "jwt-decode";
import { baseUrl } from "../APIBaseURL";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext()

export default AuthContext;

export const AuthProvider = ({children}) => {

    let [authTokens, setAuthTokens] = useState(()=> localStorage.getItem('authTokens') ? JSON.parse(localStorage.getItem('authTokens')) : null);
    let [user, setUser] = useState(()=> localStorage.getItem('authTokens') ? jwt_decode(localStorage.getItem('authTokens')) : null);
    let [loading, setLoading] = useState(true);
    let [error, setError] = useState(null);

    const navigate = useNavigate()


    let loginUser = async (e, email, password) => {
      e.preventDefault();
      // const data = new FormData(e.currentTarget);
      
        try {
          let response = await axios.post(
            `${baseUrl}/auth/token`,
            {
              username: email,
              password: password
            },
            {
              headers: {
                accept: "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
              },
            }
          );
      
          let response_data = await response.data;
      
          if (response.status === 200) {
            setAuthTokens(response_data);
            setUser(jwt_decode(response_data.access_token));
            localStorage.setItem("authTokens", JSON.stringify(response_data));
            navigate("/profile");
          }
        } catch (error) {
          if (error.response && error.response.status === 400) {
            setError("Incorrect password or email");
          }
        }
      };

    let logoutUser = () => {
        setAuthTokens(null)
        setUser(null)
        localStorage.removeItem('authTokens');
        navigate('/login')
    }


    let contextData = {
        user: user,
        loginUser: loginUser,
        logoutUser: logoutUser,
        authTokens: authTokens,
        setAuthTokens:setAuthTokens,
        setUser:setUser,
        error: error,
        setError: setError,
    }

    useEffect(()=> {

        if(authTokens){
            setUser(jwt_decode(authTokens.access_token))
        }
        setLoading(false)


    }, [authTokens, loading])

    return (
        <AuthContext.Provider value={contextData}>
            {loading ? null: children}
        </AuthContext.Provider>
    )
}
