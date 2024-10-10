# Wallet APP
### This web application provides a comprehensive platform for users to manage their personal finances effectively. Key features include:

 - Transaction Tracking: Record and categorize various types of transactions (expenses, income, etc.).
 - Currency Conversion: Automatically convert transactions to different currencies using the [Exchange Rate API](https://www.exchangerate-api.com/).
 - Analytics: Gain insights into spending patterns and financial health through detailed analytics.
 - User Management: Create accounts, manage personal information, and reset passwords.
 - Record Filtering: Filter transactions by various criteria, including date range, amount, category, and type (expense, income).

# Setup
### 1. Connect to your MongoDB Atlas cluster.
### 2. Create Database trigger with the following code:
```js
exports = function(changeEvent) {
  // Get the _id of the document that was changed
  const docId = changeEvent.documentKey._id;

  // Get the operation type of the change event
  const opType = changeEvent.operationType;

  // Get the updated balance of the document
  const updatedBalance = changeEvent.fullDocument.balance;

  // Get the current date
  let today = new Date();
  
  today.setHours(0, 0, 0, 0);

  // Create a new Date object for tomorrow by adding one day to today
  var tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  
  // Assign the startDate and endDate variables
  var startDate = today;
  var endDate = tomorrow;

  // Connect to the balance history collection
  const historyCollection = context.services.get("mongodb-atlas").db("wallet").collection("balanceTrend");

  // If the operation type is insert or update, update or create a document in the balance history collection with the _id, balance, and date
  if (opType === "insert") {
    historyCollection.insertOne({
      account_id: docId,
      balance: updatedBalance,
      date: new Date(),
      initial: true
    })
    .then(result => {
      console.log(`Successfully inserted item with _id: ${result.insertedId}`);
    })
    .catch(err => {
      console.error(`Failed to insert item: ${err}`);
    })
  }

  // If the operation type is update, update or create a document in the balance history collection with the _id, balance, and date
  if (opType === "update") {
    historyCollection.updateOne({
      account_id: docId,
      date: {
        $gte: startDate,
        $lt: endDate
      },
      initial: false
    }, {
      $set: {
        balance: updatedBalance,
        date: new Date(),
      }
    }, {
      upsert: true
    })
    .then(result => {
      console.log(`Successfully matched ${result.matchedCount} and modified ${result.modifiedCount} items.`);
    })
    .catch(err => {
      console.error(`Failed to update item: ${err}`);
    })
  }
};
```
### 3. Insert the data to `categories` collection from json file

### 4. Insert the data to `currencies` collection from json file

### 5. Go to `backend` directory.
### 6. Create `.env` file:
```sh
URL=Mongo_DB_URL # Your MongoDB Atlas cluster URL
ACCESS_SECRET_KEY=ACCESS_SECRET_KEY # Secret key for JWT Access Token
REFRESH_SECRET_KEY=REFRESH_SECRET_KEY # Secret key for JWT Refresh Token
ALGORITHM=ALGORITHM # JWT Token's encode/decode Algorithm
SERVICE_SID=SERVICE_SID # The id of Sign up Service in Twilio
SERVICE_SID_RESET_PWD=SERVICE_SID_RESET_PWD # The id of Reset Password Service in Twilio
ACCOUNT_SID=ACCOUNT_SID # Twilio user's ID  (You can find it on main Twilio's Dashboard)
TWILIO_AUTH_TOKEN=TWILIO_AUTH_TOKEN # Twilio Auth Token (You can find it on main Twilio's Dashboard)
EXCHANGE_RATE_API_KEY=EXCHANGE_RATE_API_KEY # Your API key from https://www.exchangerate-api.com website
```
### 7. Run the command:
```bash
docker compose up -d --build
```

### 8. Go to the following URL
http://localhost:8000
