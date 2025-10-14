import React, { useEffect, useState } from "react";
import { AuthContext } from "../App";

export default function Mappings() {
  const { token, apiBase } = React.useContext(AuthContext);
  const [nbModels, setNbModels] = useState([]);
  const [sbModels, setSbModels] = useState([]);
  const [mappings, setMappings] = useState([]);
  const [nbId, setNbId] = useState("");
  const [sbId, setSbId] = useState("");
  const [mappingText, setMappingText] = useState(`{
  "protocol": "NETCONF",
  "mappings": [
    { "from": "customer.name", "to": "device.config.customerName" }
  ]
}`);
  const [error, setError] = useState(null);

  const load = async () => {
    const res = await fetch(`${apiBase}/api/models`, { headers: { "X-Session-Token": token } });
    const models = await res.json();
    setNbModels(models.filter(m => m.type === "NB"));
    setSbModels(models.filter(m => m.type === "SB"));
    const mr = await fetch(`${apiBase}/api/mappings`, { headers: { "X-Session-Token": token } });
    setMappings(await mr.json());
  };

  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const md = JSON.parse(mappingText);
      const res = await fetch(`${apiBase}/api/mappings`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-Token": token },
        body: JSON.stringify({ nb_model_id: Number(nbId), sb_model_id: Number(sbId), mapping_data: md })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Failed to create mapping");
      setNbId(""); setSbId("");
      load();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <h2>Mappings</h2>
      <form onSubmit={create}>
        <label>NB Model: </label>
        <select value={nbId} onChange={(e) => setNbId(e.target.value)}>
          <option value="">Select</option>
          {nbModels.map(m => <option key={m.id} value={m.id}>{m.name} (#{m.id})</option>)}
        </select>
        <label style={{ marginLeft: 8 }}>SB Model: </label>
        <select value={sbId} onChange={(e) => setSbId(e.target.value)}>
          <option value="">Select</option>
          {sbModels.map(m => <option key={m.id} value={m.id}>{m.name} (#{m.id})</option>)}
        </select>
        <div>
          <textarea rows={8} style={{ width: "100%", marginTop: 8 }} value={mappingText} onChange={(e) => setMappingText(e.target.value)} />
        </div>
        {error && <div style={{ color: "red" }}>{error}</div>}
        <button type="submit" style={{ marginTop: 8 }}>Create Mapping</button>
      </form>
      <h3 style={{ marginTop: 16 }}>Existing</h3>
      <ul>
        {mappings.map(mp => <li key={mp.id}>#{mp.id} NB:{mp.nb_model_id} -> SB:{mp.sb_model_id} ({mp.created_at})</li>)}
      </ul>
    </div>
  );
}
