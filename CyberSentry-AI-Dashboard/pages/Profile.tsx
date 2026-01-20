import React, { useState } from 'react';
import { useStore } from '../contexts/StoreContext';
import { User, Shield, Lock, Zap, Edit2, Save, X, Camera } from 'lucide-react';

export const Profile: React.FC = () => {
  const { user, history, updateUser } = useStore();
  const [isEditing, setIsEditing] = useState(false);
  const [tempUsername, setTempUsername] = useState('');

  // Calculate statistics
  const totalScans = history.length;
  const threatsDetected = history.filter(h => h.verdict === 'SPAM' || h.verdict === 'SUSPICIOUS').length;
  const avgScore = totalScans > 0 
    ? Math.round(history.reduce((acc, curr) => acc + curr.score, 0) / totalScans) 
    : 0;

  if (!user) return null;

  const handleEditClick = () => {
    setTempUsername(user.username);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (tempUsername.trim()) {
      updateUser({ username: tempUsername });
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  return (
    <div className="space-y-8 page-animate max-w-5xl mx-auto pb-12">
      <div className="relative group">
        {/* Banner */}
        <div className="h-64 bg-gradient-to-br from-cyber-950 via-cyber-900 to-cyber-800 rounded-3xl overflow-hidden relative shadow-2xl border border-cyber-800">
           <div className="absolute inset-0 cyber-grid opacity-40 mix-blend-overlay"></div>
           <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
           <div className="absolute top-0 right-0 p-12 opacity-20 transform translate-x-1/3 -translate-y-1/3">
              <div className="w-64 h-64 bg-cyber-accent rounded-full blur-[100px]"></div>
           </div>
        </div>
        
        {/* Profile Card Overlay */}
        <div className="relative -mt-20 px-4 md:px-10">
           <div className="flex flex-col md:flex-row items-end md:items-end gap-6">
              
              {/* Avatar Section */}
              <div className="relative group/avatar">
                <div className="absolute -inset-1 bg-gradient-to-br from-cyber-accent to-purple-600 rounded-full blur opacity-50 group-hover/avatar:opacity-100 transition duration-500"></div>
                <img 
                  src={user.avatarUrl} 
                  alt="Profile" 
                  className="relative w-36 h-36 md:w-40 md:h-40 rounded-full border-4 border-white dark:border-cyber-950 bg-white dark:bg-cyber-900 shadow-xl object-cover"
                />
                <button className="absolute bottom-2 right-2 p-2 bg-gray-900 text-white rounded-full border border-gray-700 opacity-0 group-hover/avatar:opacity-100 transition-all hover:bg-cyber-accent hover:text-black hover:scale-110">
                   <Camera size={16} />
                </button>
              </div>

              {/* User Info & Actions */}
              <div className="flex-1 pb-2 w-full text-center md:text-left">
                 {isEditing ? (
                   <div className="flex flex-col md:flex-row items-center gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300">
                      <input 
                        type="text" 
                        value={tempUsername}
                        onChange={(e) => setTempUsername(e.target.value)}
                        className="text-2xl font-bold bg-white dark:bg-cyber-900 border border-cyber-accent rounded-lg px-3 py-1 focus:ring-2 focus:ring-cyber-accent focus:outline-none dark:text-white w-full md:w-auto shadow-lg shadow-cyber-accent/10"
                        autoFocus
                      />
                      <div className="flex items-center gap-2">
                        <button onClick={handleSave} className="p-2 bg-green-500 text-white rounded-lg hover:bg-green-600 shadow-lg shadow-green-500/20 transition-all hover:scale-105">
                          <Save size={20} />
                        </button>
                        <button onClick={handleCancel} className="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 shadow-lg shadow-red-500/20 transition-all hover:scale-105">
                          <X size={20} />
                        </button>
                      </div>
                   </div>
                 ) : (
                   <div>
                     <div className="flex flex-col md:flex-row items-center md:items-baseline gap-2 md:gap-4">
                        <h1 className="text-4xl font-black text-gray-900 dark:text-white tracking-tight">{user.username}</h1>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/20 uppercase tracking-widest">
                          Pro Agent
                        </span>
                     </div>
                     <p className="text-gray-500 dark:text-gray-400 font-mono text-sm mt-1">{user.email}</p>
                   </div>
                 )}
              </div>

              {/* Edit Button (Static Location) */}
              <div className="pb-4 hidden md:block">
                 {!isEditing && (
                   <button 
                     onClick={handleEditClick}
                     className="px-6 py-2.5 bg-white dark:bg-cyber-800 text-gray-900 dark:text-white border border-gray-200 dark:border-cyber-600 font-semibold rounded-xl hover:bg-gray-50 dark:hover:bg-cyber-700 hover:border-cyber-accent/50 transition-all shadow-sm flex items-center gap-2 group"
                   >
                     <Edit2 size={16} className="text-gray-400 group-hover:text-cyber-accent transition-colors" />
                     <span>Edit Profile</span>
                   </button>
                 )}
              </div>
           </div>
           
           {/* Mobile Edit Button */}
           <div className="mt-4 md:hidden flex justify-center pb-4">
              {!isEditing && (
                 <button 
                   onClick={handleEditClick}
                   className="w-full py-3 bg-white dark:bg-cyber-800 text-gray-900 dark:text-white border border-gray-200 dark:border-cyber-600 font-semibold rounded-xl hover:bg-gray-50 dark:hover:bg-cyber-700 transition-all shadow-sm flex items-center justify-center gap-2"
                 >
                   <Edit2 size={16} />
                   <span>Edit Profile</span>
                 </button>
               )}
           </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 px-4">
        
        <div className="group relative bg-white dark:bg-cyber-900/50 p-6 rounded-2xl border border-gray-200 dark:border-cyber-800 shadow-sm transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:shadow-[0_8px_30px_rgb(0,242,234,0.05)] hover:-translate-y-1 hover:border-cyber-accent/30 overflow-hidden">
           <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
           <div className="flex items-center space-x-4 relative z-10">
             <div className="p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Zap size={28} />
             </div>
             <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Scans</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">{totalScans}</p>
             </div>
           </div>
        </div>
        
        <div className="group relative bg-white dark:bg-cyber-900/50 p-6 rounded-2xl border border-gray-200 dark:border-cyber-800 shadow-sm transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:shadow-[0_8px_30px_rgb(255,0,85,0.05)] hover:-translate-y-1 hover:border-red-500/30 overflow-hidden">
           <div className="absolute top-0 right-0 w-24 h-24 bg-red-500/5 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
           <div className="flex items-center space-x-4 relative z-10">
             <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Shield size={28} />
             </div>
             <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Threats Blocked</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white group-hover:text-red-500 dark:group-hover:text-red-400 transition-colors">{threatsDetected}</p>
             </div>
           </div>
        </div>

        <div className="group relative bg-white dark:bg-cyber-900/50 p-6 rounded-2xl border border-gray-200 dark:border-cyber-800 shadow-sm transition-all duration-300 hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:shadow-[0_8px_30px_rgb(0,255,157,0.05)] hover:-translate-y-1 hover:border-green-500/30 overflow-hidden">
           <div className="absolute top-0 right-0 w-24 h-24 bg-green-500/5 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
           <div className="flex items-center space-x-4 relative z-10">
             <div className="p-3 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Lock size={28} />
             </div>
             <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Avg Safety Score</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white group-hover:text-green-500 dark:group-hover:text-green-400 transition-colors">{avgScore}%</p>
             </div>
           </div>
        </div>

      </div>

      {/* Account Details */}
      <div className="px-4">
        <div className="bg-white dark:bg-cyber-900/50 backdrop-blur-sm rounded-3xl border border-gray-200 dark:border-cyber-800 p-8 shadow-lg">
           <div className="flex items-center justify-between mb-8">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <span className="w-1 h-6 bg-cyber-accent rounded-full"></span>
                Account Information
              </h3>
           </div>
           
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                 <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">Username</label>
                 <div className="relative group">
                    <input 
                      type="text" 
                      disabled 
                      value={user.username} 
                      className="w-full p-4 bg-gray-50 dark:bg-cyber-950/50 border border-gray-200 dark:border-cyber-700 rounded-xl text-gray-700 dark:text-gray-300 transition-all opacity-70 group-hover:opacity-100" 
                    />
                    <Lock size={14} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400" />
                 </div>
              </div>
               <div className="space-y-2">
                 <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">Email Address</label>
                 <div className="relative group">
                    <input 
                      type="email" 
                      disabled 
                      value={user.email} 
                      className="w-full p-4 bg-gray-50 dark:bg-cyber-950/50 border border-gray-200 dark:border-cyber-700 rounded-xl text-gray-700 dark:text-gray-300 transition-all opacity-70 group-hover:opacity-100" 
                    />
                    <Lock size={14} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400" />
                 </div>
              </div>
               <div className="space-y-2">
                 <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">Member Since</label>
                 <input 
                    type="text" 
                    disabled 
                    value={new Date(user.joinedDate).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })} 
                    className="w-full p-4 bg-gray-50 dark:bg-cyber-950/50 border border-gray-200 dark:border-cyber-700 rounded-xl text-gray-700 dark:text-gray-300 transition-all opacity-70 hover:opacity-100" 
                 />
              </div>
               <div className="space-y-2">
                 <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider ml-1">Plan Status</label>
                 <div className="w-full p-4 bg-gray-50 dark:bg-cyber-950/50 border border-gray-200 dark:border-cyber-700 rounded-xl flex items-center justify-between transition-all hover:border-cyber-accent/30">
                    <div className="flex items-center space-x-3">
                      <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-accent opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-cyber-accent"></span>
                      </span>
                      <span className="font-semibold text-gray-900 dark:text-white">Premium Agent</span>
                    </div>
                    <span className="text-xs text-cyber-accent bg-cyber-accent/10 px-2 py-1 rounded border border-cyber-accent/20">ACTIVE</span>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};