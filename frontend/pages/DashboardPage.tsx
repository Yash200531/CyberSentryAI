import React from 'react';
import { getStats, getScans } from '../services/storage';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ShieldAlert, ShieldCheck, Activity, AlertTriangle } from 'lucide-react';
import { ThreatLevel } from '../types';
import { useNavigate } from 'react-router-dom';

const DashboardPage: React.FC = () => {
  const stats = getStats();
  const recentScans = getScans().slice(0, 5);
  const navigate = useNavigate();

  const data = [
    { name: 'Safe', value: stats.safe, color: '#10b981' },
    { name: 'Malicious', value: stats.malicious, color: '#f43f5e' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-display font-bold text-white">Command Center</h1>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Total Scans" value={stats.total} icon={<Activity />} color="text-blue-400" />
        <StatCard title="Threats Detected" value={stats.malicious} icon={<ShieldAlert />} color="text-rose-500" />
        <StatCard title="Safe Content" value={stats.safe} icon={<ShieldCheck />} color="text-emerald-500" />
        <StatCard title="Active Campaigns" value="3" icon={<AlertTriangle />} color="text-yellow-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart */}
        <div className="glass-panel p-6 rounded-xl border border-cyber-border">
          <h3 className="text-xl font-display font-bold text-white mb-6">Threat Distribution</h3>
          <div className="h-[300px] w-full font-mono text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#fff', fontFamily: 'JetBrains Mono' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="glass-panel p-6 rounded-xl border border-cyber-border">
          <h3 className="text-xl font-display font-bold text-white mb-6">Recent Interceptions</h3>
          <div className="space-y-4">
            {recentScans.length === 0 ? (
                <div className="text-center text-gray-500 py-10">No scan data available. Start a scan.</div>
            ) : (
                recentScans.map((scan) => (
                <div 
                    key={scan.id} 
                    onClick={() => navigate(`/app/report/${scan.id}`)}
                    className="flex items-center justify-between p-4 bg-white/5 rounded-lg hover:bg-white/10 cursor-pointer border border-transparent hover:border-cyber-primary/30 transition-all"
                >
                    <div className="flex items-center gap-4">
                    <div className={`w-2 h-12 rounded-full ${
                        scan.threatLevel === ThreatLevel.SAFE ? 'bg-emerald-500' : 
                        scan.threatLevel === ThreatLevel.SUSPICIOUS ? 'bg-yellow-500' : 'bg-rose-500'
                    }`} />
                    <div>
                        <p className="text-white font-medium">{scan.type} SCAN</p>
                        <p className="text-xs text-gray-400 font-mono">{new Date(scan.timestamp).toLocaleDateString()}</p>
                    </div>
                    </div>
                    <div className="text-right">
                    <span className={`text-sm font-bold font-mono ${
                         scan.threatLevel === ThreatLevel.SAFE ? 'text-emerald-400' : 
                         scan.threatLevel === ThreatLevel.SUSPICIOUS ? 'text-yellow-400' : 'text-rose-400'
                    }`}>
                        {scan.threatLevel}
                    </span>
                    <p className="text-xs text-gray-500 font-mono mt-1">Score: {scan.riskScore}</p>
                    </div>
                </div>
                ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard: React.FC<{ title: string, value: number | string, icon: React.ReactNode, color: string }> = ({ title, value, icon, color }) => (
  <div className="glass-panel p-6 rounded-xl border border-cyber-border">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-cyber-muted text-xs font-bold uppercase tracking-wider font-display">{title}</p>
        <h4 className="text-4xl font-display font-bold text-white mt-2 tracking-tight">{value}</h4>
      </div>
      <div className={`p-3 bg-white/5 rounded-lg ${color}`}>
        {icon}
      </div>
    </div>
  </div>
);

export default DashboardPage;