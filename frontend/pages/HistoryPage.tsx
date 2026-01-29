import React from 'react';
import { getScans } from '../services/storage';
import { useNavigate } from 'react-router-dom';
import { ThreatLevel } from '../types';
import { FileText, Globe, Image as ImageIcon, Mail, ChevronRight } from 'lucide-react';

const HistoryPage: React.FC = () => {
  const scans = getScans();
  const navigate = useNavigate();

  const getIcon = (type: string) => {
    switch (type) {
        case 'TEXT': return <FileText size={16} />;
        case 'URL': return <Globe size={16} />;
        case 'EMAIL': return <Mail size={16} />;
        case 'IMAGE': return <ImageIcon size={16} />;
        default: return <FileText size={16} />;
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white">Scan Registry</h1>
      
      <div className="glass-panel rounded-xl border border-cyber-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-white/5 text-gray-200 uppercase font-mono text-xs">
              <tr>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Snippet</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Risk Score</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border">
              {scans.length === 0 ? (
                <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                        No records found.
                    </td>
                </tr>
              ) : (
                scans.map((scan) => (
                    <tr key={scan.id} className="hover:bg-white/5 transition-colors group">
                    <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            scan.threatLevel === ThreatLevel.SAFE ? 'bg-emerald-500/10 text-emerald-500' :
                            scan.threatLevel === ThreatLevel.SUSPICIOUS ? 'bg-yellow-500/10 text-yellow-500' :
                            'bg-rose-500/10 text-rose-500'
                        }`}>
                        {scan.threatLevel}
                        </span>
                    </td>
                    <td className="px-6 py-4 flex items-center gap-2 text-white">
                        {getIcon(scan.type)} {scan.type}
                    </td>
                    <td className="px-6 py-4 max-w-xs truncate font-mono text-xs text-gray-500">
                        {scan.contentSnippet}
                    </td>
                    <td className="px-6 py-4">
                        {new Date(scan.timestamp).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 font-mono text-white">
                        {scan.riskScore}/100
                    </td>
                    <td className="px-6 py-4">
                        <button 
                            onClick={() => navigate(`/app/report/${scan.id}`)}
                            className="text-cyber-primary hover:text-white transition-colors"
                        >
                            <ChevronRight />
                        </button>
                    </td>
                    </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;
