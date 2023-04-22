import { useState, useEffect, useContext } from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import AuthContext from '../context/AuthContext';


export function Error(props) {
  let error;
  if (props.error === null) {
    error = null;
  } else {
    error = props.error;
  }

  return error ? (
    <Alert variant='outlined' severity='error' sx={{"mt": "4%"}} {...props}>
      {props.error}
    </Alert>
  ) : null;
}


function AlertOrNothing() {
    // create a state variable to store the item from sessionStorage
    const [isAfterRegistration, setIsAfterRegistration] = useState(false);
  
    // create an effect hook that runs when the component mounts
    useEffect(() => {
      // read the item from sessionStorage
      const value = sessionStorage.getItem("isAfterRegistration");
      // convert the value to a boolean and set the state variable
      setIsAfterRegistration(value === "true");
    }, []); // pass an empty dependency array to run only once
  
    // create a function to handle the close event of the Alert component
    const handleClose = () => {
      // remove the item from sessionStorage
      sessionStorage.removeItem("isAfterRegistration");
      // set the state variable to false
      setIsAfterRegistration(false);
    };
  
    // render the Alert component only if isAfterRegistration is true
    return isAfterRegistration ? (
      <Alert variant="outlined" severity="success" sx={{"mt": "5%"}} onClose={handleClose} >
        Congratulations, Now you can log in into your account
      </Alert>
    ) : null;
  }

function Copyright(props) {
  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit" href="https://mui.com/">
        Wallet app
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const theme = createTheme();

export default function SignIn() {
    let {error, setError, loginUser} = useContext(AuthContext);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    
    const isFormValid = () => {
        return (
          email.trim() &&
          password.trim()
        );  
      };

      const handleSubmit = (e) => {
        e.preventDefault();
        loginUser(e, email, password); 
      }

    return (
        <ThemeProvider theme={theme}>
        <Container component="main" maxWidth="xs">
            <CssBaseline />
            <AlertOrNothing />
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
                Sign in
            </Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }} method='POST'>
                <TextField
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                />
                <TextField
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                />

                <Error error={error} onClose={() => setError(null)}/>

                <Button
                disabled={!isFormValid()}
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                >
                Sign In
                </Button>
                <Grid container>
                <Grid item xs>
                    <Link href="/reset-password" variant="body2">
                    Forgot password?
                    </Link>
                </Grid>
                <Grid item>
                    <Link href={window.location.origin + "/signup"} variant="body2">
                    {"Don't have an account? Sign Up"}
                    </Link>
                </Grid>
                </Grid>
            </Box>
            </Box>
            <Copyright sx={{ mt: 8, mb: 4 }} />
        </Container>
        </ThemeProvider>
    );
    }