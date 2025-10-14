import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../App";

export default function NavBar() {
  const { token, setToken, apiBase } = React.useContext(AuthContext);
  const nav = useNavigate();

  const logout = async () => {
    try {
      await fetch(`${apiBase}/api/auth/logout`, { method: "POST", headers: { "X-Session-Token": token } });
    } catch {}
    setToken(null);
    nav("/login");
  };

  return (
    <div style={{ display: "flex", gap: 12, padding: 8, borderBottom: "1px solid #ddd" }}>
      <Link to="/models">Models</Link>
      <Link to="/mappings">Mappings</Link>
      <Link to="/provision">Provision</Link>
      <Link to="/audit">Audit Logs</Link>
      <div style={{ marginLeft: "auto" }}>
        <button onClick={logout}>Logout</button>
      </div>
    </div>
  );
}
