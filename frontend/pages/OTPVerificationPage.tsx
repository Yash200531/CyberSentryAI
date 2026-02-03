import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Shield, Mail, RefreshCw } from 'lucide-react';
import Logo from '../components/Logo';

const OTPVerificationPage: React.FC = () => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  const email = (location.state as any)?.email || '';

  useEffect(() => {
    if (!email) {
      navigate('/login');
    }
  }, [email, navigate]);

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      value = value.slice(-1);
    }
    
    if (!/^\d*$/.test(value)) {
      return;
    }

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      const prevInput = document.getElementById(`otp-${index - 1}`);
      prevInput?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData('text').slice(0, 6);
    if (!/^\d+$/.test(pasteData)) return;

    const newOtp = pasteData.split('').concat(Array(6).fill('')).slice(0, 6);
    setOtp(newOtp);

    // Focus last filled input
    const lastIndex = Math.min(pasteData.length, 5);
    const lastInput = document.getElementById(`otp-${lastIndex}`);
    lastInput?.focus();
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    const otpCode = otp.join('');
    if (otpCode.length !== 6) {
      setErrorMessage('Please enter all 6 digits');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          otp_code: otpCode,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccessMessage('Email verified successfully! Redirecting...');
        
        // Store the token
        if (data.token) {
          localStorage.setItem('access_token', data.token);
        }
        
        // Redirect after a short delay
        setTimeout(() => {
          navigate('/app/scan', { replace: true });
        }, 1500);
      } else {
        setErrorMessage(data.msg || 'Verification failed. Please try again.');
      }
    } catch (err) {
      setErrorMessage('Network error. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsResending(true);

    try {
      const response = await fetch('http://localhost:8000/auth/resend-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.otp_sent) {
        setSuccessMessage('New verification code sent to your email');
        setOtp(['', '', '', '', '', '']);
        const firstInput = document.getElementById('otp-0');
        firstInput?.focus();
      } else {
        setErrorMessage(data.msg || 'Failed to resend code. Please try again.');
      }
    } catch (err) {
      setErrorMessage('Network error. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid flex items-center justify-center px-4 relative">
      {/* Background decorative glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyber-primary/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-cyber-border shadow-2xl relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-cyber-primary/20 rounded-full flex items-center justify-center mb-4 border border-cyber-primary/50">
            <Shield className="w-8 h-8 text-cyber-primary" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-wider">EMAIL VERIFICATION</h2>
          <p className="text-cyber-muted text-sm mt-2 text-center">
            We've sent a 6-digit code to
          </p>
          <p className="text-cyber-primary text-sm font-mono mt-1">{email}</p>
        </div>

        <form onSubmit={handleVerify} className="space-y-6">
          {errorMessage && (
            <div className="rounded border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300 font-mono">
              {errorMessage}
            </div>
          )}
          
          {successMessage && (
            <div className="rounded border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm text-green-300 font-mono">
              {successMessage}
            </div>
          )}

          <div>
            <label className="block text-xs font-mono text-cyber-primary mb-3 uppercase tracking-widest text-center">
              Enter Verification Code
            </label>
            <div className="flex justify-center gap-2">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  id={`otp-${index}`}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={index === 0 ? handlePaste : undefined}
                  className="w-12 h-14 bg-black/40 border border-cyber-border rounded text-center text-white text-xl font-bold focus:outline-none focus:border-cyber-primary transition-colors"
                  autoComplete="off"
                />
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || otp.join('').length !== 6}
            className="w-full bg-cyber-primary text-black font-bold py-3 rounded hover:bg-cyan-300 transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'VERIFYING...' : 'VERIFY EMAIL'}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={handleResend}
              disabled={isResending}
              className="text-cyber-muted hover:text-cyber-primary transition-colors text-sm inline-flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isResending ? 'animate-spin' : ''}`} />
              {isResending ? 'Sending...' : "Didn't receive code? Resend"}
            </button>
          </div>

          <div className="text-center pt-4 border-t border-cyber-border">
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-cyber-muted hover:text-white transition-colors text-sm"
            >
              ← Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OTPVerificationPage;
