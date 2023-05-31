import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { Stack, Button, Typography } from "@mui/material";
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import { useNavigate } from "react-router-dom";
import BalanceChart from "./charts/BalanceTrend";
import dayjs from "dayjs";


export default function AccountDetail() {
    let [account, setAccount] = useState({});

    let api = useAxios();
    const navigate = useNavigate();
    const params = useParams();

    let accountId = params.id;

    let getAccount = async () => {
        let response = await api.get(`/accounts/${accountId}`)
        let data = await response.data
        setAccount(data)
    }

    useEffect(
        () => {
          getAccount();
          console.log(account)
        }, []
      )
    
    let handleBack = () => {
      navigate('/accounts')
    }  

    return (
      <div>
       
        <Stack sx={{padding: "1 rem"}}>
          
          <Stack sx={{py: "0.75%", px: "1.5%", backgroundColor: "#f5fffe", boxShadow: 1}} direction="row" alignItems="center">
            <Button size="small"
            sx={{width: "3%",minWidth: "15px" ,backgroundColor: "white", ":hover": { bgcolor: "#edebec"}}}
            variant="contained"
            onClick={handleBack}
            ><ArrowBackIosNewIcon sx={{"color": "black"}}/></Button>
            <Typography variant="h5" sx={{"marginLeft": 2}}>Account details</Typography>
            <Button size="small" variant="outlined" sx={{marginLeft: "auto"}}>Edit</Button>
            <Button size="small" variant="outlined" sx={{marginLeft: "2%"}} color="error">Delete</Button>
          </Stack>
          <Stack sx={{py: "1%", px: "2%", backgroundColor: "#f5fffe", boxShadow: 3, mt: "0.25%"}} direction="row">
            {account.color && (  
            <AccountBalanceWalletIcon sx={{fontSize: "105px", color: account.color}}/>
            )}
            <Stack sx={{"marginLeft": 2}}>
              <Typography variant="overline">Name</Typography>
              <Typography variant="subtitle2"><b>{account.name}</b></Typography>
              <Typography variant="overline">Created on</Typography>
              <Typography variant="subtitle2"><b>{dayjs(account.created_at).format("LL")}</b></Typography>
            </Stack>
          </Stack>
          <Stack sx={{py: "1%", px: "2%", backgroundColor: "#f5fffe", boxShadow: 3, mt: "0.25%"}}>
              <Stack>
              <Typography variant="overline">Balance</Typography>
              <Typography variant="h6"><b>{account.balance}&nbsp;{account.currency}</b></Typography>
              </Stack>
              {account.current_period &&(
              <BalanceChart data={account}/>
              )}
          </Stack>
        </Stack>
      </div>   
    )
}
