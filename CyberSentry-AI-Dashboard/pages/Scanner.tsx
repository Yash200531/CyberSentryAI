import React, { useState, useRef, useEffect } from 'react';
import { useStore } from '../contexts/StoreContext';
import { analyzeContent } from '../services/geminiService';
import { AnalysisType, AnalysisResult, Verdict } from '../types';
import { Send, Link as LinkIcon, FileText, AlertTriangle, CheckCircle, AlertOctagon, Loader2, Shield, ThumbsUp, ThumbsDown, Check, Share2, Copy, ImageIcon, Upload, X, ScanEye, Zap } from 'lucide-react';

// New component for the loading animation
const ScanningOverlay: React.FC = () => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  
  const steps = [
    "Initializing neural handshake...",
    "Parsing metadata headers...",
    "Cross-referencing threat databases...",
    "Analyzing heuristics & patterns...",
    "Detecting obfuscated scripts...",
    "Synthesizing security verdict..."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return 95;
        // Non-linear progress for realism
        const increment = Math.random() * 5 + 1;
        return prev + increment;
      });
    }, 150);

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev + 1) % steps.length);
    }, 800);

    return () => {
      clearInterval(interval);
      clearInterval(stepInterval);
    };
  }, []);

  return (
    <div className="absolute inset-0 z-20 bg-white/95 dark:bg-cyber-900/95 backdrop-blur-md flex flex-col items-center justify-center p-8 transition-all duration-300 rounded-2xl">
      <div className="w-full max-w-sm relative">
        {/* Central Graphic */}
        <div className="relative w-32 h-32 mx-auto mb-8">
          <div className="absolute inset-0 border-4 border-cyber-900/10 dark:border-cyber-accent/20 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-transparent border-t-cyber-accent rounded-full animate-spin"></div>
          <div className="absolute inset-2 border-4 border-transparent border-b-purple-500 rounded-full animate-[spin_2s_linear_infinite_reverse]"></div>
          
          <div className="absolute inset-0 flex items-center justify-center">
             <Shield className="text-cyber-accent animate-pulse" size={40} />
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden mb-4">
          <div 
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyber-accent via-blue-500 to-purple-600 transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        {/* Status Text */}
        <div className="text-center space-y-2">
          <p className="font-mono text-2xl font-bold text-gray-900 dark:text-white">
            {Math.floor(progress)}%
          </p>
          <div className="h-6 overflow-hidden">
             <p className="font-mono text-sm text-cyber-600 dark:text-cyber-accent animate-pulse">
               {">"} {steps[currentStep]}
             </p>
          </div>
        </div>
      </div>

      {/* Grid Overlay for Cyber Feel */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(0,242,234,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,242,234,0.03)_1px,transparent_1px)] bg-[size:20px_20px]"></div>
    </div>
  );
};

export const Scanner: React.FC = () => {
  const { addHistoryItem } = useStore();
  const [input, setInput] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [mode, setMode] = useState<AnalysisType>(AnalysisType.TEXT);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Ref for auto-scrolling to result
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [result]);

  const handleModeChange = (newMode: AnalysisType) => {
    setMode(newMode);
    setResult(null);
    setFeedback(null);
    // Clear inputs when switching modes to avoid confusion
    if (newMode === AnalysisType.IMAGE) {
        setInput('');
    } else {
        setSelectedImage(null);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (loading) return;
    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const contentToScan = mode === AnalysisType.IMAGE ? selectedImage : input;
    if (!contentToScan || !contentToScan.trim()) return;

    setLoading(true);
    setResult(null);
    setFeedback(null);
    setCopied(false);

    // Artificial delay to show off the cool animation
    const minTime = new Promise(resolve => setTimeout(resolve, 2000));
    const analysisPromise = analyzeContent(contentToScan, mode);
    
    // Wait for both analysis and animation minimum time
    const [_, analysis] = await Promise.all([minTime, analysisPromise]);
    
    const newResult: AnalysisResult = {
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      ...analysis
    };

    setResult(newResult);
    addHistoryItem(newResult);
    setLoading(false);
  };

  const handleShare = async () => {
    if (!result) return;
    const text = `🛡️ CyberSentry AI Scan Report\n\nType: ${result.type}\nVerdict: ${result.verdict}\nScore: ${result.score}/100\n\nReasoning:\n${result.reasoning}\n\nAnalyzed by CyberSentry AI`;
    
    try {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    } catch (err) {
        console.error('Failed to copy', err);
    }
  };

  const getVerdictColor = (verdict: Verdict) => {
    switch (verdict) {
      case Verdict.SAFE: return 'text-cyber-success border-cyber-success bg-cyber-success/10';
      case Verdict.SPAM: return 'text-cyber-danger border-cyber-danger bg-cyber-danger/10';
      case Verdict.SUSPICIOUS: return 'text-orange-500 border-orange-500 bg-orange-500/10';
      default: return 'text-gray-500 border-gray-500 bg-gray-500/10';
    }
  };

  const getVerdictIcon = (verdict: Verdict) => {
    const className = "w-10 h-10 md:w-12 md:h-12";
    switch (verdict) {
      case Verdict.SAFE: return <CheckCircle className={className} />;
      case Verdict.SPAM: return <AlertOctagon className={className} />;
      case Verdict.SUSPICIOUS: return <AlertTriangle className={className} />;
      default: return <Loader2 className={className} />;
    }
  };

  const isScanDisabled = loading || (mode === AnalysisType.IMAGE ? !selectedImage : !input.trim());

  return (
    <div className="flex flex-col h-full space-y-8 page-animate pb-12">
      <div className="text-center space-y-4 mb-4 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-cyber-accent/20 blur-[80px] rounded-full pointer-events-none"></div>
        
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyber-accent/10 border border-cyber-accent/20 text-cyber-accent text-xs font-semibold mb-2">
            <Zap size={12} className="fill-current" />
            <span>AI-Powered Forensics Engine v3.0</span>
        </div>

        <h2 className="text-5xl md:text-6xl font-black tracking-tight premium-text p-2">
          CyberSentry AI
        </h2>
        <p className="text-gray-600 dark:text-gray-400 max-w-lg mx-auto text-lg">
          Advanced threat detection for the modern web. Scan links, text, and media instantly.
        </p>
      </div>

      {/* Scanner Interface */}
      <div className="relative bg-white dark:bg-cyber-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-cyber-700 overflow-hidden min-h-[400px] transition-all duration-300 hover:border-cyber-accent/30 hover:shadow-[0_0_40px_rgba(0,242,234,0.05)]">
        
        {loading && <ScanningOverlay />}

        {/* Toggle Header */}
        <div className="flex border-b border-gray-200 dark:border-cyber-700 overflow-x-auto">
          <button
            onClick={() => handleModeChange(AnalysisType.TEXT)}
            disabled={loading}
            className={`flex-1 py-4 flex items-center justify-center space-x-2 transition-all min-w-[100px] ${
              mode === AnalysisType.TEXT 
                ? 'bg-gray-50 dark:bg-cyber-700/50 text-cyber-accent font-bold border-b-2 border-cyber-accent' 
                : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-cyber-700/30'
            }`}
          >
            <FileText size={20} />
            <span>Text</span>
          </button>
          <button
            onClick={() => handleModeChange(AnalysisType.LINK)}
            disabled={loading}
            className={`flex-1 py-4 flex items-center justify-center space-x-2 transition-all min-w-[100px] ${
              mode === AnalysisType.LINK 
                ? 'bg-gray-50 dark:bg-cyber-700/50 text-cyber-accent font-bold border-b-2 border-cyber-accent' 
                : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-cyber-700/30'
            }`}
          >
            <LinkIcon size={20} />
            <span>Link</span>
          </button>
          <button
            onClick={() => handleModeChange(AnalysisType.IMAGE)}
            disabled={loading}
            className={`flex-1 py-4 flex items-center justify-center space-x-2 transition-all min-w-[100px] ${
              mode === AnalysisType.IMAGE 
                ? 'bg-gray-50 dark:bg-cyber-700/50 text-cyber-accent font-bold border-b-2 border-cyber-accent' 
                : 'text-gray-500 hover:bg-gray-50 dark:hover:bg-cyber-700/30'
            }`}
          >
            <ImageIcon size={20} />
            <span>Image</span>
          </button>
        </div>

        <div className="p-6 md:p-8">
          <form onSubmit={handleScan} className="space-y-6">
            
            <div className="relative group">
              <div className={`absolute -inset-0.5 bg-gradient-to-r from-cyber-accent to-purple-600 rounded-xl opacity-0 group-focus-within:opacity-20 transition duration-500 blur ${loading ? 'opacity-0' : ''}`}></div>
              
              {mode === AnalysisType.IMAGE ? (
                 <div 
                   onDragOver={(e) => e.preventDefault()}
                   onDrop={handleDrop}
                   className="relative w-full h-64 p-4 bg-gray-50 dark:bg-cyber-900 border-2 border-dashed border-gray-300 dark:border-cyber-600 rounded-xl transition-all hover:border-cyber-accent dark:hover:border-cyber-accent flex flex-col items-center justify-center text-center cursor-pointer overflow-hidden group-hover:bg-white dark:group-hover:bg-cyber-900"
                 >
                    {!selectedImage ? (
                      <div onClick={() => fileInputRef.current?.click()} className="w-full h-full flex flex-col items-center justify-center">
                        <Upload size={48} className="text-gray-400 dark:text-cyber-500 mb-4 group-hover:text-cyber-accent transition-colors duration-300 transform group-hover:scale-110" />
                        <p className="text-lg font-medium text-gray-700 dark:text-gray-300">Drag & Drop or Click to Upload</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Supports JPG, PNG, WEBP</p>
                        <input 
                          type="file" 
                          ref={fileInputRef}
                          onChange={handleFileChange}
                          accept="image/*" 
                          className="hidden" 
                        />
                      </div>
                    ) : (
                      <div className="relative w-full h-full flex items-center justify-center">
                        <img src={selectedImage} alt="Preview" className="max-w-full max-h-full rounded-lg object-contain shadow-lg" />
                        <button 
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setSelectedImage(null); }}
                          className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 shadow-md transition-transform hover:scale-110"
                        >
                          <X size={16} />
                        </button>
                        <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-black/60 px-3 py-1 rounded-full text-xs text-white backdrop-blur-sm flex items-center gap-1">
                           <Check size={12} className="text-green-400"/> Ready to scan
                        </div>
                      </div>
                    )}
                 </div>
              ) : (
                <>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                    placeholder={mode === AnalysisType.LINK ? "https://suspicious-website.com/login..." : "Paste the email or message content here..."}
                    className="relative w-full h-48 p-4 bg-gray-50 dark:bg-cyber-900 border-2 border-gray-200 dark:border-cyber-600 rounded-xl focus:ring-0 focus:border-cyber-accent outline-none transition-all resize-none font-mono text-sm disabled:opacity-50 disabled:cursor-not-allowed group-hover:bg-white dark:group-hover:bg-cyber-900"
                  />
                  <div className="absolute bottom-4 right-4 text-xs text-gray-400">
                    {input.length} chars
                  </div>
                </>
              )}
            </div>

            <button
              type="submit"
              disabled={isScanDisabled}
              className="w-full py-4 bg-cyber-accent hover:bg-cyan-400 text-cyber-900 font-bold rounded-xl shadow-[0_0_20px_rgba(0,242,234,0.3)] transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {mode === AnalysisType.IMAGE ? <ScanEye size={20} /> : <Send size={20} />}
              <span>{mode === AnalysisType.IMAGE ? "Scan Image for Deepfakes" : "Analyze Threat"}</span>
            </button>
          </form>
        </div>
      </div>

      {/* Results Area */}
      {result && (
        <div ref={resultRef} className="page-animate relative">
          <div className={`p-1 rounded-2xl bg-gradient-to-r ${result.verdict === Verdict.SAFE ? 'from-green-400 to-cyber-success' : result.verdict === Verdict.SPAM ? 'from-orange-500 to-cyber-danger' : 'from-yellow-400 to-orange-400'}`}>
            <div className="bg-white dark:bg-cyber-800 rounded-xl p-6 md:p-8">
              
              <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
                
                {/* Score Circle */}
                <div className="flex-shrink-0 relative group">
                  <div className={`w-24 h-24 md:w-32 md:h-32 rounded-full border-4 flex items-center justify-center ${getVerdictColor(result.verdict).replace('bg-', 'bg-opacity-0 ')}`}>
                    <div className="text-center">
                       <span className="block text-2xl md:text-3xl font-bold">{result.score}</span>
                       <span className="text-[10px] md:text-xs uppercase font-semibold">
                         {result.type === AnalysisType.IMAGE ? 'Authenticity' : 'Security'}
                       </span>
                    </div>
                  </div>
                  <div className={`absolute top-0 right-0 p-1 md:p-2 rounded-full ${getVerdictColor(result.verdict)}`}>
                     {getVerdictIcon(result.verdict)}
                  </div>
                </div>

                {/* Text Details */}
                <div className="flex-1 space-y-4 w-full text-center md:text-left">
                  <div>
                    <h3 className="text-lg font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Verdict</h3>
                    <div className={`text-3xl font-bold flex items-center justify-center md:justify-start space-x-2 ${getVerdictColor(result.verdict).split(' ')[0]}`}>
                      <span>{result.verdict}</span>
                    </div>
                  </div>

                  <div className="bg-gray-50 dark:bg-cyber-900/50 p-4 rounded-lg border border-gray-100 dark:border-cyber-700 text-left">
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">AI Forensics Report</h4>
                    <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                      {result.reasoning}
                    </p>
                  </div>
                </div>
              </div>

              {/* Feedback and Share Section */}
              <div className="mt-8 pt-6 border-t border-gray-100 dark:border-cyber-700">
                <div className="flex flex-col-reverse md:flex-row items-center justify-between gap-4">
                  
                  {/* Feedback Controls */}
                  <div className="w-full md:w-auto">
                    {!feedback ? (
                      <div className="flex flex-col sm:flex-row items-center gap-3">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => setFeedback('up')}
                            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-cyber-700 text-gray-500 dark:text-gray-400 hover:text-green-500 dark:hover:text-green-400 transition-colors"
                            title="Helpful"
                          >
                            <ThumbsUp size={18} />
                          </button>
                          <button
                            onClick={() => setFeedback('down')}
                            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-cyber-700 text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                            title="Not Helpful"
                          >
                            <ThumbsDown size={18} />
                          </button>
                          <span className="text-xs text-gray-400 dark:text-gray-500">Rate analysis</span>
                        </div>
                        <p className="text-xs text-gray-400 dark:text-gray-500 hidden sm:block">|</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 italic">
                          AI can be inaccurate.
                        </p>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 py-2 px-3 rounded-lg animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <Check size={16} />
                        <span className="font-medium">Thanks for feedback!</span>
                      </div>
                    )}
                  </div>

                  {/* Share Button */}
                  <button
                    onClick={handleShare}
                    className="w-full md:w-auto flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg bg-gray-100 dark:bg-cyber-700 hover:bg-gray-200 dark:hover:bg-cyber-600 text-gray-700 dark:text-gray-200 transition-all active:scale-95 font-medium text-sm"
                  >
                    {copied ? <Check size={16} className="text-green-600 dark:text-green-400"/> : <Share2 size={16} />}
                    <span>{copied ? 'Copied to Clipboard' : 'Share Result'}</span>
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
};