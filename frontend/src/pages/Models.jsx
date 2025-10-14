import React, { useEffect, useState } from "react";
import { AuthContext } from "../App";

export default function Models() {
  const { token, apiBase } = React.useContext(AuthContext);
  const [items, setItems] = useState([]);
  const [type, setType] = useState("NB");
  const [name, setName] = useState("");
  const [dataText, setDataText] = useState("{\n  \n}");
  const [error, setError] = useState(null);

  const load = async () => {
    const res = await fetch(`${apiBase}/api/models`, { headers: { "X-Session-Token": token } });
    const data = await res.json();
    if (res.ok) setItems(data);
  };

  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const payload = JSON.parse(dataText);
      const res = await fetch(`${apiBase}/api/models`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-Token": token },
        body: JSON.stringify({ type, name, data: payload, version: "v1" })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to create");
      setName("");
      setDataText("{\n  \n}");
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <h2>Models</h2>
      <form onSubmit={create} style={{ marginBottom: 16 }}>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option>NB</option>
          <option>SB</option>
        </select>
        <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} style={{ marginLeft: 8 }} />
        <div>
          <textarea value={dataText} onChange={(e) => setDataText(e.target.value)} rows={8} style={{ width: "100%", marginTop: 8 }} />
        </div>
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" style={{ marginTop: 8 }}>Upload</button>
      </form>
      <table border="1" cellPadding="6">
        <thead><tr><th>ID</th><th>Type</th><th>Name</th><th>Version</th><th>Created</th></tr></thead>
        <tbody>
          {items.map(m => (
            <tr key={m.id}><td>{m.id}</td><td>{m.type}</td><td>{m.name}</td><td>{m.version}</td><td>{m.created_at}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
