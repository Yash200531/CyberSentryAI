import React from 'react';
import { Lock, GitBranch, Terminal, Server } from 'lucide-react';

const InfoPage: React.FC = () => {
  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
      
      <div className="border-b border-cyber-border pb-4 flex items-center justify-between">
        <div>
             <h1 className="text-2xl font-display font-bold text-white uppercase tracking-wider">Technical Specifications</h1>
             <p className="text-cyber-muted text-xs font-mono mt-1">SYSTEM VERSION 3.0.1 // BUILD: RELEASE_CANDIDATE</p>
        </div>
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded bg-cyber-primary/10 border border-cyber-primary/20">
             <div className="w-2 h-2 rounded-full bg-cyber-success animate-pulse"></div>
             <span className="text-xs font-mono text-cyber-primary">OPERATIONAL</span>
        </div>
      </div>

      {/* Infrastructure Matrix */}
      <div className="space-y-4">
        <h3 className="text-sm font-mono text-gray-500 uppercase flex items-center gap-2">
            <Server size={14} /> Infrastructure Matrix
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <SpecCard title="Interface Layer" items={['React 18 Core', 'TypeScript Strict', 'Tailwind Utility Engine', 'WebGL Rendering']} />
            <SpecCard title="Logic Controller" items={['FastAPI Asynchronous', 'Python 3.11 Runtime', 'Pydantic Validation', 'JWT Security Protocol']} />
            <SpecCard title="Inference Engine" items={['Gemini 3 Pro Model', 'Neuro-Symbolic Logic', 'Tesseract OCR v5', 'FAISS Vector Index']} />
            <SpecCard title="Data Persistence" items={['PostgreSQL Relational', 'Redis Cache Layer', 'JSON Blob Storage', 'Encrypted At-Rest']} />
        </div>
      </div>

      {/* Analysis Protocol */}
      <div className="space-y-4">
         <h3 className="text-sm font-mono text-gray-500 uppercase flex items-center gap-2">
            <GitBranch size={14} /> Analysis Vector Protocol
        </h3>
        <div className="glass-panel border border-cyber-border rounded-lg p-0 overflow-hidden">
             {/* Step 1 */}
             <div className="flex flex-col md:flex-row border-b border-cyber-border/50 last:border-0">
                 <div className="bg-white/5 p-4 md:w-48 shrink-0 border-r border-cyber-border/50 flex flex-col justify-center">
                     <span className="text-cyber-primary font-mono text-xs font-bold">PHASE 01</span>
                     <span className="text-white font-bold text-sm">Ingestion</span>
                 </div>
                 <div className="p-4 text-sm text-gray-400">
                     Raw artifacts (Text, MIME, URL, Binary) are sanitized and decomposed into structural tokens. Metadata is extracted for timestamp and origin verification.
                 </div>
             </div>
             {/* Step 2 */}
             <div className="flex flex-col md:flex-row border-b border-cyber-border/50 last:border-0">
                 <div className="bg-white/5 p-4 md:w-48 shrink-0 border-r border-cyber-border/50 flex flex-col justify-center">
                     <span className="text-cyber-primary font-mono text-xs font-bold">PHASE 02</span>
                     <span className="text-white font-bold text-sm">Adversarial Emulation</span>
                 </div>
                 <div className="p-4 text-sm text-gray-400">
                     The generative model adopts a specific "Red Team" persona constrained by a system instruction set. It evaluates the artifact for psychological levers (urgency, fear, greed) rather than just keyword matching.
                 </div>
             </div>
             {/* Step 3 */}
             <div className="flex flex-col md:flex-row border-b border-cyber-border/50 last:border-0">
                 <div className="bg-white/5 p-4 md:w-48 shrink-0 border-r border-cyber-border/50 flex flex-col justify-center">
                     <span className="text-cyber-primary font-mono text-xs font-bold">PHASE 03</span>
                     <span className="text-white font-bold text-sm">DNA Sequencing</span>
                 </div>
                 <div className="p-4 text-sm text-gray-400">
                     A 6-dimensional vector is generated (Linguistics, Urgency, Impersonation, Obfuscation, Visual, Intent). This "Cyber DNA" hash is computed and compared against the Threat Lineage Database for campaign attribution.
                 </div>
             </div>
        </div>
      </div>

      {/* Compliance Block */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-cyber-border rounded bg-cyber-panel/50">
              <h4 className="text-white text-sm font-bold mb-2 flex items-center gap-2"><Lock size={14} className="text-emerald-500"/> Privacy Assurance</h4>
              <p className="text-xs text-gray-500 leading-relaxed text-justify">
                  This system operates under strict data minimization principles. PII (Personally Identifiable Information) is hashed prior to inference layer transmission. Scan artifacts are siloed within tenant boundaries and are not used for global model training without explicit opt-in.
              </p>
          </div>
          <div className="p-4 border border-cyber-border rounded bg-cyber-panel/50">
              <h4 className="text-white text-sm font-bold mb-2 flex items-center gap-2"><Terminal size={14} className="text-yellow-500"/> Integration Standards</h4>
              <p className="text-xs text-gray-500 leading-relaxed text-justify">
                  Output formats adhere to STIX 2.1 (Structured Threat Information Expression) standards, enabling direct integration with SIEM (Security Information and Event Management) platforms such as Splunk, Sentinel, and QRadar.
              </p>
          </div>
      </div>

    </div>
  );
};

const SpecCard = ({ title, items }: { title: string, items: string[] }) => (
    <div className="border border-cyber-border bg-white/5 p-4 rounded hover:border-cyber-primary/30 transition-colors">
        <div className="text-xs font-mono text-cyber-primary mb-3 uppercase border-b border-white/5 pb-1">{title}</div>
        <ul className="space-y-2">
            {items.map((it, i) => (
                <li key={i} className="text-xs text-gray-300 flex items-start gap-2">
                    <span className="text-cyber-muted/50 select-none">::</span> {it}
                </li>
            ))}
        </ul>
    </div>
);

export default InfoPage;