import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DialogTitle from '@mui/material/DialogTitle';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import { Box } from '@mui/material';
import { NumericFormat } from 'react-number-format';
import { InputLabel, Select, MenuItem } from "@mui/material";
import { useState, useEffect } from 'react';
import useAxios from '../utils/useAxios';

const CategorySelect = ({onChoose, onReset, categories}) => {
    // The state variables for the selected category and subcategory
    const [category, setCategory] = useState("");
    const [subcategory, setSubcategory] = useState("");

    // The handler function for changing the category
    const handleCategoryChange = (event) => {
      // Set the category state to the selected value
      setCategory(event.target.value);
      // Reset the subcategory state to an empty string
      setSubcategory("");
      onReset();
    };
  
    // The handler function for changing the subcategory
    const handleSubcategoryChange = (event) => {
      // Set the subcategory state to the selected value
      setSubcategory(event.target.value);
      onChoose(event.target.value);

    };
  
    // The JSX element that renders the select menu
    return (  
      <div>
      {categories && (    
      <div>  
      {!category ? (
        <div>
        <FormControl sx={{"width": "40%", mt: "2%", mr: "2%"}} variant='standard'>
          <InputLabel>Category</InputLabel>
          <Select
            value={category}
            onChange={handleCategoryChange}
          >
            {/* Map over the response data and create a menu item for each category */}
            {categories.map((item) => (
              <MenuItem key={item._id} value={item.name}>
                {item.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        </div>
        ) : null}  
        {/* Only render the subcategory select menu if a category is selected */}
        {category && (
          <div>
          <Button sx={{mt: "4.5%", width: "10px"}} onClick={(e) => {setCategory(""); setSubcategory(""); onReset();}}><ArrowBackIcon sx={{color: "green"}}></ArrowBackIcon></Button>  
          <FormControl sx={{"width": "40%", mt: "2%", mr: "2%"}} variant='standard'>
            <InputLabel id="subcategory-label">Subcategory</InputLabel>
            <Select
              labelId="subcategory-label"
              value={subcategory}
              onChange={handleSubcategoryChange}
            >
              {/* Find the subcategories array that matches the selected category and create a menu item for each subcategory */}
              {categories
                .find((item) => item.name === category)
                .subcategories.map((subitem) => (
                  <MenuItem key={subitem.name} value={subitem.name}>
                    {subitem.name}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
          </div>
        )}
      </div>
      )}
      </div>
    );
  };


export default function FormDialog({opened, onClose, onSubmit, accounts, categories}) {

  let [open, setOpen] = useState(opened);

  let [recordType, setRecordType] = useState("");
  let [from, setFrom] = useState('');
  let [to, setTo] = useState('');
  let [amount, setAmount] = useState(null);
  let [category, setCategory] = useState("");

  let api = useAxios();

  useEffect(() => {
    setTo('');
  }, [from, recordType]);

  let handleFromField = (e) => {
    setFrom(e.target.value)
  }

  let handleToField = (e) => {
    setTo(e.target.value)
  }

  const handleClose = () => {
    onClose();
  };

  let handleAmountChange = (e) => {
    setAmount(e.target.value);
  }

  let handleCategoryChoose = (category) => {
    setCategory(category)
  }


  let isFormValid = () => {
    // Check if the common fields are valid
    let commonValid = recordType.trim() && from.trim() && amount && amount >= 0.01;
    // If the recordType is not Transfer, return the commonValid value
    if (recordType !== "Transfer") return commonValid && category.trim();
    // If the recordType is Transfer, check if the to field is also valid
    let transferValid = to.trim();
    // Return the result of combining the commonValid and transferValid values
    return commonValid && transferValid;
  }

  let createNormalRecord = async () => {
    try {
      let response = await api.post("/records/create", {"account_id": from, 
                                                               "amount": amount, "category": category,
                                                               "record_type": recordType});
      onSubmit();
    } catch (e) {
      console.log("Something went wrong")
    }
  }

  let createTransferRecord = async () => {
    try {
      let response = await api.post("/records/create", {"account_id": from, "receiver": to,
                                                               "amount": amount,
                                                               "record_type": recordType});
      onSubmit();
    } catch (e) {
      console.log("Something went wrong")
    }
  }

  let handleSubmit = () => {
    onClose();
    if (recordType === 'Transfer') {
      createTransferRecord();
    } else {
      createNormalRecord();
    }
  }

  return (
    <div>
    {accounts && (    
    <div>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add record</DialogTitle>
        <DialogContent>
          <FormControl sx={{mt: "5%"}}>
            <FormLabel id="demo-row-radio-buttons-group-label">Record type</FormLabel>
            <RadioGroup
                row
                aria-labelledby="demo-row-radio-buttons-group-label"
                name="row-radio-buttons-group"
                value={recordType}
                onChange={(e) => setRecordType(e.target.value)}
            >
                <FormControlLabel value="Expense" control={<Radio />} label="Expense" />
                <FormControlLabel value="Income" control={<Radio />} label="Income" />
                <FormControlLabel value="Transfer" control={<Radio />} label="Transfer" />
            </RadioGroup>
           </FormControl>
           <FormControl fullWidth sx={{mt: "4%"}}>
                <InputLabel id="account-select-label">{recordType === 'Income' ? "To" : "From"}</InputLabel>
                <Select
                    name="from"
                    value={from}
                    onChange={handleFromField}
                    labelId="account-select-label"
                    id="account-select"
                    label="Account"
                    hidden
                >
                    {accounts.map((account) => (
                    <MenuItem key={account.id} value={account.id}>
                        {account.name}
                    </MenuItem>
                    ))}
                </Select>
            </FormControl>
            {recordType === 'Transfer' && ( // check if the record type is transfer
                <FormControl fullWidth sx={{ mt: '4%' }}>
                    <InputLabel id="account-select-label">To</InputLabel>
                    <Select
                    name="to"
                    value={to}
                    onChange={handleToField}
                    labelId="account-select-label"
                    id="account-select"
                    label="Account"
                    hidden
                    >
                    {accounts
                        .filter((account) => account.id !== from) // filter out the selected account from the first form
                        .map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                            {account.name}
                        </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                )}
          <NumericFormat
            value={amount}
            onChange={handleAmountChange}
            decimalScale={2}
            decimalSeparator="."
            allowNegative={false}
            // Use customInput prop to pass TextField component
            customInput={TextField}
            // Pass any additional props to TextField component
            label="Amount"
            name="amount"
            fullWidth
            variant="standard"
            sx={{"mt": "2%"}}
          />
          <Box sx={{ display: recordType === "Transfer" ? "none" : "block" }}>
          <CategorySelect onChoose={handleCategoryChoose} onReset={() => setCategory("")} categories={categories}/>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant='outlined' sx={{color: "green"}} disabled={!isFormValid()}>Submit</Button>
        </DialogActions>
      </Dialog>
    </div>
    )}
    </div>
  );
}