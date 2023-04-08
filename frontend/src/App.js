import './App.css';
import SignUp from './components/SignUpPage';
import SignIn from './components/SignInPage';
import UserProfile from './components/UserProfile';
import { AuthProvider } from './context/AuthContext';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import PrivateRoute from './utils/PrivateRoute';


function App() {
  return( 
   
    <BrowserRouter>
    <AuthProvider>
      <Routes>
          <Route path='/signup' element={<SignUp />} />
          <Route path='/login' element={
          <SignIn />
          } />
          <Route path='/profile' element={
              <PrivateRoute>
              <UserProfile />
              </PrivateRoute>
          }/>
      </Routes>
    </AuthProvider>  
    </BrowserRouter>
  );
}

export default App;
