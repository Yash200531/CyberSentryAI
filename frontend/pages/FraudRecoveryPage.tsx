import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ShieldAlert, CheckCircle, FileText, Download, AlertCircle, ChevronRight, Info } from 'lucide-react';

interface RecoveryStep {
  step_number: number;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  priority: 'high' | 'medium' | 'normal';
  completed_at: string | null;
}

interface RecoveryPlan {
  session_id: string;
  timestamp: string;
  threat_summary: {
    type: string;
    category: string;
    confidence: number;
    scan_type: string;
    urgency_level: string;
  };
  immediate_actions: RecoveryStep[];
  recovery_steps: RecoveryStep[];
  personalized_advice: string;
  resources: {
    emergency_contacts?: Array<{ name: string; url?: string; phone?: string; info?: string }>;
    credit_bureaus?: Array<{ name: string; phone: string }>;
    financial_institutions?: Array<{ action: string; info: string }>;
  };
  progress_tracker: {
    total_steps: number;
    completed_steps: number[];
    current_step: number;
  };
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const FraudRecoveryPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [recoveryPlan, setRecoveryPlan] = useState<RecoveryPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [showReport, setShowReport] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<any>(null);

  // Get threat data from navigation state or generate from scan result
  const threatData = location.state?.threatData;

  useEffect(() => {
    if (threatData) {
      generateRecoveryPlan(threatData);
    } else {
      setLoading(false);
    }
  }, []);

  const generateRecoveryPlan = async (data: any) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/recovery/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threat_data: data }),
      });

      if (!response.ok) throw new Error('Failed to generate recovery plan');

      const result = await response.json();
      setRecoveryPlan(result.recovery_plan);
      setCompletedSteps(result.recovery_plan.progress_tracker.completed_steps || []);
      setCurrentStep(result.recovery_plan.progress_tracker.current_step || 0);
    } catch (error) {
      console.error('Error generating recovery plan:', error);
      alert('Failed to generate recovery plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const markStepComplete = async (stepNumber: number, status: 'completed' | 'skipped') => {
    if (!recoveryPlan) return;

    try {
      const response = await fetch(`${API_BASE}/recovery/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: recoveryPlan.session_id,
          step_number: stepNumber,
          status: status,
        }),
      });

      if (!response.ok) throw new Error('Failed to update progress');

      // Update local state
      if (status === 'completed' && !completedSteps.includes(stepNumber)) {
        setCompletedSteps([...completedSteps, stepNumber]);
      }
      
      // Move to next step
      if (stepNumber === currentStep + 1) {
        setCurrentStep(stepNumber);
      }
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const generateReport = async () => {
    if (!recoveryPlan) return;

    try {
      const response = await fetch(`${API_BASE}/recovery/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: recoveryPlan.session_id,
          recovery_plan: recoveryPlan,
          completed_steps: completedSteps,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate report');

      const result = await response.json();
      setGeneratedReport(result.report);
      setShowReport(true);
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report. Please try again.');
    }
  };

  const downloadReport = () => {
    if (!generatedReport) return;

    const reportText = JSON.stringify(generatedReport, null, 2);
    const blob = new Blob([reportText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fraud-recovery-report-${generatedReport.report_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return 'text-red-500 bg-red-500/10 border-red-500/30';
      case 'high':
        return 'text-orange-500 bg-orange-500/10 border-orange-500/30';
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      default:
        return 'text-blue-500 bg-blue-500/10 border-blue-500/30';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'medium':
        return <Info className="w-4 h-4 text-yellow-500" />;
      default:
        return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ShieldAlert className="w-16 h-16 text-cyber-primary mx-auto mb-4 animate-pulse" />
          <p className="text-white text-xl">Generating your recovery plan...</p>
        </div>
      </div>
    );
  }

  if (!recoveryPlan) {
    return (
      <div className="space-y-6">
        <div className="glass-panel rounded-2xl border border-cyber-border p-8 text-center">
          <ShieldAlert className="w-16 h-16 text-cyber-muted mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">No Recovery Plan Available</h2>
          <p className="text-cyber-muted mb-6">
            To generate a recovery plan, first scan content for threats.
          </p>
          <button
            onClick={() => navigate('/app/scan')}
            className="btn-primary px-6 py-3 rounded-lg font-medium"
          >
            Go to Scan Page
          </button>
        </div>
      </div>
    );
  }

  const progressPercentage = (completedSteps.length / recoveryPlan.recovery_steps.length) * 100;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Fraud Recovery Assistant</h1>
          <p className="text-cyber-muted">AI-powered guidance for cyber threat recovery</p>
        </div>
        <button
          onClick={generateReport}
          className="btn-secondary px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <FileText className="w-4 h-4" />
          Generate Report
        </button>
      </div>

      {/* Threat Summary */}
      <div className="glass-panel rounded-2xl border border-cyber-border p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">Incident Summary</h2>
            <p className="text-cyber-muted">Session ID: {recoveryPlan.session_id}</p>
          </div>
          <span
            className={`px-4 py-2 rounded-lg border font-semibold uppercase text-sm ${getUrgencyColor(
              recoveryPlan.threat_summary.urgency_level
            )}`}
          >
            {recoveryPlan.threat_summary.urgency_level} Priority
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-cyber-dark/50 rounded-lg p-4">
            <p className="text-cyber-muted text-sm mb-1">Threat Type</p>
            <p className="text-white font-semibold capitalize">{recoveryPlan.threat_summary.type}</p>
          </div>
          <div className="bg-cyber-dark/50 rounded-lg p-4">
            <p className="text-cyber-muted text-sm mb-1">Confidence</p>
            <p className="text-white font-semibold">{recoveryPlan.threat_summary.confidence.toFixed(1)}%</p>
          </div>
          <div className="bg-cyber-dark/50 rounded-lg p-4">
            <p className="text-cyber-muted text-sm mb-1">Detection Time</p>
            <p className="text-white font-semibold">
              {new Date(recoveryPlan.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Progress Tracker */}
      <div className="glass-panel rounded-2xl border border-cyber-border p-6">
        <h2 className="text-xl font-bold text-white mb-4">Recovery Progress</h2>
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-cyber-muted">
              {completedSteps.length} of {recoveryPlan.recovery_steps.length} steps completed
            </span>
            <span className="text-cyber-primary font-semibold">{progressPercentage.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-cyber-dark rounded-full h-3">
            <div
              className="bg-gradient-to-r from-cyber-primary to-cyber-secondary h-3 rounded-full transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Personalized Advice */}
      <div className="glass-panel rounded-2xl border border-cyber-border p-6">
        <h2 className="text-xl font-bold text-white mb-4">Personalized Advice</h2>
        <div className="bg-cyber-dark/50 rounded-lg p-4 border border-cyber-primary/30">
          <p className="text-cyber-muted leading-relaxed whitespace-pre-line">
            {recoveryPlan.personalized_advice}
          </p>
        </div>
      </div>

      {/* Immediate Actions */}
      <div className="glass-panel rounded-2xl border border-cyber-border p-6">
        <h2 className="text-xl font-bold text-white mb-4">Immediate Actions Required</h2>
        <div className="space-y-3">
          {recoveryPlan.immediate_actions.map((action) => (
            <div
              key={action.step_number}
              className={`bg-cyber-dark/50 rounded-lg p-4 border ${
                completedSteps.includes(action.step_number)
                  ? 'border-green-500/30'
                  : 'border-red-500/30'
              }`}
            >
              <div className="flex items-start gap-3">
                {completedSteps.includes(action.step_number) ? (
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                ) : (
                  getPriorityIcon(action.priority)
                )}
                <div className="flex-1">
                  <p className="text-white font-medium">{action.description}</p>
                </div>
                {!completedSteps.includes(action.step_number) && (
                  <button
                    onClick={() => markStepComplete(action.step_number, 'completed')}
                    className="btn-primary px-3 py-1 text-sm rounded"
                  >
                    Mark Complete
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* All Recovery Steps */}
      <div className="glass-panel rounded-2xl border border-cyber-border p-6">
        <h2 className="text-xl font-bold text-white mb-4">Complete Recovery Checklist</h2>
        <div className="space-y-2">
          {recoveryPlan.recovery_steps.map((step) => (
            <div
              key={step.step_number}
              className={`bg-cyber-dark/30 rounded-lg p-4 border transition-all ${
                completedSteps.includes(step.step_number)
                  ? 'border-green-500/30 opacity-75'
                  : 'border-cyber-border hover:border-cyber-primary/50'
              }`}
            >
              <div className="flex items-start gap-3">
                <span className="text-cyber-muted font-mono text-sm mt-0.5">
                  {step.step_number.toString().padStart(2, '0')}
                </span>
                <div className="flex-1">
                  <p className={`${completedSteps.includes(step.step_number) ? 'text-cyber-muted line-through' : 'text-white'}`}>
                    {step.description}
                  </p>
                </div>
                {completedSteps.includes(step.step_number) ? (
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => markStepComplete(step.step_number, 'completed')}
                      className="btn-primary px-3 py-1 text-sm rounded"
                    >
                      Complete
                    </button>
                    <button
                      onClick={() => markStepComplete(step.step_number, 'skipped')}
                      className="btn-secondary px-3 py-1 text-sm rounded"
                    >
                      Skip
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resources */}
      <div className="glass-panel rounded-2xl border border-cyber-border p-6">
        <h2 className="text-xl font-bold text-white mb-4">Important Resources</h2>
        
        {recoveryPlan.resources.emergency_contacts && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-cyber-primary mb-3">Emergency Contacts</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {recoveryPlan.resources.emergency_contacts.map((contact, idx) => (
                <div key={idx} className="bg-cyber-dark/50 rounded-lg p-3">
                  <p className="text-white font-medium mb-1">{contact.name}</p>
                  {contact.url && (
                    <a
                      href={contact.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyber-primary hover:text-cyber-secondary text-sm flex items-center gap-1"
                    >
                      Visit Website <ChevronRight className="w-3 h-3" />
                    </a>
                  )}
                  {contact.phone && <p className="text-cyber-muted text-sm">{contact.phone}</p>}
                  {contact.info && <p className="text-cyber-muted text-sm">{contact.info}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {recoveryPlan.resources.credit_bureaus && (
          <div>
            <h3 className="text-lg font-semibold text-cyber-primary mb-3">Credit Bureaus</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {recoveryPlan.resources.credit_bureaus.map((bureau, idx) => (
                <div key={idx} className="bg-cyber-dark/50 rounded-lg p-3">
                  <p className="text-white font-medium mb-1">{bureau.name}</p>
                  <p className="text-cyber-muted text-sm">{bureau.phone}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Report Modal */}
      {showReport && generatedReport && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl border border-cyber-border max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Recovery Report</h2>
                <p className="text-cyber-muted">Report ID: {generatedReport.report_id}</p>
              </div>
              <button
                onClick={() => setShowReport(false)}
                className="text-cyber-muted hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <h3 className="text-lg font-semibold text-cyber-primary mb-2">Incident Details</h3>
                <div className="bg-cyber-dark/50 rounded-lg p-3 space-y-1">
                  <p className="text-cyber-muted">
                    <span className="text-white font-medium">Type:</span>{' '}
                    {generatedReport.incident_details.incident_type}
                  </p>
                  <p className="text-cyber-muted">
                    <span className="text-white font-medium">Date:</span>{' '}
                    {new Date(generatedReport.incident_details.detection_date).toLocaleString()}
                  </p>
                  <p className="text-cyber-muted">
                    <span className="text-white font-medium">Completion:</span>{' '}
                    {generatedReport.completion_rate}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={downloadReport}
                className="btn-primary flex-1 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Report
              </button>
              <button
                onClick={() => setShowReport(false)}
                className="btn-secondary px-4 py-2 rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FraudRecoveryPage;
