import React from 'react';
import { useStore } from '../contexts/StoreContext';
import { User, Shield, Lock, Zap } from 'lucide-react';

export const Profile: React.FC = () => {
  const { user, history } = useStore();

  // Calculate statistics
  const totalScans = history.length;
  const threatsDetected = history.filter(h => h.verdict === 'SPAM' || h.verdict === 'SUSPICIOUS').length;
  const avgScore = totalScans > 0 
    ? Math.round(history.reduce((acc, curr) => acc + curr.score, 0) / totalScans) 
    : 0;

  if (!user) return null;

  return (
    <div className="space-y-8 page-animate">
      <div className="relative">
        {/* Banner */}
        <div className="h-48 bg-gradient-to-r from-cyber-900 to-cyber-800 rounded-2xl overflow-hidden relative">
           <div className="absolute inset-0 cyber-grid opacity-30"></div>
           <div className="absolute inset-0 bg-cyber-accent/5"></div>
        </div>
        
        {/* Profile Card */}
        <div className="relative -mt-16 px-6 mb-6">
           <div className="flex flex-col md:flex-row items-end md:items-end space-y-4 md:space-y-0 md:space-x-6">
              <img 
                src={user.avatarUrl} 
                alt="Profile" 
                className="w-32 h-32 rounded-full border-4 border-white dark:border-cyber-900 bg-white shadow-lg"
              />
              <div className="pb-2">
                 <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{user.username}</h1>
                 <p className="text-gray-500 dark:text-gray-400">{user.email}</p>
              </div>
              <div className="flex-1"></div>
              <div className="pb-3 flex space-x-3">
                 <button className="px-4 py-2 bg-cyber-accent text-cyber-900 font-bold rounded-lg hover:bg-cyan-400 transition-colors">Edit Profile</button>
              </div>
           </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-cyber-800 p-6 rounded-xl border border-gray-200 dark:border-cyber-700 shadow-sm flex items-center space-x-4 transition-transform hover:-translate-y-1">
           <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg">
              <Zap size={24} />
           </div>
           <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Scans</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalScans}</p>
           </div>
        </div>
        
        <div className="bg-white dark:bg-cyber-800 p-6 rounded-xl border border-gray-200 dark:border-cyber-700 shadow-sm flex items-center space-x-4 transition-transform hover:-translate-y-1">
           <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg">
              <Shield size={24} />
           </div>
           <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Threats Blocked</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{threatsDetected}</p>
           </div>
        </div>

        <div className="bg-white dark:bg-cyber-800 p-6 rounded-xl border border-gray-200 dark:border-cyber-700 shadow-sm flex items-center space-x-4 transition-transform hover:-translate-y-1">
           <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg">
              <Lock size={24} />
           </div>
           <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Avg Safety Score</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{avgScore}%</p>
           </div>
        </div>
      </div>

      {/* Account Details */}
      <div className="bg-white dark:bg-cyber-800 rounded-xl border border-gray-200 dark:border-cyber-700 p-8">
         <h3 className="text-xl font-bold mb-6 text-gray-900 dark:text-white">Account Information</h3>
         <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
               <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Username</label>
               <input type="text" disabled value={user.username} className="w-full p-3 bg-gray-50 dark:bg-cyber-900 border border-gray-200 dark:border-cyber-600 rounded-lg text-gray-700 dark:text-gray-300" />
            </div>
             <div>
               <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Email Address</label>
               <input type="email" disabled value={user.email} className="w-full p-3 bg-gray-50 dark:bg-cyber-900 border border-gray-200 dark:border-cyber-600 rounded-lg text-gray-700 dark:text-gray-300" />
            </div>
             <div>
               <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Member Since</label>
               <input type="text" disabled value={new Date(user.joinedDate).toLocaleDateString()} className="w-full p-3 bg-gray-50 dark:bg-cyber-900 border border-gray-200 dark:border-cyber-600 rounded-lg text-gray-700 dark:text-gray-300" />
            </div>
             <div>
               <label className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Plan Status</label>
               <div className="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-cyber-900 border border-gray-200 dark:border-cyber-600 rounded-lg">
                  <span className="w-2 h-2 rounded-full bg-cyber-accent shadow-[0_0_8px_#00f2ea]"></span>
                  <span className="text-gray-700 dark:text-gray-300">Active (Premium)</span>
               </div>
            </div>
         </div>
      </div>
    </div>
  );
};