import { useState, useEffect, useRef } from 'react';
import { ListItem, ListItemText, List, Collapse, Checkbox, Stack } from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';


function SubcategoryItem({ text, category, checked, setChecked }) {
  // A helper function to handle the onChange event for the subcategory checkbox
  const handleChange = () => {
    // If the subcategory is in the checked array, remove it and return a new object
    if (checked[category]?.includes(text)) {
      setChecked((prev) => ({
        ...prev,
        [category]: prev[category].filter((item) => item !== text),
      }));
    } else {
      // If the subcategory is not in the checked array, add it and return a new object
      setChecked((prev) => ({
        ...prev,
        [category]: [...(Array.isArray(prev[category]) ? prev[category] : []), text],
      }));
    }
  };

  const isChecked = checked[category]?.includes(text) ? true : false;

  return ( 
    <ListItem sx={{ marginLeft: "5%", padding: 0 }}>
      <Checkbox
        checked={isChecked}
        onChange={handleChange}
      />
      <ListItemText primary={text} primaryTypographyProps={{fontSize: '15px'}} />
    </ListItem>
  );
}

// A custom component that renders a category list item with a toggle
function CategoryItem({ text, subcategories, checked, setChecked }) {
  const [open, setOpen] = useState(false);

  // A helper function to determine the checked state for the category checkbox
  const getCheckedState = () => {
    // Get the number of subcategories that are in the checked array
    const checkedCount = subcategories.filter(subcategory =>
      checked[text]?.includes(subcategory.name)
    ).length;
    // If the number is zero, return "none"
    if (checkedCount === 0) {
      return "none";
    }
    // If the number is equal to the length of the subcategories array, return "all"
    if (checkedCount === subcategories.length) {
      return "all";
    }
    // If the number is between zero and the length of the subcategories array, return "some"
    return "some";
  }

  // A helper function to handle the onChange event for the category checkbox
  const handleChange = () => {
    // Get the current checked state
    const state = getCheckedState();
    // If the current state is "all", set the state to "none" and remove all subcategories from the checked array
    if (state === "all") {
      setChecked((prev) => ({
        ...prev,
        [text]: [],
      }));
    }
    // If the current state is "none" or "some", set the state to "all" and add all subcategories to the checked array
    else {
      setChecked((prev) => ({
        ...prev,
        [text]: subcategories.map((subcategory) => subcategory.name),
      }));
      setOpen(true);
    }
  };

  const handleClick = () => {
    setOpen(!open);
  };

  return (
    <div>
      <ListItem button sx={{ padding: 0 }}>
        <Checkbox
          checked={getCheckedState() === "all"}
          onChange={handleChange}
        />
        <Stack onClick={handleClick} direction="row" alignItems="center" sx={{width: "80%"}}>
          <ListItemText primary={text} />
          {open ? <ExpandLess /> : <ExpandMore />}
        </Stack>
      </ListItem>
      <Collapse in={open} timeout="auto" unmountOnExit>
        <List>
          {subcategories.map((subcategory, index) => (
            <SubcategoryItem
              key={index}
              text={subcategory.name}
              category={text}
              checked={checked}
              setChecked={setChecked}
            />
          ))}
        </List>
      </Collapse>
    </div>
  );
}
  

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


  // The main component that renders the response
  function CategoryList({ categories, setFilters }) {
    // A single state that stores an object with category names as keys and arrays of subcategory names as values
    let [checked, setChecked] = useState(
      categories.reduce(
        (acc, category) => ({ ...acc, [category.name]: [] }),
        {}
      )
    );

    let [num, setNum] = useState(1);

    const checkedHasChanged = useHasChanged(checked);

    const getAllValues = () => {
      // Get an array of the property values of the checked object
      const values = Object.values(checked);
      // Flatten the array of arrays into a single array
      const flattened = values.flat();
      // Return the flattened array
      return flattened;
    };

    useEffect(() => {
    // Only run the effect if checked has changed
    if (checkedHasChanged) {
      console.log(num);
      let selectedCategories = getAllValues();
      console.log("Hello");

      setNum((prev) => {
        return prev + 1;
      });
      setFilters((prevFilters) => {
        return { ...prevFilters, categories: selectedCategories };
      });
    }
  }, [checked, checkedHasChanged]);

    const isEmpty = () => {
      // Get an array of values from the checked object
      const values = Object.values(checked);
      // Return true if every value is an empty array, false otherwise
      return values.every(value => value.length === 0);
    };

    const handleAll = () => {
      // If the checkbox is checked, clear the checked variable and return a new object with empty arrays for each category
      if (!isEmpty()) {
        setChecked(categories.reduce(
          (acc, category) => ({ ...acc, [category.name]: [] }),
          {}
        ));
      }
    };

    console.log(checked)

    return (
      <div style={{ width: "100%" }}>
        {setFilters && (
        <List>
        <ListItem button sx={{padding: 0}}>
        <Checkbox checked={isEmpty()} onChange={handleAll} />
        <ListItemText primary="All categories"/>
        </ListItem> 
          {categories.map((category) => (
            <div>
              <CategoryItem
                key={category._id}
                text={category.name}
                subcategories={category.subcategories}
                checked={checked}
                setChecked={setChecked}
              />
            </div>
          ))}
        </List>
        )}
      </div>
    );
  }


export default CategoryList