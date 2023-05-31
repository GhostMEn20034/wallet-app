import './App.css';
import SignUp from './components/SignUpPage';
import SignIn from './components/SignInPage';
import UserProfile from './components/UserProfile';
import { AuthProvider } from './context/AuthContext';
import { BrowserRouter, Routes, Route} from 'react-router-dom';
import PrivateRoute from './utils/PrivateRoute';
import SendOTP from './components/ResetPassword';
import ConfirmOTP from './components/ConfirmResetCode';
import RecordHistory from './components/RecordsHistory';
import AcccountList from './components/Accounts';
import AccountDetail from './components/AccountDetail';

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
          <Route path='/records' element={
            <PrivateRoute>
            <RecordHistory />  
            </PrivateRoute>
          }/>
          <Route path='/accounts' element={
            <PrivateRoute>
            <AcccountList />  
            </PrivateRoute>
          }/>
          <Route path='/accounts/:id' element={
            <PrivateRoute>
            <AccountDetail />
            </PrivateRoute>
          } />
          <Route path='/reset-password' element={<SendOTP />}/>
          <Route path='/reset-password/otp' element={<ConfirmOTP />}/>
      </Routes>
    </AuthProvider>  
    </BrowserRouter> 
  );
}

export default App;
