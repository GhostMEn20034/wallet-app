import {
  Box,
  Button,
  Typography,
  FormControl,
  MenuItem,
  Select,
  Stack,
  Paper
} from "@mui/material";

import { useNavigate } from "react-router-dom";
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import { useState, useEffect } from "react";
import { styled } from '@mui/material/styles';
import useAxios from '../utils/useAxios';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';


export default function AcccountList() {
  let [accounts, setAccounts] = useState([]);
  let [sortOption, setSortOption] = useState({ sortBy: "name", order: "asc" });

  let api = useAxios();
  const navigate = useNavigate();

  let getAccounts = async () => {
    let params = {
      sort_by: sortOption.sortBy, order: sortOption.order
    }

    let response = await api.get("/accounts/", { "params": params });
    let data = await response.data;
    // console.log(data)
    setAccounts(data);
  }

  useEffect(
    () => {
      getAccounts();
    }, [sortOption]
  )

  const Item = styled(Paper)(({ theme }) => ({
    backgroundColor: "#f3fffe",
    ...theme.typography.body2,
    padding: theme.spacing(1),
    // textAlign: 'center',
    color: theme.palette.text.secondary,
  }));


  let handleChangeOption = (e) => {

    let sortOptions = [
      { "sortBy": "name", "order": "asc" },
      { "sortBy": "name", "order": "desc" },
      { "sortBy": "balance", "order": "asc" },
      { "sortBy": "balance", "order": "desc" },
    ];

    let selectedOption = e.target.value;

    setSortOption(sortOptions[selectedOption]);
  }

  let getValue = () => {
    // This function returns the value that matches the sortOption state object
    switch (`${sortOption.sortBy}-${sortOption.order}`) {
      case "name-asc":
        return 0;
      case "name-desc":
        return 1;
      case "balance-asc":
        return 2;
      case "balance-desc":
        return 3;
      default:
        return -1; // Return -1 if no match is found
    }
  }

  let handleClickOnAccount = id => {
    navigate(`/accounts/${id}`)
  }

  return (
    <div>
      <Box display="flex">
        <Box sx={{ bgcolor: "#f5fffe", width: "23%", height: "10%", paddingBottom: "2%", mt: "8.5%", ml: "1%", "borderRadius": "15px", boxShadow: 3 }}
        >
          <Box spacing={0}>
            <Typography variant='h5' sx={{ mt: "5%", ml: "5%" }}>Accounts</Typography>
            <Button variant='contained' size='small'
              sx={{ width: "65%", left: "20%", mt: "10%", mr: "5%", backgroundColor: "#30b864", ":hover": { bgcolor: "#289953", color: "white" } }}>
              <AddCircleOutlineIcon /> &nbsp;Add Account
            </Button>
          </Box>
          <Typography sx={{ ml: "5%", mt: "5%" }} variant='subtitle1'>
            Sort by:
          </Typography>
          <FormControl sx={{ ml: "5%", width: "90%" }} size="small">
            <Select
              value={getValue()}
              onChange={handleChangeOption}
            >
              <MenuItem value={0}>Name (asc)</MenuItem>
              <MenuItem value={1}>Name (desc)</MenuItem>
              <MenuItem value={2}>Balance (asc)</MenuItem>
              <MenuItem value={3}>Balance (desc)</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Box sx={{ width: '100%', mt: "7%" }}>

          <Stack sx={{ mr: "1.5%" }}>
            <Stack sx={{ mt: "2%" }}>
              {accounts && accounts.map((item, index) => (
                <Stack key={index}>
                  <Stack spacing={2} key={`stack-${item._id}`} sx={{ ml: "5%" }}>
                    <Item key={item._id} sx={{ mb: "1.5%", display: "flex", alignItems: "center", padding: 1.5, ":hover": { "cursor": "pointer" } }}
                      onClick={() => handleClickOnAccount(item._id)}>
                      <AccountBalanceWalletIcon fontSize="large" sx={{ color: item.color }} />
                      <Typography sx={{ ml: "2%", color: "black" }}><b>{item.name}</b></Typography>
                      <Typography sx={{ ml: "auto", color: "black" }}><b>{item.balance}&nbsp;{item.currency}</b></Typography>
                    </Item>
                  </Stack>
                </Stack>
              ))}
            </Stack>
          </Stack>
        </Box>
      </Box>

    </div>
  )
}