import { Navigate } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";

function PrivateRoute({ children }) {
  let {user} = useContext(AuthContext)
    return user ? <>{children}</> : <Navigate to="/login" />;
  }

export default PrivateRoute