import { useState } from 'react';
import dayjs from 'dayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { Stack } from '@mui/material';
import { RadioGroup, FormControlLabel, Radio, Grid, Button, Dialog, Box } from "@mui/material";

const shortcutsItems = [
  {
   label: "Own range",
   startDate: null,
   endDate: null,
  },
  {
    label: "Last day",
    startDate:() => dayjs().subtract(1, "day"),
    endDate: () => dayjs(),
  },
  {
    label: "Last 7 days",
    startDate: () => dayjs().subtract(7, "day"),
    endDate: ()=> dayjs(),
  },
  {
    label: "Last 30 days",
    startDate: () => dayjs().subtract(30, "day"),
    endDate: () => dayjs(),
  },
  {
    label: "Current month",
    startDate: () => dayjs().startOf("month"),
    endDate: () => dayjs().endOf("month"),
  },
  {
    label: "Last 90 days",
    startDate: () => dayjs().subtract(90, "day"),
    endDate: () => dayjs(),
  },
  {
    label: "Last 12 months",
    startDate: () => dayjs().subtract(12, "month"),
    endDate: () => dayjs(),
  },
];

  
  export default function DateRangePicker({setFilters}) {
    const [startDate, setStartDate] = useState(dayjs().subtract(30, "day"));
    const [endDate, setEndDate] = useState(dayjs());
    const [radioValue, setRadioValue] = useState(3); // index of Last 30 days
    const [dialogOpen, setDialogOpen] = useState(false);

    
  
    const handleChange = (event) => {
      const index = parseInt(event.target.value);
      setRadioValue(index);
      const selectedItem = shortcutsItems[index];
      if (selectedItem) {
        setStartDate(selectedItem.startDate);
        setEndDate(selectedItem.endDate);
      }
    };
  
    const handleClick = () => {
      setRadioValue(6); // index of Own range
    };

    const handleSubmit = () => {
      // console.log(endDate.with(dayjs()).toISOString())
        if (radioValue === 3) {
          setFilters((prevFilters) => {
            return {...prevFilters, startDate: null, endDate: null}
          })
        } else {
          setFilters((prevFilters) => {
            return { ...prevFilters, startDate: startDate.startOf("day").toISOString(), 
            endDate: endDate.endOf("day").toISOString()};
          })
      }


        setDialogOpen(false)
      };

      const handleOpen = () => {
        setDialogOpen(true); // open dialog on button click
      };
    
      const handleClose = () => {
        setDialogOpen(false); // close dialog on escape or outside click
      };  
      
      let isFormValid = () => {
        return startDate && endDate;
      }

    return (
      <Stack>
      <Button variant="contained" onClick={handleOpen} size='small' sx={{backgroundColor: "#30b864", ":hover": {bgcolor: "#289953", color: "white"}}}>
        {startDate && endDate && radioValue === 0 ? `${startDate.format("MM/DD/YYYY")} - ${endDate.format("MM/DD/YYYY")}` : shortcutsItems[radioValue].label}
      </Button>
      <Dialog open={dialogOpen} onClose={handleClose} sx={{width: "100%"}}>
      <Box padding={3}>  
      <Stack direction="row" mb={2}>
          <Stack sx={{ mr: "20%", width: "35%" }}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
                label='from'
                value={startDate}
                onChange={(date) => {
                  setStartDate(date)
                  setRadioValue(0)
                }}
                onClick={handleClick}
              />
            </LocalizationProvider>
          </Stack>
          <Stack sx={{ width: "35%" }}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DatePicker
                label='to'
                value={endDate}
                onChange={(date) => {
                  setEndDate(date)
                  setRadioValue(0)
                }}
                onClick={handleClick}
              />
            </LocalizationProvider>
          </Stack>
        </Stack>
        <Stack sx={{ width: "100%" }}>
        <RadioGroup
          name="date-range"
          value={radioValue}
          onChange={handleChange}
        >
          <Grid container spacing={2}>
              {shortcutsItems.map((item, index) => (
                <Grid item xs={4} key={item.label}>
                  <FormControlLabel
                    value={index} // use index as value
                    control={<Radio />}
                    label={item.label}
                  />
                </Grid>
              ))}
            </Grid>
        </RadioGroup>
      </Stack>
      <Button sx={{mt: "4%",ml:"35%" ,width: "25%"}} onClick={handleSubmit} variant='contained' disabled={!isFormValid()}>Submit</Button>
      </Box>
     </Dialog>
     </Stack>
    );
  }