import dayjs from "dayjs";

export default function fillMissingDate(data, start_date, end_date, defaultBalance, defaultAccountId) {

    let output = [];
    // Get the account_id from the first object in the data array
    let account_id = data[0].account_id ? data[0].account_id : defaultAccountId;
    // Get the balance from the first object in the data array
    let first_balance = data[0].balance ? data[0].balance : defaultBalance;
    // Get the balance from the last object in the data array
    let last_balance = data[data.length - 1].balance ? data[data.length-1].balance : defaultBalance;;
    // Loop through the days from start to end
    while (start_date <= end_date) {
    // Format the date as YYYY-MM-DD
    let date = start_date
    // Find the matching object in the data array using dayjs()
    let match = data.find((item) => dayjs(item.date).isSame(date, 'day'));
    // If there is a match, push it to the output array and execute some things
    if (match) {
    output.push(match);
    // Execute some things here
    console.log('Match found for ' + date);
    } else {
    // Otherwise, check if the date is less than or greater than the dates in the data array
    if (dayjs(start_date).isBefore(dayjs(data[0].date, 'day').startOf('day'))) {
    // If the date is less than the first date in the data array, push a new object with the first balance
    output.push({ account_id: account_id, balance: first_balance, date: dayjs(date).format("YYYY-MM-DD") });
    } else if (dayjs(start_date).isAfter(dayjs(data[data.length - 1].date).startOf('day'))) {
    // If the date is greater than the last date in the data array, push a new object with the last balance
    output.push({ account_id: account_id, balance: last_balance, date: dayjs(date).format("YY-MM-DD") });
    }
    }
    // Increment the start date by one day
    start_date = start_date.add(1, "day")
    }
    // Return the output array
    console.log(output)
    return output;
   }