import React from "react";
import { Dropdown } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

const StockInfo = ({ symbol, details, history = [] }) => {
  return (
    <div>
      <h2>{symbol}</h2>
      <p>Quantity: {details.quantity}</p>
      <p>Value: {details.value}</p>
      {
        // ChatGPTreadme 2, I asked for help to make the dropdown
      }
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
      </Dropdown>
    </div>
  );
};

export default StockInfo;
