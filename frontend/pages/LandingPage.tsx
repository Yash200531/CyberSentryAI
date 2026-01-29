import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Cpu, ArrowRight, Radar } from 'lucide-react';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-cyber-dark text-white cyber-grid overflow-hidden relative">
      {/* Navbar */}
      <nav className="relative z-10 px-6 py-6 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <Shield className="w-8 h-8 text-cyber-primary" />
          <span className="font-display font-bold text-xl tracking-widest">CYBER<span className="text-cyber-primary">SENTRY</span>AI</span>
        </div>
        <button 
          onClick={() => navigate('/login')}
          className="px-6 py-2 border border-cyber-primary text-cyber-primary hover:bg-cyber-primary hover:text-black font-display font-bold tracking-wide rounded transition-all shadow-[0_0_10px_rgba(6,182,212,0.4)]"
        >
          ACCESS PORTAL
        </button>
      </nav>

      {/* Hero */}
      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32 text-center md:text-left">
        <div className="flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1 space-y-8">
            <div className="inline-block px-3 py-1 bg-cyber-primary/10 border border-cyber-primary/30 rounded-full text-cyber-primary text-xs font-mono tracking-wide mb-4">
              SYSTEM STATUS: ONLINE // AI MODEL: GEMINI-3-PRO
            </div>
            <h1 className="font-display text-5xl md:text-7xl font-bold leading-tight">
              Think Like an <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-primary to-blue-500">Attacker.</span>
            </h1>
            <p className="text-gray-400 text-lg max-w-xl leading-relaxed font-light">
              The first AI-powered cyber forensics platform that uses "Red Team" reasoning to detect scams, fingerprint threats with Cyber DNA, and explain the kill chain.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
               <button 
                onClick={() => navigate('/login')}
                className="px-8 py-4 bg-cyber-primary text-black font-display font-bold text-lg rounded hover:bg-cyan-300 transition-all shadow-[0_0_20px_rgba(6,182,212,0.5)] flex items-center justify-center gap-2"
              >
                Start Analysis <ArrowRight size={20} />
              </button>
            </div>
          </div>
          
          {/* Animated Visual */}
          <div className="flex-1 w-full relative">
            <div className="relative w-full aspect-square max-w-lg mx-auto">
               {/* Rings */}
               <div className="absolute inset-0 border border-cyber-primary/20 rounded-full animate-[spin_10s_linear_infinite]" />
               <div className="absolute inset-4 border border-cyber-secondary/20 rounded-full animate-[spin_15s_linear_infinite_reverse]" />
               <div className="absolute inset-12 border border-cyber-accent/20 rounded-full animate-[spin_20s_linear_infinite]" />
               
               {/* Center HUD */}
               <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-32 h-32 bg-cyber-panel/80 backdrop-blur border border-cyber-primary rounded-lg flex items-center justify-center shadow-[0_0_30px_rgba(6,182,212,0.2)]">
                    <Shield className="w-16 h-16 text-cyber-primary animate-pulse" />
                  </div>
               </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="border-t border-cyber-border bg-black/40 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-16 grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<Cpu />} 
            title="Red-Team AI" 
            desc="Generative AI that explains the 'why' behind an attack, simulating attacker psychology." 
          />
          <FeatureCard 
            icon={<Lock />} 
            title="Cyber DNA" 
            desc="Fingerprint threats based on linguistics, visual artifacts, and behavioral patterns." 
          />
          <FeatureCard 
            icon={<Radar />} 
            title="Lineage Tracking" 
            desc="Connect isolated incidents to larger campaign groups and threat actors." 
          />
        </div>
      </div>
    </div>
  );
};

const FeatureCard: React.FC<{ icon: React.ReactNode, title: string, desc: string }> = ({ icon, title, desc }) => (
  <div className="p-6 rounded-xl border border-cyber-border bg-white/5 hover:border-cyber-primary/50 transition-colors group">
    <div className="w-12 h-12 bg-cyber-primary/10 rounded-lg flex items-center justify-center text-cyber-primary mb-4 group-hover:scale-110 transition-transform">
      {icon}
    </div>
    <h3 className="text-xl font-display font-bold mb-2 text-white">{title}</h3>
    <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
  </div>
);

export default LandingPage;