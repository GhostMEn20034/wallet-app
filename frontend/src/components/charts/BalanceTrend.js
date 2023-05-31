import React from "react";
import { Stack } from "@mui/material";
import { Line } from "react-chartjs-2";
import fillMissingDates from "../../utils/FillMissingData";
import dayjs from "dayjs";
import { 
    LineController, 
    PointElement, 
    LineElement, 
    CategoryScale, 
    LinearScale, 
    Title, 
    Tooltip, 
    Legend,
    Chart
  } from "chart.js"; // import CategoryScale and Chart

  Chart.register(
    LineController, 
    PointElement, 
    LineElement, 
    CategoryScale, 
    LinearScale, 
    Title, 
    Tooltip, 
    Legend
  );



 export default function BalanceChart({data}) {
        console.log(data)
      // Set the start date to the first day of the current month
      let start = dayjs().startOf('month');
      // Set the end date to the last day of the current month
      let end = dayjs().endOf('month');

      data = fillMissingDates(data.current_period, start, end, data.balance, data.account_id)
      
      // Extract the dates and balances from the data
      const dates = data.map((item) => item.date.slice(0, 10));
      const balances = data.map((item) => item.balance);
      
      // Define the chart options
      const options = {
        scales: {
          xAxes: [
            {
              type: "time",
              time: {
                unit: "day",
                displayFormats: {
                  day: "YYYY-MM-DD"
                }
              },
            }
          ],
          x: {
            ticks: {
                autoSkip: true,
                maxRotation: 0,
                callback: function(val, index) {
                    // Hide every 2nd tick label
                    return index % 4 === 0 ? this.getLabelForValue(val) : '';
                  },// it should work
              }
          }
        },
        plugins: {
          legend: {
            labels: {
              usePointStyle: true // make the legend icon circle form
            }
          }
        },
        maintainAspectRatio: false,
      };
      
      // Define the chart data
      const chartData = {
        labels: dates,
        datasets: [
          {
            label: "Balance",
            data: balances,
            fill: false,
            borderColor: "#426cf5",
            backgroundColor: "#426cf5", // change the line color
            pointStyle: "circle", // change the legend icon
            tension: 0.4 // make the line curly
          }
        ]
      };

      return (
        <Stack sx={{height: "300px"}}>
         <Line data={chartData} options={options} />
        </Stack>
      )
 }
// The data provided by the user