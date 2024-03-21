import React, { useState } from "react";
import { Dropdown } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const StockInfo = ({ symbol, details, history = [] }) => {
  const [showChart, setShowChart] = useState(false);

  //prepare data for chart.js
  const chartData = {
    labels: history.map(([date]) => date),
    datasets: [
      {
        label: "Closing Price",
        data: history.map(([_, data]) => data["4. close"]),
        borderColor: "rgb(75, 192, 192)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
      },
    ],
  };

  const chartOptions = {
    scales: {
      y: {
        beginAtZero: false,
      },
    },
    elements: {
      line: {
        tension: 0.3,
      },
    },
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        marginBottom: "20px",
      }}
    >
      <div>
        <h2>{symbol}</h2>
        <p>Quantity: {details.quantity}</p>
        <p>Value: ${details.value}</p>
        <button
          onClick={() => setShowChart(!showChart)}
          className="btn btn-info mb-2"
        >
          Toggle Chart
        </button>
        <Dropdown>
          <Dropdown.Toggle variant="success" id={`dropdown-${symbol}`}>
            Historical Data
          </Dropdown.Toggle>

          <Dropdown.Menu
            style={{ padding: 0, maxWidth: "100%", overflowY: "scroll" }}
          >
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Open</th>
                  <th>High</th>
                  <th>Low</th>
                  <th>Close</th>
                  <th>Volume</th>
                </tr>
              </thead>
              <tbody>
                {history.map(([date, data], index) => (
                  <tr key={index}>
                    <td>{date}</td>
                    <td>{data["1. open"]}</td>
                    <td>{data["2. high"]}</td>
                    <td>{data["3. low"]}</td>
                    <td>{data["4. close"]}</td>
                    <td>{data["5. volume"]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Dropdown.Menu>
          {
            // ChatGPTreadme 2, I asked for help to make the dropdown
          }
        </Dropdown>
      </div>
      {showChart && (
        <div style={{ width: "400px", height: "300px" }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      )}
    </div>
  );
};

export default StockInfo;
