import React from "react";

const AdminPanel: React.FC = () => {
  return (
    <div style={{ padding: "2rem", color: "#e2e8f0" }}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>Admin Panel</h1>
      <p style={{ marginTop: "0.5rem", opacity: 0.8 }}>
        Administrative controls and system status.
      </p>
    </div>
  );
};

export default AdminPanel;