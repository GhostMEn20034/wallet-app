import axios from 'axios';
import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import { TextField } from '@mui/material';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import AppBar from '@mui/material/AppBar';
import BasicDatePicker from './DatePicker';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import { baseUrl } from '../APIBaseURL';
import AuthContext from '../context/AuthContext';
import dayjs from 'dayjs';
import useAxios from '../utils/useAxios';


function DenseAppBar() {
    return (
      <Box sx={{ flexGrow: 1,}}>
        <AppBar position="static" sx={{"background": "#5E35B1"}}>
          <Toolbar variant="dense" >
            <Typography variant="h6" color="inherit" component="div">
              Personal info
            </Typography>
          </Toolbar>
        </AppBar>
      </Box>
    );
  }


export default function UserProfile() {
    let [firstName, setFirstName] = React.useState("");
    let [lastName, setLastName] = React.useState("");
    let [email, setEmail] = React.useState("");
    let [dateOfBirth, setDateOfBirth] = React.useState(null);
    let [gender, setGender] = React.useState("")

    let {authTokens, logoutUser} = React.useContext(AuthContext)

    let api = useAxios()

    React.useEffect(
        () => {
            getUserData()
        }, []
    )

    let getUserData = async () => {
            let response = await api.get('/user/profile')      

            let data = await response.data

            if (response.status === 200) {
                setFirstName(data.first_name);
                setLastName(data.last_name || '')
                setEmail(data.email);
                setDateOfBirth(dayjs(data.date_of_birth) || null);
                setGender(data.gender);
            } else if (response.status === 401) {
                logoutUser()
            }
        }
    

    const isFormValid = () => {
        return (
            firstName.trim() &&
            email.trim() 
        );
    }


    const handleSubmit = (e) => {
        e.preventDefault();
        let data_from_form = {
          first_name : firstName,
          last_name: lastName,
          email: email,
          date_of_birth: dateOfBirth.format("YYYY-MM-DD"),
          gender: gender
        }
        console.log(data_from_form)
    }

    return (
    <React.Fragment>
        <DenseAppBar />  
        <CssBaseline />
        <Container sx={{width: '75%'}}>
        <Box sx={{ height: '50vh', 'mt': '2%', padding: 1}} component='form' onSubmit={handleSubmit}>
        <Box>    
        <TextField id="standard-basic" label="First name" variant="standard" name='first_name' value={firstName} 
        onChange={(e) => setFirstName(e.target.value)} sx={{m: 2, }}/>
        </Box>
        <Box>
        <TextField id="standard-basic" label="Last Name" variant="standard" name='last_name' 
        value={lastName} onChange={(e) => setLastName(e.target.value)} sx={{m: 2, }}/>
        </Box>
        <Box>
        <TextField id="standard-basic" label="Email address" variant="standard" name='email'
        value={email} onChange={(e) => setEmail(e.target.value)} sx={{m: 2, }}/>
        </Box>
        <Box>    
        <BasicDatePicker sx={{'m': 2}} value={dateOfBirth} onChange={(NewValue) => setDateOfBirth(NewValue)}/>
        </Box>
        <Box>
        <Box sx={{ width: "15%" }}>
          <FormControl fullWidth sx={{m: 2}}>
            <InputLabel id="demo-simple-select-label">Gender</InputLabel>
            <Select
              name='gender'
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              label="Gender"
            >
              <MenuItem value='Unspecified'>Unspecified</MenuItem>
              <MenuItem value='Male'>Male</MenuItem>
              <MenuItem value='Female'>Female</MenuItem>
            </Select>
          </FormControl>
        </Box>
        </Box>
        <Button variant="contained" size="medium" sx={{m: 2}} type='submit' disabled={!isFormValid()}>
            Update Personal info
        </Button>    
        </Box>
        </Container>
    </React.Fragment>
    );
    }