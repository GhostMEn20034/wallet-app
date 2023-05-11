import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import { styled } from '@mui/material/styles';
import useAxios from '../utils/useAxios';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';
import Checkbox from '@mui/material/Checkbox';
import { Button, Select, Collapse, List } from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import DeleteIcon from '@mui/icons-material/Delete';
import {FormControl, MenuItem, ListItem, ListItemText } from '@mui/material';
import FormDialog from './AddRecord';
import CircularProgress from '@mui/material/CircularProgress';
import CategoryList from './CategoryFilter';
import AccountFilter from './AccountFilter';


function RecordAmount({recordType, amount}) {
  const recordStyles = {
    "Expense": {color: "red", sign: "-"},
    "Income": {color: "green", sign: ""},
    "Transfer withdrawal": {color: "black", sign: "-"},
    "Transfer income": {color: "black", sign: ""}
  };

  const {color, sign} = recordStyles[recordType];

  return (
  <Typography sx={{display: "flex", color: color, "ml": "auto"}}><b>{sign + amount + " USD"}</b></Typography>
  )
}

export default function RecordHistory() {
  let [data, setData] = useState({});
  let [checked, setChecked] = useState([]);
  let [opened, setOpened] = useState(false);
  let [sortOption, setSortOption] = useState({sortBy: "date", order: "desc"});
  let [openedFilter, setOpenedFilter] = useState(false);
  let [categories, setCategories] = useState([]);
  let [filters, setFilters] = useState({});

  const Item = styled(Paper)(({ theme }) => ({
      backgroundColor: "#f3fffe",
      ...theme.typography.body2,
      padding: theme.spacing(1),
      // textAlign: 'center',
      color: theme.palette.text.secondary,
    }));

  let api = useAxios();

  let getRecords = async () => {

      const qs = require('qs')

      let params = { sort_by: sortOption.sortBy, order: sortOption.order, categories: filters.categories ? filters.categories : undefined,
                     account_ids: filters.accounts ? filters.accounts : undefined };
      let response = await api.get('/records/', {params: params, paramsSerializer: {
        // Use the 'indices' option to remove the brackets
        serialize: params => qs.stringify(params, {indices: false})
      }})

      let data = await response.data;
      setData(data);
  }

  let getCategories = async () => {
    let response = await api.get('/categories/');
    let data = await response.data;

    setCategories(data);

  }


  useEffect(() => {
    console.log(Object.keys(checked));
    console.log(checked)
  }, [checked]);

  useEffect(() => {
    console.log("Hello");
  }, [filters]);

  useEffect(
      () => {
          getRecords();
      }, [sortOption, filters]
  )


  useEffect(
    () => {
        getCategories();
    }, []
)

  // use a function to update both checked and recordId states
  function updateChecked(id) {
    // create a copy of the checked object
    let newChecked = {...checked};
    // toggle the checked state of the checkbox with the given id
    newChecked[id] = !newChecked[id];
    
    if (!newChecked[id]) {
      delete newChecked[id];
    }
    // set the checked state to the new object
    setChecked(newChecked);
  }

  let isSelected = () => {
    let keys = Object.keys(checked);
    return keys.length >= 1;
  }

  let handleClickOpen = () => {
    setOpened(true);
  }

  let handleClose = () => {
    setOpened(false)
  }


  let handleChangeOption = (e) => {

    let sortOptions = [
      {"sortBy": "date", "order": "desc"},
      {"sortBy": "date", "order": "asc"},
      {"sortBy": "amount", "order": "desc"},
      {"sortBy": "amount", "order": "asc"},
    ];

    let selectedOption = e.target.value;

    setSortOption(sortOptions[selectedOption]);
  }

  let getValue = () => {
    // This function returns the value that matches the sortOption state object
    switch (`${sortOption.sortBy}-${sortOption.order}`) {
      case "date-desc":
        return 0;
      case "date-asc":
        return 1;
      case "amount-desc":
        return 2;
      case "amount-asc":
        return 3;
      default:
        return -1; // Return -1 if no match is found
    }
  }

  const deleteRecords = (ids) => {

    let accounts = data.accounts
    // Use the map method to create a new array of data with modified records
    if (sortOption.sortBy === 'date') {
      let newData = data.response.map(item => {
        // For each item in the response array, filter out the records that match the ids
        let newRecords = item.records.filter(record => !ids.includes(record._id));
        // Return a new object with the same date and the new records
        return {...item, records: newRecords};
      });
      // Use the filter method to remove the items that have no records
      let filtered_data = newData.filter(item => item.records.length > 0);
      return {response: filtered_data, accounts: accounts}
    } else {
      let newData = data.response.filter(record => !ids.includes(record._id));
        // Return a new object with the same date and the new records
        return {response: newData, accounts: accounts};
    }
    
  };

  let deleteSelected = async () => {

    let record_data = {
      "record_ids": Object.keys(checked)
    }
    try {
      let response = await api.delete('/records/delete', {data: record_data})
      if (await response.status === 204) {
        let newData = deleteRecords(Object.keys(checked));
        setData(newData);
        setChecked({})
      }
    } catch (error) {
      console.log(error.response)
    }
  }

  let handleClickOnFilter = () => {
    setOpenedFilter(!openedFilter)
  }


  // console.log(data.accounts)
  console.log(filters)
  // console.log(data)

  return (
    <div>
    <Box display="flex">
    {opened && <FormDialog opened={opened} onClose={handleClose} onSubmit={getRecords}/>}
    <Box sx={{bgcolor: "#f5fffe", width: "23%", height: "10%", paddingBottom: "2%", mt: "8.5%", ml: "1%", "borderRadius": "15px", boxShadow: 3}}
    >
      <Button variant='contained' size='small' onClick={handleClickOpen}
      sx={{ml: '22.5%', mt: "10%", mr: "5%", backgroundColor: "#30b864", ":hover": {bgcolor: "#289953", color: "white"}}}>
        <AddCircleOutlineIcon /> &nbsp;Add record
      </Button>
      <Typography sx={{ml: "5%", mt: "5%"}} variant='subtitle1'>
       Sort by:
      </Typography>
      <FormControl sx={{ ml: "5%", width: "90%"}} size="small">
        <Select
          value={getValue()}
          onChange={handleChangeOption}
        >
          <MenuItem value={0}>Creation date (desc)</MenuItem>
          <MenuItem value={1}>Creation date (asc)</MenuItem>
          <MenuItem value={2}>Amount (desc)</MenuItem>
          <MenuItem value={3}>Amount (asc)</MenuItem>
        </Select>
      </FormControl> 
      <Typography sx={{ml: "5%", mt: "5%"}} variant='subtitle1'>
       <b>Filters</b>
      </Typography>
      <List>
      <ListItem direction='row' alignItems='center' onClick={handleClickOnFilter} button>
      <Typography sx={{ml: "5%"}} variant='subtitle1'>
       Categories
      </Typography>
      {openedFilter ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
     
      <Collapse in={openedFilter} timeout="auto">
      {categories && (  
      <CategoryList categories={categories} setFilters={setFilters}/>
      )}
      </Collapse>
      
      <ListItem alignItems='center' width="100%" sx={{padding: 0}}>
      {data.accounts && (<AccountFilter accounts={data.accounts} setFilters={setFilters}/>)}
      </ListItem>
      </List>
    </Box>
    <Box sx={{ mt: "1%", width: '100%'}}>
      
      <Stack sx={{mr: "1.5%"}}>
        <Button variant='contained' size='small' onClick={() => deleteSelected()}
        sx={{backgroundColor: "red", width: "20%", ":hover": {bgcolor: "#db0804", color: "white"}, ml: "80%"}}
        disabled={!isSelected()}>
          <DeleteIcon /> &nbsp;Delete record(s)
        </Button>


        <Stack sx={{mt: "2%"}}>
        {data.response && data.response.map((item, index) => (
          <Stack key={index}>
          { (sortOption.sortBy === 'date') ? (
          <Stack spacing={2} key={`sss-111`} sx={{ml: "5%"}}>
    
          <Typography variant="subtitle1" sx={{color: "#000080", mt: index === 0 ? 0 : 2}}>
          <b>{dayjs(item.date).format("D MMMM YYYY")}</b>
          </Typography>

          {item.records && item.records.map((record) => (
          <Item key={record._id} sx={{mb: "1.5%", display: "flex", alignItems: "center"}}>
          <Checkbox sx={{"width": "2.5%", position: "relative"}} checked={checked[record._id]} onChange={() => {updateChecked(record._id)}} />
          <Typography sx={{ml: "2%", color: "black", width: "15%"}}><b>{record.category}</b></Typography>
          <Typography sx={{ml: "4%"}}>{record.account_name}</Typography>
          <RecordAmount recordType={record.record_type} amount={record.amount}/>
          </Item>
          ))}

          </Stack> ) : (
          <Stack spacing={2} key={`stack-${item._id}`} sx={{ml: "5%"}}>
          <Item key={item._id} sx={{mb: "1.5%", display: "flex", alignItems: "center"}}>
          <Checkbox sx={{"width": "2.5%", position: "relative"}} checked={checked[item._id]} onChange={() => {updateChecked(item._id)}} />
          <Typography sx={{ml: "2%", color: "black", width: "15%"}}><b>{item.category}</b></Typography>
          <Typography sx={{ml: "4%"}}>{item.account_name}</Typography>
          {item.record_type && (<RecordAmount recordType={item.record_type} amount={item.amount}/>)}
          </Item>
          </Stack>
          )
          }
          </Stack>
        ))}
        </Stack>    
      </Stack>
    </Box>
    </Box>
    
    </div>)
  }