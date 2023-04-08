import * as React from 'react';
import dayjs from 'dayjs';
import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

export default function BasicDatePicker(props) {
  
const date = new Date("1900-01-01")
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DemoContainer components={['DatePicker']}>
        <DatePicker name='date_picker' minDate={dayjs(date)} maxDate={dayjs(new Date())} label="Date of birth" format='YYYY-MM-DD' {...props} />
      </DemoContainer>
    </LocalizationProvider>
  );
}