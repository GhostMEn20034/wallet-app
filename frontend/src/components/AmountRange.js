import {useState} from "react";
import { NumericFormat } from 'react-number-format';
import { TextField, Stack, Collapse, Typography, ListItem, Button } from "@mui/material";
import { ExpandLess, ExpandMore } from "@mui/icons-material";

export default function AmountRange({setFilters}) {
    const [open, setOpen] = useState(false);
    const [minAmount, setMinAmount] = useState(1);
    const [maxAmount, setMaxAmount] = useState(1);


    let handleMinAmount = (e) => {
        setMinAmount(e.target.value)
        console.log(minAmount)
    }

    let handleMaxAmount = (e) => {
        setMaxAmount(e.target.value)
        console.log(maxAmount)
    }

    let handleReset = () => {
        setMinAmount(1);
        setMaxAmount(1);
        // Uncomment these lines to also reset the filters
        setFilters((prevFilters) => {
          return { ...prevFilters, "minAmount": null, "maxAmount": null };
        });
      }

    let handleClick = () => {
        setOpen(!open)
    }

    let isRangeValid = () => {
        return Number(minAmount) !== null && Number(maxAmount) !== null && Number(maxAmount) > Number(minAmount) && Number(minAmount) > 0;
    }

    console.log(isRangeValid())

    let handleSubmit = () => {
        setFilters((prevFilters) => {
            return { ...prevFilters, "minAmount": minAmount, "maxAmount": maxAmount };
          });
    }

    return(
        <Stack button sx={{width: "100%", mt: "2%", mb: 0, cursor: "pointer"}}>
            <ListItem button sx={{width: "100%"}} onClick={handleClick}>
            <Stack direction="row" alignItems='center' sx={{ml: "5%"}}>
                <Typography>Amount Range</Typography>
                {open ? <ExpandLess /> : <ExpandMore />}
            </Stack>
            </ListItem>
            <Collapse in={open} timeout="auto">
            <Stack sx={{mt: "5%", width: "100%", ml: "5%", color: "f5fffe"}} direction="row">    
            <NumericFormat
            value={minAmount}
            onChange={handleMinAmount}
            decimalScale={0}
            decimalSeparator="."
            allowNegative={false}
            // Use customInput prop to pass TextField component
            customInput={TextField}
            label="Min Amount"
            name="amount"
            fullWidth
            variant="standard"
            sx={{"mt": "2%", ml: "10%", width: "30%"}}
            />
            <NumericFormat
            value={maxAmount}
            onChange={handleMaxAmount}
            decimalScale={0}
            decimalSeparator="."
            allowNegative={false}
            // Use customInput prop to pass TextField component
            customInput={TextField}
            label="Max amount"
            name="amount"
            fullWidth
            variant="standard"
            sx={{"mt": "2%", ml: "10%","width": "30%"}}
            />
            </Stack>
            <Stack direction="row">
            <Button variant="contained" size="small" sx={{mt: "5%",ml: "15%", width: "10%"}}
            onClick={handleReset}
            >Reset</Button>    
            <Button variant="contained" size="small" sx={{mt: "5%", ml: "10%", width: "35%"}}
            onClick={handleSubmit}
            disabled={!isRangeValid()}>Submit</Button>
            </Stack>
            </Collapse>
        </Stack>
    )
}