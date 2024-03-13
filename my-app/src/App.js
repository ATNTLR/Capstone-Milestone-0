import React, { useState, useEffect } from "react";
import StockInfo from "./components/StockInfo";

function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [stockHistory, setStockHistory] = useState({});
  const [symbol, setSymbol] = useState("");
  const [quantity, setQuantity] = useState(0);

  const fetchPortfolio = () => {
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/overview")
      .then((response) => response.json())
      .then((data) => {
        setPortfolio(data);
        fetchStockHistory(Object.keys(data.symbols));
      });
  };

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

  const handleAddStock = () => {
    //log to see if the function is called
    console.log("Add Stock button clicked", symbol, quantity);

    fetch(
      `https://mcsbt-integration-antoine.nw.r.appspot.com/modify_portfolio`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          operation: "add",
          symbol: symbol.toUpperCase(),
          quantity: parseInt(quantity, 10),
        }),
      }
    )
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error:", data.error);
        } else {
          setPortfolio(data); //update the portfolio state directly with the returned data (likely temporary)
          console.log("Portfolio after adding stock", data);
        }
      })
      .catch((error) => console.error("Error:", error));
  };

  const handleRemoveStock = () => {
    //log to see if the function is called
    console.log("Remove Stock button clicked", symbol, quantity);

    fetch(
      `https://mcsbt-integration-antoine.nw.r.appspot.com/modify_portfolio`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          operation: "remove",
          symbol: symbol.toUpperCase(),
          quantity: parseInt(quantity, 10),
        }),
      }
    )
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error:", data.error);
        } else {
          setPortfolio(data);
          console.log("Portfolio after removing stock", data);
        }
      })
      .catch((error) => console.error("Error:", error));
  };

  return (
    <div>
      <h1>User Portfolio</h1>
      <h2>Total Portfolio Value: {portfolio && portfolio.total_value}</h2>
      <div>
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
        <button onClick={handleAddStock}>Add Stock</button>
        <button onClick={handleRemoveStock}>Remove Stock</button>
      </div>
      {portfolio &&
        Object.entries(portfolio.symbols).map(([symbol, details]) => (
          <StockInfo
            key={symbol}
            symbol={symbol}
            details={details}
            history={stockHistory[symbol]}
          />
        ))}
    </div>
  );
}

export default App;
