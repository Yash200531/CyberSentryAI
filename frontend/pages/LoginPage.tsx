import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { User as UserIcon } from 'lucide-react';
import Logo from '../components/Logo';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('analyst@ji.ai');
  const [password, setPassword] = useState('Sw@gtm!1');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    const success = await login(email, password);
    if (success) {
      // Default redirect to New Scan page as per requirements
      navigate('/app/scan');
    } else {
      setErrorMessage('Invalid credentials. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid flex items-center justify-center px-4 relative">
       {/* Background decorative glow */}
       <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyber-primary/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-cyber-border shadow-2xl relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-cyber-primary/20 rounded-full flex items-center justify-center mb-4 border border-cyber-primary/50">
            <Logo size="small" showText={false} />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-wider">SECURE LOGIN</h2>
          <p className="text-cyber-muted text-sm mt-2">Enter credentials to access the grid</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {errorMessage && (
            <div className="rounded border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300 font-mono">
              {errorMessage}
            </div>
          )}
          <div>
            <label htmlFor="login-email" className="block text-xs font-mono text-cyber-primary mb-2 uppercase tracking-widest">Identifier</label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
              <input 
                id="login-email"
                name="email"
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-black/40 border border-cyber-border rounded px-10 py-3 text-white focus:outline-none focus:border-cyber-primary transition-colors"
                placeholder="analyst@ji.ai"
                autoComplete="username"
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="login-password" className="block text-xs font-mono text-cyber-primary mb-2 uppercase tracking-widest">Passcode</label>
            <input 
              id="login-password"
              name="password"
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-black/40 border border-cyber-border rounded px-4 py-3 text-white focus:outline-none focus:border-cyber-primary transition-colors"
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full bg-cyber-primary text-black font-bold py-3 rounded hover:bg-cyan-300 transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] disabled:opacity-50"
          >
            {isLoading ? 'AUTHENTICATING...' : 'INITIALIZE SESSION'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;