import { useState } from 'react';
import axios from 'axios';
import Button from '@mui/material/Button';
import { useNavigate } from 'react-router-dom';
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


export default function SendOTP() {
    const navigate = useNavigate();
    const theme = createTheme();


    const [email, setEmail] = useState("");
    const [error, setError] = useState(null);

    const isFormValid = () => {
        return email.trim();
    }

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            let response = await axios.post(`${baseUrl}/pwd-reset/verify-email`, 
            {"email": email}, {headers: {'Content-Type': 'application/x-www-form-urlencoded',
                                         'accept': 'application/json'
        }});
            sessionStorage.setItem("email", email);
            navigate("/reset-password/otp");

        } catch (error) {
            if (error.response.status === 400) {
                setError(error.response.data.detail);
            } else if (error.response.status === 422) {
                setError("Invalid email");
            }
        }
    }

    return (
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
            <Typography variant="h5">
                Reset Password
            </Typography>
            <Box component="form" noValidate sx={{ mt: 1 }} onSubmit={handleSubmit}>
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

                <Error error={error} onClose={() => setError(null)}/>

                <Button
                disabled={!isFormValid()}
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                >
                Submit
                </Button>
                <Grid container>
                <Grid item>
                    <Link href="/login" variant="body2">
                    {"Back to login"}
                    </Link>
                </Grid>
                </Grid>
            </Box>
            </Box>
        </Container>
        </ThemeProvider>
    );
}