import axios from "axios";
import { useState } from "react";
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import { useNavigate } from 'react-router-dom';
import { baseUrl } from '../APIBaseURL';
import { ErrorOrNothing } from "./SignUpPage";

export default function ConfirmCode({onBack, email, password1, password2}) {
    const [code, setCode] = useState("")
    const [error, setError] = useState(null)
  
    const isFormValid = () => {
      console.log(code.trim().length === 7)
      return (
        code.trim().length === 7
      );
    };


    const navigate = useNavigate()
  
    const handleSubmit = (e) => {
      e.preventDefault();
      axios.post(`${baseUrl}/signup/verify-email`, {
        email: email,
        code: code,
      }).then(response => {

        axios.post(`${baseUrl}/user/signup`, {
          email: email,
          password1: password1,
          password2: password2
        }).then(response => {
          sessionStorage.setItem("isAfterRegistration", true);
          navigate('/login');
        })
          .catch(error => {
            setError(error.response.data)
          })

      })
        .catch(error => {
          setError(error.response.data)
        })

      
    };
  
    const handleChange = (e) => {
      setCode(e.target.value);
    };
  
  
    return (
    <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="100vh"
    >
      <form onSubmit={handleSubmit}>
      <Grid container direction="column">
          <Grid item>
          <Typography variant="body1" gutterBottom>
          To ensure that <b>{email}</b> is your email, <br />
          we've sent <b>7-digit</b> confirmation code on this email
          </Typography>
          </Grid>
          <Grid item>
            <TextField
              label="Enter code here"
              value={code}
              onChange={handleChange}
              required
              sx={{ml: "20%"}}
            />
          </Grid>
          <ErrorOrNothing error={error} onClose={() => setError(null)}/>
          <Grid item sx={{mt: "3%"}}>
            <Button type="submit" variant="contained" color="primary" disabled={!isFormValid()} sx={{ml: "20%"}}>
              Submit
            </Button>
            <Button 
            onClick={
              () => {onBack(); 
                     setCode("");}
            }
            variant="contained"
            sx={{ml: "8.23%",backgroundColor: "#ebdb02", ":hover": {bgcolor: "#d1c302", color: "white"}}}
            >
              Go back
            </Button>
          </Grid>
        </Grid>
      </form>
    </Box>
    )
  }