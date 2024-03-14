import React, { useState, useEffect } from "react";
import StockInfo from "./components/StockInfo";
import "./App.css";

function App() {
  //state initialization
  const [portfolio, setPortfolio] = useState(null);
  const [stockHistory, setStockHistory] = useState({});
  const [symbol, setSymbol] = useState("");
  const [quantity, setQuantity] = useState(0);
  const [operation, setOperation] = useState("add");
  const [selectedStock, setSelectedStock] = useState(null); //showing additional info

  const fetchPortfolio = () => {
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/overview")
      .then((response) => response.json())
      .then((data) => {
        setPortfolio(data);
        fetchStockHistory(Object.keys(data.symbols));
      });
  };
  //fetches historical data for every symbol in portfolio
  const fetchStockHistory = (symbols) => {
    symbols.forEach((symbol) => {
      fetch(
        `https://mcsbt-integration-antoine.nw.r.appspot.com/stockinfo/${symbol}`
      )
        .then((response) => response.json())
        .then((history) => {
          setStockHistory((prevState) => ({
            ...prevState,
            [symbol]: history,
          }));
        });
    });
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleModifyPortfolio = () => {
    console.log("Modify Portfolio button clicked", operation, symbol, quantity);

    fetch(
      `https://mcsbt-integration-antoine.nw.r.appspot.com/modifyPortfolio`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          operation: operation.toUpperCase(),
          stock_symbol: symbol.toUpperCase(),
          quantity: parseInt(quantity, 10),
        }),
      }
    )
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => Promise.reject(data.error));
        }
        //refresh portfolio data to show changes
        fetchPortfolio();
      })
      .catch((error) => {
        console.error("Error:", error);
        alert(error); //error message with an alert
      });
  };

  const handleSelectStock = (symbol) => {
    setSelectedStock(stockHistory[symbol]);
  };

  return (
    <div className="app-container">
      <div className="title-total-value">
        <h1>User Portfolio</h1>
        <h2>Total Portfolio Value: {portfolio && portfolio.total_value}</h2>
      </div>
      <div className="modify-portfolio">
        <input
          type="text"
          placeholder="Symbol"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
        />
        <input
          type="number"
          placeholder="Quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />
        <div>
          <label>
            <input
              type="radio"
              value="add"
              checked={operation === "add"}
              onChange={(e) => setOperation(e.target.value)}
            />
            Add
          </label>
          <label>
            <input
              /* ChatGPTreadme 3 radio button help */
              type="radio"
              value="remove"
              checked={operation === "remove"}
              onChange={(e) => setOperation(e.target.value)}
            />
            Remove
          </label>
        </div>
        <button onClick={handleModifyPortfolio}>Modify Portfolio</button>
      </div>
      <div className="stock-list">
        {portfolio &&
          Object.entries(portfolio.symbols).map(([symbol, details]) => (
            <div key={symbol} onClick={() => handleSelectStock(symbol)}>
              <StockInfo
                symbol={symbol}
                details={details}
                history={stockHistory[symbol]}
              />
            </div>
          ))}
      </div>
      {selectedStock && (
        <div className="stock-details">
          {/* nothing to render yet, functionality will come later */}
        </div>
      )}
    </div>
  );
}

export default App;
