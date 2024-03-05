import React, { useState, useEffect } from "react";
import StockInfo from "./components/StockInfo";

//the main app component it manages the state and fetches data for stock portfolio
function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [stockHistory, setStockHistory] = useState({});

  useEffect(() => {
    //fetch the portfolio
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/user1")
      .then((response) => response.json())
      .then((data) => {
        setPortfolio(data);
        fetchStockHistory(Object.keys(data.symbols));
      });
  }, []);
  //fetch historical data for all stocks in portfolio
  const fetchStockHistory = (symbols) => {
    symbols.forEach((symbol) => {
      fetch(
        `https://mcsbt-integration-antoine.nw.r.appspot.com/stockinfo/${symbol}`
      )
        .then((response) => response.json())
        .then((history) => {
          setStockHistory((prevState) => ({ ...prevState, [symbol]: history }));
        });
    });
  };

  return (
    <div>
      <h1>User Portfolio</h1>
      <h2>Total Portfolio Value: {portfolio && portfolio.total_value}</h2>
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
