import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { CyberDNA, ThreatLevel } from '../types';

interface Props {
  data: CyberDNA;
  threatLevel: ThreatLevel;
}

const CyberDNAChart: React.FC<Props> = ({ data, threatLevel }) => {
  const chartData = [
    { subject: 'Linguistics', A: data.linguistics, fullMark: 100 },
    { subject: 'Urgency', A: data.urgency, fullMark: 100 },
    { subject: 'Impersonation', A: data.impersonation, fullMark: 100 },
    { subject: 'Obfuscation', A: data.obfuscation, fullMark: 100 },
    { subject: 'Visual', A: data.visual, fullMark: 100 },
    { subject: 'Intent', A: data.intent, fullMark: 100 },
  ];

  const isSafe = threatLevel === ThreatLevel.SAFE;
  const mainColor = isSafe ? '#06b6d4' : '#f43f5e'; // Cyan vs Rose
  const fillColor = isSafe ? '#06b6d4' : '#f43f5e';

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-black/90 border border-cyber-primary/30 p-4 rounded-none shadow-[0_0_15px_rgba(6,182,212,0.15)] backdrop-blur-md min-w-[200px]">
          <div className="flex justify-between items-center mb-2 border-b border-white/10 pb-1">
             <p className="text-white font-display font-bold uppercase tracking-wider text-xs">{label}</p>
             <span className={`font-mono font-bold text-xs ${isSafe ? 'text-cyber-primary' : 'text-cyber-accent'}`}>
               {payload[0].value.toFixed(1)}
             </span>
          </div>
          <p className="text-gray-400 text-[10px] leading-relaxed font-mono">
            {getDescription(label)}
          </p>
        </div>
      );
    }
    return null;
  };

  const getDescription = (label: string) => {
    switch (label) {
      case 'Linguistics': return 'NLP analysis of persuasive/coercive patterns.';
      case 'Urgency': return 'Artificial time pressure detection.';
      case 'Impersonation': return 'Brand/Entity mimicry score.';
      case 'Obfuscation': return 'Technical evasion techniques.';
      case 'Visual': return 'Optical character recognition (OCR) anomalies.';
      case 'Intent': return 'Malicious payload severity rating.';
      default: return '';
    }
  };

  return (
    <div className="w-full h-full relative group bg-cyber-panel/20 rounded-xl overflow-hidden border border-white/5">
      
      {/* Background Reticle / HUD Elements */}
      <div className="absolute inset-0 pointer-events-none">
         {/* Center Crosshair */}
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] rounded-full border border-dashed border-white/5"></div>
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] rounded-full border border-white/5"></div>
         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40%] h-[40%] rounded-full border border-dashed border-white/5"></div>
         
         {/* Cross lines */}
         <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1px] h-full bg-gradient-to-b from-transparent via-white/10 to-transparent"></div>
         <div className="absolute top-1/2 left-0 -translate-y-1/2 w-full h-[1px] bg-gradient-to-r from-transparent via-white/10 to-transparent"></div>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#334155" strokeOpacity={0.5} gridType="polygon" />
          
          <PolarAngleAxis 
            dataKey="subject" 
            tick={({ payload, x, y, textAnchor, stroke, radius }) => {
                return (
                  <g className="recharts-layer recharts-polar-angle-axis-tick">
                    <text
                      x={x}
                      y={y}
                      dy={0}
                      textAnchor={textAnchor}
                      fill="#94a3b8"
                      fontSize="10px"
                      fontFamily="Space Grotesk"
                      fontWeight="600"
                      letterSpacing="0.05em"
                      className="uppercase"
                    >
                      {payload.value}
                    </text>
                  </g>
                );
            }}
          />
          
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          
          <Radar
            name="Cyber DNA"
            dataKey="A"
            stroke={mainColor}
            strokeWidth={3}
            fill={fillColor}
            fillOpacity={0.3}
            isAnimationActive={true}
            animationDuration={1500}
            animationEasing="ease-out"
            dot={{ r: 3, fill: '#fff', strokeWidth: 0 }}
            activeDot={{ r: 6, fill: mainColor, stroke: '#fff', strokeWidth: 2 }}
          />
          <Tooltip content={<CustomTooltip />} cursor={false} />
        </RadarChart>
      </ResponsiveContainer>
      
      {/* Decorative corners for that "Tech" look */}
      <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyber-border/50 rounded-tl"></div>
      <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyber-border/50 rounded-tr"></div>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyber-border/50 rounded-bl"></div>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyber-border/50 rounded-br"></div>

      {/* Live Status Indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-2">
         <span className="text-[10px] text-cyber-muted font-mono tracking-widest uppercase opacity-70">Live Analysis</span>
         <div className={`w-1.5 h-1.5 rounded-full ${isSafe ? 'bg-cyber-primary' : 'bg-cyber-accent'} animate-pulse`}></div>
      </div>
    </div>
  );
};

export default CyberDNAChart;
