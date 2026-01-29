import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { ScanResult, ThreatLevel } from '../types';

export const exportToJSON = (scan: ScanResult) => {
  const dataStr = JSON.stringify(scan, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
  const exportFileDefaultName = `SENTRY_INTEL_${scan.id.substring(0,8)}.json`;

  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
};

export const exportToCSV = (scan: ScanResult) => {
  const headers = [
    'ScanID', 'Date', 'Type', 'RiskScore', 'ThreatLevel', 
    'Linguistics', 'Urgency', 'Impersonation', 'Obfuscation', 'Visual', 'Intent',
    'AttackGoal', 'Confidence'
  ];
  
  const row = [
    scan.id,
    scan.timestamp,
    scan.type,
    scan.riskScore,
    scan.threatLevel,
    scan.cyberDNA.linguistics,
    scan.cyberDNA.urgency,
    scan.cyberDNA.impersonation,
    scan.cyberDNA.obfuscation,
    scan.cyberDNA.visual,
    scan.cyberDNA.intent,
    `"${scan.redTeamReport.attackGoal.replace(/"/g, '""')}"`, // Escape quotes
    scan.redTeamReport.confidenceScore
  ];

  const csvContent = "data:text/csv;charset=utf-8," 
    + headers.join(",") + "\n" + row.join(",");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `SENTRY_INTEL_${scan.id.substring(0,8)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const exportToPDF = (scan: ScanResult) => {
  const doc = new jsPDF();
  const primaryColor = '#06b6d4';
  const dangerColor = '#f43f5e';
  const isSafe = scan.threatLevel === ThreatLevel.SAFE;

  // Header
  doc.setFillColor(5, 10, 20); // Dark BG
  doc.rect(0, 0, 210, 20, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.text("CYBER SENTRY // THREAT INTELLIGENCE REPORT", 10, 13);
  doc.setFontSize(8);
  doc.text(`GENERATED: ${new Date().toISOString()}`, 150, 13);

  // Executive Summary
  doc.setTextColor(0, 0, 0);
  doc.setFontSize(18);
  doc.text(`${scan.threatLevel} THREAT DETECTED`, 10, 35);
  
  doc.setDrawColor(isSafe ? 16 : 244, isSafe ? 185 : 63, isSafe ? 129 : 94); // Border color based on threat
  doc.setLineWidth(1);
  doc.line(10, 38, 200, 38);

  doc.setFontSize(10);
  doc.text(`SCAN ID: ${scan.id}`, 10, 45);
  doc.text(`RISK SCORE: ${scan.riskScore}/100`, 10, 50);
  doc.text(`TYPE: ${scan.type}`, 80, 50);
  doc.text(`CONFIDENCE: ${scan.redTeamReport.confidenceScore * 100}%`, 140, 50);

  // Red Team Table
  autoTable(doc, {
    startY: 60,
    head: [['Red-Team Intelligence', 'Analysis']],
    body: [
      ['Attack Goal', scan.redTeamReport.attackGoal],
      ['Victim Profile', scan.redTeamReport.victimProfile],
      ['Psychology', scan.redTeamReport.psychologyExploited],
      ['Next Moves', scan.redTeamReport.nextMoves],
    ],
    theme: 'grid',
    headStyles: { fillColor: isSafe ? [16, 185, 129] : [244, 63, 94] },
  });

  // Cyber DNA Table
  const finalY = (doc as any).lastAutoTable.finalY || 100;
  
  doc.setFontSize(12);
  doc.text("Cyber DNA Fingerprint", 10, finalY + 15);

  autoTable(doc, {
    startY: finalY + 20,
    head: [['Trait', 'Score (0-100)', 'Severity']],
    body: [
      ['Linguistics', scan.cyberDNA.linguistics, getSeverity(scan.cyberDNA.linguistics)],
      ['Urgency', scan.cyberDNA.urgency, getSeverity(scan.cyberDNA.urgency)],
      ['Impersonation', scan.cyberDNA.impersonation, getSeverity(scan.cyberDNA.impersonation)],
      ['Obfuscation', scan.cyberDNA.obfuscation, getSeverity(scan.cyberDNA.obfuscation)],
      ['Visual Deception', scan.cyberDNA.visual, getSeverity(scan.cyberDNA.visual)],
      ['Malicious Intent', scan.cyberDNA.intent, getSeverity(scan.cyberDNA.intent)],
    ],
    theme: 'striped',
  });

  // Footer
  const pageHeight = doc.internal.pageSize.height;
  doc.setFontSize(8);
  doc.setTextColor(100);
  doc.text("CONFIDENTIAL - FOR INTERNAL USE ONLY - CYBERSENTRY.AI", 10, pageHeight - 10);

  doc.save(`SENTRY_REPORT_${scan.id.substring(0,8)}.pdf`);
};

function getSeverity(score: number): string {
  if (score < 30) return 'LOW';
  if (score < 70) return 'MEDIUM';
  return 'HIGH';
}
