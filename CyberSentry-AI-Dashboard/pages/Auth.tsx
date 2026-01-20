import React, { useState } from 'react';
import { useStore } from '../contexts/StoreContext';
import { ShieldCheck, UserPlus, LogIn, ArrowRight } from 'lucide-react';

export const Auth: React.FC = () => {
  const { login } = useStore();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const name = isLogin ? formData.email.split('@')[0] : formData.username;
    login(name, formData.email);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gray-50 dark:bg-cyber-950 transition-colors duration-300 relative overflow-hidden">
      
      {/* Premium Background Layers */}
      <div className="absolute inset-0 z-0 premium-bg-pattern pointer-events-none opacity-0 dark:opacity-100 transition-opacity duration-500"></div>
      <div className="absolute inset-0 z-0 cyber-grid pointer-events-none opacity-0 dark:opacity-100 transition-opacity duration-500"></div>

      {/* Abstract Background Shapes - Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-cyber-accent/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none"></div>

      <div className="w-full max-w-md bg-white dark:bg-cyber-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200 dark:border-cyber-800 p-8 z-10 relative">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4 text-cyber-accent">
            <ShieldCheck size={56} className="drop-shadow-[0_0_15px_rgba(0,242,234,0.4)]" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">CyberSentry AI</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">
            {isLogin ? 'Welcome back, Agent.' : 'Initialize your security clearance.'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
              <input
                type="text"
                required
                className="w-full p-3 bg-gray-50 dark:bg-cyber-950 border border-gray-300 dark:border-cyber-700 rounded-lg focus:ring-2 focus:ring-cyber-accent focus:border-transparent outline-none transition-all dark:text-white"
                placeholder="AgentName"
                value={formData.username}
                onChange={e => setFormData({ ...formData, username: e.target.value })}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
            <input
              type="email"
              required
              className="w-full p-3 bg-gray-50 dark:bg-cyber-950 border border-gray-300 dark:border-cyber-700 rounded-lg focus:ring-2 focus:ring-cyber-accent focus:border-transparent outline-none transition-all dark:text-white"
              placeholder="agent@cybersentry.ai"
              value={formData.email}
              onChange={e => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Passcode</label>
            <input
              type="password"
              required
              className="w-full p-3 bg-gray-50 dark:bg-cyber-950 border border-gray-300 dark:border-cyber-700 rounded-lg focus:ring-2 focus:ring-cyber-accent focus:border-transparent outline-none transition-all dark:text-white"
              placeholder="••••••••"
              value={formData.password}
              onChange={e => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-cyber-accent hover:bg-cyan-400 text-cyber-900 font-bold rounded-lg transition-all flex items-center justify-center space-x-2 group shadow-[0_0_20px_rgba(0,242,234,0.2)]"
          >
            <span>{isLogin ? 'Authenticate' : 'Register Account'}</span>
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-cyber-accent dark:hover:text-cyber-accent transition-colors flex items-center justify-center w-full space-x-2"
          >
            {isLogin ? (
               <>
                <UserPlus size={16} />
                <span>New User ? Sign up</span>
               </>
            ) : (
               <>
                <LogIn size={16} />
                <span>Return to login</span>
               </>
            )}
          </button>
        </div>
      </div>

      <div className="mt-8 z-10 text-center text-sm text-gray-500 dark:text-gray-500">
         <p>
           Copyright 2026 CyberSentry AI <span className="hidden sm:inline">|</span> <br className="sm:hidden" />
           Designed And Developed by <span className="font-bold text-gray-800 dark:text-gray-200 tracking-wide">Team X</span>
         </p>
      </div>
    </div>
  );
};