import React from 'react';
import { Users, Crosshair } from 'lucide-react';

const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
      
      {/* Header Block */}
      <div className="border-b border-cyber-border pb-6 flex flex-col md:flex-row justify-between items-end">
        <div>
           <div className="text-cyber-primary font-mono text-xs uppercase tracking-[0.2em] mb-2">Internal Documentation</div>
           <h1 className="text-3xl md:text-4xl font-display font-bold text-white tracking-tight">
             MISSION DIRECTIVE
           </h1>
        </div>
        <div className="text-right hidden md:block">
           <div className="text-xs text-gray-500 font-mono">CLASSIFICATION: UNCLASSIFIED</div>
           <div className="text-xs text-gray-500 font-mono">DOC ID: CS-GEN-001</div>
        </div>
      </div>

      {/* Strategic Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <h2 className="text-xl font-display font-bold text-white flex items-center gap-2">
            <Crosshair className="text-cyber-accent" size={20} /> Operational Mandate
          </h2>
          <p className="text-gray-400 text-sm leading-relaxed text-justify">
            The CyberSentryAI initiative was established to bridge the capability gap between offensive cyber operations and defensive security analysis. In an ecosystem dominated by static signature detection, adversaries utilize polymorphic vectors and social engineering to bypass perimeter defenses.
          </p>
          <p className="text-gray-400 text-sm leading-relaxed text-justify">
            Our mandate is to deploy a <strong>Neuro-Symbolic Reasoning Engine</strong> capable of emulating adversarial psychology ("Red Team Logic") to identify sophisticated threats that lack historical signatures.
          </p>
        </div>

        <div className="glass-panel p-6 rounded-lg border border-cyber-border bg-black/20">
           <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
             <span className="font-mono text-xs text-cyber-primary uppercase">System Capabilities</span>
             <ActivityIndicator />
           </div>
           <ul className="space-y-3">
             <CapabilityItem label="Adversarial Simulation" desc="Generative modeling of attacker intent and methodology." />
             <CapabilityItem label="Cognitive Fingerprinting" desc="Extraction of 'Cyber DNA' from linguistic and visual artifacts." />
             <CapabilityItem label="Kill Chain Attribution" desc="Mapping of isolated incidents to known threat actor lineages." />
           </ul>
        </div>
      </div>

      {/* Personnel Dossier */}
      <div className="mt-12">
        <div className="flex items-center gap-2 mb-6 border-b border-cyber-border pb-2">
           <Users className="text-cyber-primary" size={20} />
           <h2 className="text-lg font-display font-bold text-white uppercase tracking-wider">Engineering Command</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <PersonnelCard 
            name="Tarun Kumar" 
            role="Lead Architect: Inference Engine" 
            id="TK-001"
            specialty="LLM Integration / Backend Logic"
          />
          <PersonnelCard 
            name="Shivam Singh" 
            role="Lead Architect: User Experience" 
            id="SS-002"
            specialty="Frontend Engineering / Visualization"
          />
          <PersonnelCard 
            name="Yash" 
            role="Systems Intelligence Analyst" 
            id="YA-003"
            specialty="Threat Modeling / Infrastructure"
          />
        </div>
      </div>
    </div>
  );
};

const CapabilityItem = ({ label, desc }: { label: string, desc: string }) => (
  <li className="flex items-start gap-3 text-sm">
    <div className="mt-1.5 w-1.5 h-1.5 bg-cyber-primary rounded-full shadow-[0_0_5px_rgba(6,182,212,0.8)]" />
    <div>
      <strong className="text-gray-200 block font-mono text-xs uppercase">{label}</strong>
      <span className="text-gray-500">{desc}</span>
    </div>
  </li>
);

const PersonnelCard = ({ name, role, id, specialty }: { name: string, role: string, id: string, specialty: string }) => (
  <div className="glass-panel p-5 rounded border border-cyber-border hover:border-cyber-primary/30 transition-all group relative overflow-hidden">
    <div className="absolute top-0 right-0 p-2 opacity-50">
       <div className="text-[10px] font-mono text-cyber-muted">{id}</div>
    </div>
    <div className="flex items-center gap-4 mb-3">
       <div className="w-10 h-10 bg-white/5 rounded border border-white/10 flex items-center justify-center font-bold text-cyber-primary">
         {name.charAt(0)}
       </div>
       <div>
         <div className="text-white font-bold text-sm group-hover:text-cyber-primary transition-colors">{name}</div>
         <div className="text-xs text-gray-500 font-mono">Active Duty</div>
       </div>
    </div>
    <div className="space-y-1 pt-2 border-t border-white/5">
       <div className="text-xs text-gray-400 font-mono uppercase">Role</div>
       <div className="text-sm text-gray-300">{role}</div>
    </div>
    <div className="space-y-1 pt-2">
       <div className="text-xs text-gray-400 font-mono uppercase">Specialization</div>
       <div className="text-xs text-cyber-primary/80">{specialty}</div>
    </div>
  </div>
);

const ActivityIndicator = () => (
    <div className="flex gap-1">
        <div className="w-1 h-3 bg-cyber-primary animate-pulse" />
        <div className="w-1 h-3 bg-cyber-primary animate-pulse delay-75" />
        <div className="w-1 h-3 bg-cyber-primary animate-pulse delay-150" />
    </div>
);

export default AboutPage;