import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getScans } from '../services/storage';
import { exportToJSON, exportToCSV, exportToPDF } from '../services/exportService';
import { ThreatLevel } from '../types';
import CyberDNAChart from '../components/CyberDNAChart';
import { AlertOctagon, CheckCircle, Fingerprint, BrainCircuit, Share2, ArrowLeft, Download, FileJson, FileText, FileSpreadsheet } from 'lucide-react';

const ReportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const scans = getScans();
  const scan = scans.find(s => s.id === id);
  const [showExportMenu, setShowExportMenu] = useState(false);

  if (!scan) return <div className="text-white">Report not found.</div>;

  const isSafe = scan.threatLevel === ThreatLevel.SAFE;
  
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
      {/* Navigation & Header */}
      <div className="flex justify-between items-center">
        <button 
            onClick={() => navigate(-1)}
            className="flex items-center text-cyber-muted hover:text-white transition-colors text-sm font-medium"
        >
            <ArrowLeft size={16} className="mr-2" /> Back to History
        </button>
        
        <div className="relative">
            <button 
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="flex items-center gap-2 px-4 py-2 bg-cyber-primary/10 text-cyber-primary border border-cyber-primary/30 rounded hover:bg-cyber-primary hover:text-black transition-all font-display font-bold text-sm"
            >
                <Download size={16} /> EXPORT INTEL
            </button>
            {showExportMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-cyber-panel border border-cyber-border rounded-lg shadow-xl z-50 overflow-hidden">
                    <button onClick={() => exportToPDF(scan)} className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/10 flex items-center gap-2">
                        <FileText size={16} className="text-red-400" /> PDF Report
                    </button>
                    <button onClick={() => exportToCSV(scan)} className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/10 flex items-center gap-2 border-t border-cyber-border/50">
                        <FileSpreadsheet size={16} className="text-green-400" /> CSV Data
                    </button>
                    <button onClick={() => exportToJSON(scan)} className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-white/10 flex items-center gap-2 border-t border-cyber-border/50">
                        <FileJson size={16} className="text-yellow-400" /> JSON (STIX)
                    </button>
                </div>
            )}
        </div>
      </div>

      {/* Header Risk Banner */}
      <div className={`glass-panel p-8 rounded-2xl border-2 flex flex-col md:flex-row items-center justify-between ${
        isSafe ? 'border-emerald-500/30 bg-emerald-900/10' : 'border-rose-500/30 bg-rose-900/10'
      }`}>
        <div className="flex items-center gap-6">
          <div className={`w-20 h-20 rounded-full flex items-center justify-center border-4 ${
             isSafe ? 'border-emerald-500 text-emerald-500' : 'border-rose-500 text-rose-500'
          }`}>
            {isSafe ? <CheckCircle size={40} /> : <AlertOctagon size={40} />}
          </div>
          <div>
            <h2 className="text-3xl font-display font-bold text-white tracking-tight">{scan.threatLevel} DETECTED</h2>
            <div className="flex items-center gap-2 mt-1">
                <span className="text-gray-400 text-sm">RISK SCORE:</span>
                <span className={`font-mono text-xl font-bold ${isSafe ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {scan.riskScore}/100
                </span>
            </div>
          </div>
        </div>
        <div className="mt-6 md:mt-0 text-right">
           <div className="text-sm text-cyber-muted font-mono mb-2">SCAN ID: <span className="text-white">{scan.id.substring(0,8)}</span></div>
           <div className="inline-block px-4 py-1 rounded bg-black/50 border border-cyber-border text-white font-mono text-xs tracking-wider uppercase">
             {scan.type} ANALYSIS
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COL: Red Team Intel */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Red Team Panel */}
          <div className="glass-panel p-1 rounded-2xl border border-cyber-primary/30 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyber-primary to-transparent opacity-50" />
            
            <div className="bg-black/40 p-6 rounded-xl">
               <div className="flex items-center gap-3 mb-6">
                 <BrainCircuit className="text-cyber-primary" />
                 <h3 className="text-xl font-display font-bold text-white tracking-wide">RED-TEAM INTELLIGENCE</h3>
               </div>

               <div className="space-y-6">
                 <div className="p-4 bg-white/5 rounded-lg border-l-2 border-cyber-secondary">
                    <span className="text-xs font-bold text-cyber-secondary uppercase tracking-wider block mb-1 font-display">Attacker Goal</span>
                    <p className="text-gray-200 leading-relaxed">{scan.redTeamReport.attackGoal}</p>
                 </div>

                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-white/5 rounded-lg border-l-2 border-purple-500">
                        <span className="text-xs font-bold text-purple-500 uppercase tracking-wider block mb-1 font-display">Psychology Exploited</span>
                        <p className="text-gray-300 text-sm">{scan.redTeamReport.psychologyExploited}</p>
                    </div>
                    <div className="p-4 bg-white/5 rounded-lg border-l-2 border-orange-500">
                        <span className="text-xs font-bold text-orange-500 uppercase tracking-wider block mb-1 font-display">Target Victim Profile</span>
                        <p className="text-gray-300 text-sm">{scan.redTeamReport.victimProfile}</p>
                    </div>
                 </div>

                 <div>
                    <span className="text-xs font-bold text-cyber-accent uppercase tracking-wider block mb-3 font-display">Attack Kill Chain</span>
                    <div className="space-y-2">
                        {scan.redTeamReport.exploitationChain.map((step, idx) => (
                            <div key={idx} className="flex items-start gap-3">
                                <div className="min-w-[24px] h-6 rounded-full bg-cyber-accent/20 text-cyber-accent flex items-center justify-center text-xs font-mono font-bold mt-0.5">
                                    {idx + 1}
                                </div>
                                <p className="text-gray-300 text-sm">{step}</p>
                            </div>
                        ))}
                    </div>
                 </div>
               </div>
            </div>
          </div>

          {/* Content Preview */}
          <div className="glass-panel p-6 rounded-xl border border-cyber-border">
            <h3 className="text-lg font-display font-bold text-white mb-4">Analyzed Artifact</h3>
            <div className="bg-black/50 p-4 rounded border border-cyber-border font-mono text-xs text-gray-400 overflow-auto max-h-48 whitespace-pre-wrap leading-relaxed">
              {scan.contentSnippet}
            </div>
          </div>
        </div>

        {/* RIGHT COL: Cyber DNA */}
        <div className="space-y-8">
            <div className="glass-panel p-6 rounded-xl border border-cyber-border flex flex-col h-[500px]">
                <div className="flex items-center gap-2 mb-6 text-cyber-primary shrink-0">
                    <Fingerprint />
                    <h3 className="text-lg font-display font-bold text-white">CYBER DNA</h3>
                </div>

                <div className="flex-1 w-full relative font-mono text-xs">
                   <CyberDNAChart data={scan.cyberDNA} threatLevel={scan.threatLevel} />
                </div>

                <div className="mt-6 space-y-4 shrink-0">
                    <div>
                        <span className="text-xs text-gray-500 uppercase font-bold tracking-wider">Fingerprint Hash</span>
                        <div className="font-mono text-cyber-primary text-sm break-all bg-black/30 p-2 rounded border border-cyber-border/50 mt-1">
                            {scan.cyberDNA.fingerprintHash || "N/A"}
                        </div>
                    </div>
                    <div>
                         <span className="text-xs text-gray-500 uppercase font-bold tracking-wider">Lineage / Similar Campaigns</span>
                         <div className="mt-2 flex flex-wrap gap-2">
                            {scan.cyberDNA.similarCampaigns.length > 0 ? (
                                scan.cyberDNA.similarCampaigns.map((camp, i) => (
                                    <span key={i} className="px-2 py-1 bg-white/5 text-xs font-mono text-gray-300 rounded border border-white/10">{camp}</span>
                                ))
                            ) : <span className="text-xs text-gray-500 font-mono">No known lineage matches.</span>}
                         </div>
                    </div>
                </div>
            </div>
        </div>

      </div>
    </div>
  );
};

export default ReportPage;
