import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Models from "./pages/Models";
import Mappings from "./pages/Mappings";
import Provision from "./pages/Provision";
import AuditLogs from "./pages/AuditLogs";
import NavBar from "./components/NavBar";

const apiBase = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000";

export const AuthContext = React.createContext({ token: null, setToken: () => {} });

function Protected({ children }) {
  const { token } = React.useContext(AuthContext);
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("session_token"));

  useEffect(() => {
    if (token) localStorage.setItem("session_token", token);
    else localStorage.removeItem("session_token");
  }, [token]);

  return (
    <AuthContext.Provider value={{ token, setToken, apiBase }}>
      <BrowserRouter>
        {token && <NavBar />}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/models" element={<Protected><Models /></Protected>} />
          <Route path="/mappings" element={<Protected><Mappings /></Protected>} />
          <Route path="/provision" element={<Protected><Provision /></Protected>} />
          <Route path="/audit" element={<Protected><AuditLogs /></Protected>} />
          <Route path="*" element={<Navigate to={token ? "/models" : "/login"} replace />} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}
