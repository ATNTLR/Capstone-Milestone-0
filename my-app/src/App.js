import React, { useState, useEffect } from "react";
import StockInfo from "./components/StockInfo";
import "./App.css";

function App() {
  //state initialization
  const [portfolio, setPortfolio] = useState({ total_value: 0, symbols: {} });
  const [stockHistory, setStockHistory] = useState({});
  const [symbol, setSymbol] = useState("");
  const [quantity, setQuantity] = useState(0);
  const [operation, setOperation] = useState("add");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showRegister, setShowRegister] = useState(false);

  const fetchPortfolio = () => {
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/overview", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        setPortfolio(data);
        //check if symbols is defined before fetching stock history
        if (data.symbols) {
          const symbols = Object.keys(data.symbols);
          if (symbols.length > 0) {
            fetchStockHistory(symbols);
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching portfolio:", error);
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
    if (isLoggedIn) {
      fetchPortfolio();
    } else {
      setPortfolio({ total_value: 0, symbols: {} });
    }
  }, [isLoggedIn]);

  const handleLogin = (event) => {
    event.preventDefault();
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/login", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          setIsLoggedIn(true);
        } else {
          alert(data.error);
        }
      })
      .catch((error) => {
        console.error("Login error:", error);
      });
  };

  const handleLogout = () => {
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/logout", {
      method: "GET",
      credentials: "include",
    })
      .then((response) => response.json())
      .then((data) => {
        setIsLoggedIn(false);
        console.log(data.message);
      })
      .catch((error) => {
        console.error("Logout error:", error);
      });
  };

  const handleRegister = (event) => {
    event.preventDefault();
    //check if passwords match
    if (password !== confirmPassword) {
      alert("Passwords don't match");
      return;
    }
    fetch("https://mcsbt-integration-antoine.nw.r.appspot.com/register", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          console.log("Registration successful:", data);
          setShowRegister(false); //switch back to the login form or directly log in the user
        } else {
          alert(data.error);
        }
      })
      .catch((error) => {
        console.error("Registration error:", error);
      });
  };

  const handleModifyPortfolio = () => {
    console.log("Modify Portfolio button clicked", operation, symbol, quantity);

    fetch(
      `https://mcsbt-integration-antoine.nw.r.appspot.com/modifyPortfolio`,
      {
        method: "POST",
        credentials: "include",
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

  return (
    <div className="app-container">
      {!isLoggedIn ? (
        <>
          {showRegister ? (
            <form onSubmit={handleRegister}>
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <input
                type="password"
                placeholder="Re-enter Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <button type="submit">Register</button>
              <button onClick={() => setShowRegister(false)}>
                Back to Login
              </button>
            </form>
          ) : (
            <>
              <form onSubmit={handleLogin}>
                <input
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">Login</button>
              </form>
              <button onClick={() => setShowRegister(true)}>
                Need an account? Register
              </button>
            </>
          )}
        </>
      ) : (
        <>
          <div className="header-area">
            <div className="left-header">
              <h1>User Portfolio</h1>
              <h2>
                Total Portfolio Value: {portfolio && portfolio.total_value}
              </h2>
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
                    /* ChatGPTreadme 3 radio button help */
                    type="radio"
                    value="add"
                    checked={operation === "add"}
                    onChange={(e) => setOperation(e.target.value)}
                  />{" "}
                  Add
                </label>
                <label>
                  <input
                    type="radio"
                    value="remove"
                    checked={operation === "remove"}
                    onChange={(e) => setOperation(e.target.value)}
                  />{" "}
                  Remove
                </label>
              </div>
              <button onClick={handleModifyPortfolio}>Modify Portfolio</button>
            </div>
          </div>
          <div className="stock-list">
            {portfolio &&
              portfolio.symbols &&
              Object.entries(portfolio.symbols).map(([symbol, details]) => (
                <div key={symbol}>
                  <StockInfo
                    symbol={symbol}
                    details={details}
                    history={stockHistory[symbol]}
                  />
                </div>
              ))}
            <button onClick={handleLogout}>Logout</button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
