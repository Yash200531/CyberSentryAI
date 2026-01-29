import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ScanType } from '../types';
import { analyzeContent } from '../services/backendService';
import { saveScan } from '../services/storage';
import { useAuth } from '../AuthContext';
import { FileText, Globe, Image as ImageIcon, Mail, Upload, Loader2, Play } from 'lucide-react';

const ScanPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ScanType>(ScanType.TEXT);
  const [inputContent, setInputContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const runAnalysis = async () => {
    if (!user) return;
    setIsAnalyzing(true);
    
    // Artificial delay to show the "cool" loading state for at least 2s
    const startTime = Date.now();

    try {
      const result = await analyzeContent(
        activeTab,
        inputContent,
        user.id
      );

      await saveScan(result);
      
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 2000 - elapsed);
      
      setTimeout(() => {
        setIsAnalyzing(false);
        navigate(`/app/report/${result.id}`);
      }, remaining);

    } catch (e) {
      console.error(e);
      setIsAnalyzing(false);
      alert('Analysis failed. Check console.');
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">New Threat Scan</h1>
          <p className="text-cyber-muted">Select input source and initialize Red-Team analysis.</p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl border border-cyber-border overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-cyber-border">
          {[
            { id: ScanType.TEXT, icon: FileText, label: 'Raw Text' },
            { id: ScanType.URL, icon: Globe, label: 'URL / Domain' },
            { id: ScanType.EMAIL, icon: Mail, label: 'Email Content' },
            { id: ScanType.IMAGE, icon: ImageIcon, label: 'Image / OCR' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => { setActiveTab(tab.id); setInputContent(''); setPreviewUrl(null); }}
              className={`flex-1 py-4 flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-cyber-primary/10 text-cyber-primary border-b-2 border-cyber-primary'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <tab.icon size={18} />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="p-8 min-h-[400px] relative">
          
          {/* Scanning Overlay */}
          {isAnalyzing && (
            <div className="absolute inset-0 z-20 bg-cyber-dark/90 flex flex-col items-center justify-center backdrop-blur-sm">
              <div className="w-64 h-2 bg-gray-800 rounded-full overflow-hidden mb-4">
                <div className="h-full bg-cyber-primary animate-[scan_2s_ease-in-out_infinite]" style={{ width: '100%' }}></div>
              </div>
              <div className="flex items-center gap-3 text-cyber-primary font-mono text-lg animate-pulse">
                <Loader2 className="animate-spin" />
                ANALYZING THREAT VECTORS...
              </div>
              <div className="mt-2 text-cyber-muted text-sm font-mono">
                 Extracting Cyber DNA... Simulating Attacker Mindset...
              </div>
            </div>
          )}

          {activeTab === ScanType.IMAGE ? (
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-cyber-border rounded-xl p-12 hover:border-cyber-primary/50 transition-colors">
              {previewUrl ? (
                <div className="relative w-full max-w-md">
                   <img src={previewUrl} alt="Preview" className="w-full h-auto rounded shadow-lg" />
                   <button 
                    onClick={() => {setPreviewUrl(null); setSelectedFile(null);}}
                    className="absolute top-2 right-2 bg-red-500/80 text-white p-1 rounded hover:bg-red-500"
                   >
                     X
                   </button>
                </div>
              ) : (
                <>
                  <Upload className="w-16 h-16 text-gray-500 mb-4" />
                  <label htmlFor="scan-image-upload" className="cursor-pointer bg-cyber-primary/10 text-cyber-primary px-6 py-2 rounded border border-cyber-primary/30 hover:bg-cyber-primary hover:text-black transition-colors">
                    Upload Screenshot / Image
                  </label>
                  <input
                    id="scan-image-upload"
                    name="scan-image"
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleFileChange}
                  />
                  <p className="mt-4 text-gray-500 text-sm">Supports PNG, JPG, WEBP</p>
                </>
              )}
            </div>
          ) : (
            <textarea
              value={inputContent}
              onChange={(e) => setInputContent(e.target.value)}
              placeholder={
                activeTab === ScanType.URL ? "https://suspicious-site.com/login" :
                activeTab === ScanType.EMAIL ? "Paste full email headers and body here..." :
                "Paste suspicious text content..."
              }
              className="w-full h-[300px] bg-black/30 border border-cyber-border rounded-xl p-4 text-white font-mono text-sm focus:outline-none focus:border-cyber-primary/50 resize-none"
            />
          )}

          <div className="mt-6 flex justify-end">
            <button
              onClick={runAnalysis}
              disabled={isAnalyzing || (!inputContent && !previewUrl)}
              className="px-8 py-3 bg-cyber-primary text-black font-bold rounded flex items-center gap-2 hover:bg-cyan-300 transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play size={20} fill="currentColor" />
              INITIATE SCAN
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScanPage;
