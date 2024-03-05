import React from "react";
import { Dropdown } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

//dropdown inspired from GPT, 2 in doc
//history prop defaults to empty array to handle history data not immediately available
const StockInfo = ({ symbol, details, history = [] }) => {
  return (
    <div>
      <h2>{symbol}</h2>
      <p>Quantity: {details.quantity}</p>
      <p>Value: {details.value}</p>
      <Dropdown>
        <Dropdown.Toggle variant="success" id="dropdown-basic">
          Historical Data
        </Dropdown.Toggle>

        <Dropdown.Menu style={{ maxHeight: "300px", overflowY: "scroll" }}>
          {history?.map(([date, data], index) => (
            <Dropdown.Item key={index} as="div">
              <p>
                <strong>Date:</strong> {date}
              </p>
              <p>
                <strong>Open:</strong> {data["1. open"]}
              </p>
              <p>
                <strong>High:</strong> {data["2. high"]}
              </p>
              <p>
                <strong>Low:</strong> {data["3. low"]}
              </p>
              <p>
                <strong>Close:</strong> {data["4. close"]}
              </p>
              <p>
                <strong>Volume:</strong> {data["5. volume"]}
              </p>
              <hr />
            </Dropdown.Item>
          ))}
        </Dropdown.Menu>
      </Dropdown>
    </div>
  );
};

export default StockInfo;
