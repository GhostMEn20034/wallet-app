import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import { styled } from '@mui/material/styles';
import useAxios from '../utils/useAxios';
import Typography from '@mui/material/Typography';
import dayjs from 'dayjs';
import Checkbox from '@mui/material/Checkbox';
import { Button } from '@mui/material';


function RecordAmount({recordType, amount}) {
  const recordStyles = {
    "Expense": {color: "red", sign: "-"},
    "Income": {color: "green", sign: ""},
    "Transfer": {color: "black", sign: "-"}
  };

  const {color, sign} = recordStyles[recordType];

  return (
  <Typography sx={{display: "flex", color: color, "ml": "auto"}}><b>{sign + amount}</b></Typography>
  )
}

export default function RecordHistory() {

  let [data, setData] = useState([]);
  let [checked, setChecked] = useState({});

  const Item = styled(Paper)(({ theme }) => ({
      backgroundColor: "#f3fffe",
      ...theme.typography.body2,
      padding: theme.spacing(1),
      // textAlign: 'center',
      color: theme.palette.text.secondary,
    }));

  let api = useAxios();

  let getRecords = async () => {
      let response = await api.get('/records/');
      let data = await response.data;

      setData(data);
  }

  useEffect(() => {
    console.log(Object.keys(checked));
    console.log(checked)
  }, [checked]);

  useEffect(
      () => {
          getRecords();
          console.log(data)
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

  const deleteRecords = (ids) => {
    // Use the map method to create a new array of data with modified records
    let newData = data.map(item => {
      // For each item in the data array, filter out the records that match the ids
      let newRecords = item.records.filter(record => !ids.includes(record._id));
      // Return a new object with the same date and the new records
      return {...item, records: newRecords};
    });
    // Use the filter method to remove the items that have no records
    return newData.filter(item => item.records.length > 0);
  };

  let deleteSelected = async () => {

    let record_data = {
      "record_ids": Object.keys(checked)
    }
    console.log(record_data)
    try {
      let response = await api.delete('/records/delete', {data: record_data})
      if (await response.status === 204) {
        let newData = deleteRecords(Object.keys(checked));
        setData(newData);
        setChecked({})
        console.log(data)
      }
    } catch (error) {
      console.log(error.response.data)
    }
  }

  return (
  <Box sx={{ width: '75%', mt: "1%", "ml": "23%"}}>
    <Stack >
      <Button variant='contained' size='small' onClick={() => deleteSelected()}
      sx={{backgroundColor: "red", width: "20%", ":hover": {bgcolor: "#db0804", color: "white"}, ml: "73%"}}
      disabled={!isSelected()}>
        Delete record(s)
      </Button>
      {data.map(item => (
        <Stack spacing={2} key={item.date} sx={{ml: "10%"}}>
        <Typography variant="subtitle1" sx={{mt: "2%", color: "#000080"}}>
        {dayjs(item.date).format("D MMMM YYYY")}
        </Typography>
        {item.records.map((record) => (
        <Item key={record._id} sx={{mb: "2%", "width": "90%", display: "flex", alignItems: "center"}}>
        <Checkbox sx={{"width": "2%", position: "relative"}} checked={checked[record._id]} onChange={() => {updateChecked(record._id)}} />
        <Typography sx={{ml: "2%", color: "black", width: "15%"}}><b>{record.category}</b></Typography>
        <Typography sx={{ml: "4%"}}>{record.account_name}</Typography>
        <RecordAmount recordType={record.record_type} amount={record.amount}/>
        </Item>
        ))}
        </Stack> 
      ))}
    </Stack>
  </Box>

  )
}