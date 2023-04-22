import { useState, useContext, useEffect } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import { Alert } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Error } from './SignInPage';
import { baseUrl } from '../APIBaseURL';
import AuthContext from '../context/AuthContext';


async function sleep(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
  }

function ChangedSuccess ({success, onClose}) {
    return success ? (
        <Alert variant="outlined" severity="success" onClose={onClose} >{success}</Alert>
    ) : null
}



export default function ConfirmOTP() {
    let {loginUser} = useContext(AuthContext);

    const [code, setCode] = useState("");
    const [password, setPassword] = useState("");
    const [submitted, setSubmitted] = useState(false);
    const [success, setSuccess] = useState("");
    const [error, setError] = useState(null);

    let token = sessionStorage.getItem("reset_pwd_token");

    useEffect(() => {
        if (token) {
          setSubmitted(true)
        }
      }, [token])

    const theme = createTheme();
    let email = sessionStorage.getItem("email");

    const isCodeValid = () => {
        return code.trim().length === 8;
    }
    
    const isPasswordValid = () => {
        return password.trim();
    }

    const handleCodeSubmit = async (e) => {
        e.preventDefault();
        try {
            let response = await axios.post(`${baseUrl}/pwd-reset/check-otp`, {
                email: email,
                code: code
            });
            console.log(response.data)
            sessionStorage.setItem("reset_pwd_token", await response.data.reset_pwd_token)
            setSubmitted(true);
        } catch (error) {
            setError(error.response.data.detail);
        }
    }

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        try {
            let response = await axios.post(`${baseUrl}/reset-password`, {
                token: sessionStorage.getItem("reset_pwd_token"),
                new_password: password

            });
            let status = await response.data.status;
            setSuccess(status);
            sessionStorage.removeItem("reset_pwd_token");
            sessionStorage.removeItem("email");
            await sleep(1);
            loginUser(e, email, password);

        } catch (error) {
                setError(error.response.data.detail)
        }
    }

    return (
        <div>
        {!submitted ? (    
        <ThemeProvider theme={theme}>
        <Container component="main" maxWidth="xs">
            <CssBaseline />
            <Box
            sx={{
                marginTop: "50%",
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
            }}
            >
            <Typography variant="h6">
                To ensure that <b>{email}</b> is your email, <br />
                we've sent <b>8-digit</b> code
            </Typography>
            <Box component="form" noValidate sx={{ mt: 1 }} onSubmit={handleCodeSubmit} method='POST'>
                <TextField
                value={code}
                onChange={(e) => setCode(e.target.value)}
                margin="normal"
                required
                fullWidth
                id="code"
                label="OTP code"
                name="code"
                autoComplete="code"
                autoFocus
                />

                <Error error={error} onClose={() => setError(null)}/>

                <Button
                disabled={!isCodeValid()}
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                >
                submit
                </Button>
                <Grid container>
                <Grid item>
                    <Link href="/login" variant="body2" onClick={() => sessionStorage.removeItem("email")}>
                    {"Back to login"}
                    </Link>
                </Grid>
                </Grid>
            </Box>
            </Box>
        </Container>
        </ThemeProvider>
        ) : (

            <ThemeProvider theme={theme}>
            <Container component="main" maxWidth="xs">
                <CssBaseline />
                <Box
                sx={{
                    marginTop: "50%",
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
                >
                <Typography variant="h6">
                    Enter new password
                </Typography>
                <Box component="form" noValidate sx={{ mt: 1 }} onSubmit={handlePasswordSubmit} method='POST'>
                    <TextField
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    margin="normal"
                    required
                    fullWidth
                    type='password'
                    id="password"
                    label="New password"
                    name="new_password"
                    autoComplete="current-password"
                    autoFocus
                    />
    
                    <Error error={error} onClose={() => setError(null)}/>
                    <ChangedSuccess success={success} onClose={(e) => setSuccess("")}/>
    
                    <Button
                    disabled={!isPasswordValid()}
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                    >
                    submit
                    </Button>
                    <Grid container>
                    <Grid item>
                        <Link href="/login" variant="body2" onClick={() => {
                            sessionStorage.removeItem("reset_pwd_token");
                            sessionStorage.removeItem("email");
                            }}>
                        {"Back to login"}
                        </Link>
                    </Grid>
                    </Grid>
                </Box>
                </Box>
            </Container>
            </ThemeProvider>
        )}
        </div>

    );
}