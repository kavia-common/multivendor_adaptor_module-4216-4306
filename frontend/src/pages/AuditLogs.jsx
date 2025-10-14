import React, { useEffect, useState } from "react";
import { AuthContext } from "../App";

export default function AuditLogs() {
  const { token, apiBase } = React.useContext(AuthContext);
  const [logs, setLogs] = useState([]);

  const load = async () => {
    const res = await fetch(`${apiBase}/api/admin/audit_logs`, { headers: { "X-Session-Token": token } });
    if (res.ok) setLogs(await res.json());
  };

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: 16 }}>
      <h2>Audit Logs</h2>
      <table border="1" cellPadding="6">
        <thead><tr><th>ID</th><th>Action</th><th>User</th><th>Timestamp</th><th>Details</th></tr></thead>
        <tbody>
          {logs.map(l => (
            <tr key={l.id}>
              <td>{l.id}</td>
              <td>{l.action}</td>
              <td>{l.user_id || "-"}</td>
              <td>{l.timestamp}</td>
              <td><pre style={{ margin: 0 }}>{JSON.stringify(l.details, null, 2)}</pre></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
