import React from "react";

const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: "2rem", color: "#e2e8f0" }}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>Dashboard</h1>
      <p style={{ marginTop: "0.5rem", opacity: 0.8 }}>
        Overview of recent activity and system health.
      </p>
    </div>
  );
};

export default Dashboard;