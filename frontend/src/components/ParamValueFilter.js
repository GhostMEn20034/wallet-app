import { useState, useRef, useEffect } from 'react';
import { ListItem, ListItemText, List, Collapse, Checkbox, Stack } from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';


function useHasChanged(value) {
    // Store the previous value in a ref
    const prevValue = useRef(value);
    // Compare the current and previous values
    const hasChanged = prevValue.current !== value;
    // Update the ref with the current value
    prevValue.current = value;
    // Return the result
    return hasChanged;
  }
  

export default function ParamValueFilter ({filterNameVisible,filterNameInner ,objects, setFilters}) {
    let [open, setOpen] = useState(false);


    let [checked, setChecked] = useState([]);
    
    const checkedHasChanged = useHasChanged(checked);

    
    useEffect(() => {
        // Only run the effect if checked has changed
        if (checkedHasChanged) {
        //   console.log(num);
          let selectedValues = checked;
          console.log("Hello");
    
        //   setNum((prev) => {
        //     return prev + 1;
        //   });
          setFilters((prevFilters) => {
            return { ...prevFilters, [filterNameInner]: selectedValues };
          });
        }
      }, [checked, checkedHasChanged]);  
    
    
    const isEmpty = () => {
        // Return true if the checked array is empty, false otherwise
        return checked.length === 0;
      };
    
    const handleAll = () => {
        // If the checkbox is checked, clear the checked array
        if (!isEmpty()) {
          setChecked([]);
        }
      };

    let handleClick = () => {
        setOpen(!open)
    }

    const handleChange = (id) => (event) => {
        // If the id is in the checked array, remove it and return a new array
        if (checked.includes(id)) {
          setChecked((prev) => prev.filter((item) => item !== id));
        } else {
          // If the id is not in the checked array, add it and return a new array
          setChecked((prev) => [...prev, id]);
        }
      };

    console.log(checked)
    return (
        <Stack sx={{width: "100%"}}>
            <List sx={{py: 0}}>
            <ListItem button sx={{width: "100%"}} onClick={handleClick}>
            <Stack direction="row" alignItems='center' sx={{ml: "5%"}}>
                <ListItemText primary={filterNameVisible.charAt(0).toUpperCase() + filterNameVisible.slice(1)} />
                {open ? <ExpandLess /> : <ExpandMore />}
            </Stack>
            </ListItem>
            <Collapse in={open} timeout="auto">
            <List>
                <ListItem sx={{ marginLeft: "5%", padding: 0 }}>
                <Checkbox checked={isEmpty()} onChange={handleAll} />
                <ListItemText primary={"All " + `${filterNameVisible}`} primaryTypographyProps={{fontSize: '15px'}} />
                </ListItem>
                {objects.map((obj) => (
                    <ListItem sx={{ marginLeft: "5%", padding: 0 }}>
                    <Checkbox checked={checked.includes(obj.id)} onChange={handleChange(obj.id)} />
                    <ListItemText primary={obj.name} primaryTypographyProps={{fontSize: '15px'}} />
                    </ListItem>
                ))}
                
            </List>
            </Collapse>
            </List>
        </Stack>
  );
}
