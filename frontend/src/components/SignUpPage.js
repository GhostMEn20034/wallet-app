import axios from 'axios';
import { useState } from 'react';
import Alert from '@mui/material/Alert';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { baseUrl } from '../APIBaseURL';
import ConfirmCode from './ConfirmCode';




function Copyright(props) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit" href="#">
        Wallet App
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}



export function ErrorOrNothing(props) {
  let error;
  if (props.error === null) {
    error = null;
  } else {
    error = props.error.detail;
  }

  return error ? (
    <Alert variant="outlined" severity="error" sx={{"mt": "4%"}} {...props}>
      {props.error.detail}
    </Alert>
  ) : null;
}




const theme = createTheme();

export default function SignUp() {
  // const navigate = useNavigate()

  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);



  const isFormValid = () => {
    return (
      email.trim() &&
      password1.trim() &&
      password2.trim()
    );
  };


  const handleBack = () => {
    setSubmitted(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    axios.post(`${baseUrl}/signup/validate-credentials`, {
      email: data.get('email'),
      password1: data.get('password1'),
      password2: data.get('password2')
    }).then(response => {
      setSubmitted(true)
      console.log(submitted)
    })
      .catch(error => {
        setError(error.response.data)
      })
  };

  return (
    <div>
      {!submitted ? (
        <ThemeProvider theme={theme}>
        <Container component="main" maxWidth="xs">
          <CssBaseline />
          <Box
            sx={{
              marginTop: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
              <LockOutlinedIcon />
            </Avatar>
            <Typography component="h1" variant="h5">
              Sign up
            </Typography>
            <Box component="form" noValidate onSubmit={handleSubmit} sx={{ mt: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    fullWidth
                    id="email"
                    label="Email Address"
                    name="email"
                    autoComplete="email"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    value={password1}
                    onChange={(e) => setPassword1(e.target.value)}
                    required
                    fullWidth
                    name="password1"
                    label="Password"
                    type="password"
                    id="password1"
                    autoComplete="new-password"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    value={password2}
                    onChange={(e) => setPassword2(e.target.value)}
                    required
                    fullWidth
                    name="password2"
                    label="Confirm password"
                    type="password"
                    id="password2"
                    autoComplete="new-password"
                  />
                </Grid>
              </Grid>
  
              <ErrorOrNothing error={error} onClose={() => setError(null)}/>
  
              <Button
                disabled={!isFormValid()}
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
              >
                Sign Up
              </Button>
              <Grid container justifyContent="flex-end">
                <Grid item>
                  <Link href={window.location.origin + "/login"} variant="body2">
                    Already have an account? Sign in
                  </Link>
                </Grid>
              </Grid>
            </Box>
          </Box>
          <Copyright sx={{ mt: 5 }} />
        </Container>
      </ThemeProvider>
      ) : (
        <ConfirmCode onBack={handleBack} email={email} password1={password1} password2={password2}/>
      )}
    </div>
  );
}