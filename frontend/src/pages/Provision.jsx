import React, { useEffect, useState } from "react";
import { AuthContext } from "../App";

export default function Provision() {
  const { token, apiBase } = React.useContext(AuthContext);
  const [mappings, setMappings] = useState([]);
  const [nbModels, setNbModels] = useState([]);
  const [mappingId, setMappingId] = useState("");
  const [nbModelId, setNbModelId] = useState("");
  const [nbInline, setNbInline] = useState("{\n  \n}");
  const [useInline, setUseInline] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    const mr = await fetch(`${apiBase}/api/mappings`, { headers: { "X-Session-Token": token } });
    setMappings(await mr.json());
    const res = await fetch(`${apiBase}/api/models`, { headers: { "X-Session-Token": token } });
    const models = await res.json();
    setNbModels(models.filter(m => m.type === "NB"));
  };

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    try {
      const body = { mapping_id: Number(mappingId) };
      if (useInline) {
        body.nb_inline = JSON.parse(nbInline);
      } else {
        body.nb_model_id = Number(nbModelId);
      }
      const res = await fetch(`${apiBase}/api/provision`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-Token": token },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || "Provision failed");
      setResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <h2>Provision</h2>
      <form onSubmit={submit}>
        <label>Mapping</label>
        <select value={mappingId} onChange={(e) => setMappingId(e.target.value)}>
          <option value="">Select mapping</option>
          {mappings.map(m => <option key={m.id} value={m.id}>#{m.id} NB:{m.nb_model_id} -> SB:{m.sb_model_id}</option>)}
        </select>
        <div style={{ marginTop: 8 }}>
          <label>
            <input type="checkbox" checked={useInline} onChange={(e) => setUseInline(e.target.checked)} />
            Use inline NB JSON
          </label>
        </div>
        {useInline ? (
          <textarea rows={8} style={{ width: "100%", marginTop: 8 }} value={nbInline} onChange={(e) => setNbInline(e.target.value)} />
        ) : (
          <select value={nbModelId} onChange={(e) => setNbModelId(e.target.value)} style={{ marginTop: 8 }}>
            <option value="">Select NB model</option>
            {nbModels.map(n => <option key={n.id} value={n.id}>{n.name} (#{n.id})</option>)}
          </select>
        )}
        <button type="submit" style={{ display: "block", marginTop: 8 }}>Trigger</button>
      </form>
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      {result && (
        <div style={{ marginTop: 8 }}>
          <strong>Result:</strong>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
