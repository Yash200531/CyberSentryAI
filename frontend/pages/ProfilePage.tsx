import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import { updateUserAvatar } from '../services/storage';
import { Shield, Key, Lock, Activity, Server, AlertTriangle, UserCircle, Camera, UploadCloud } from 'lucide-react';

const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [isUploading, setIsUploading] = useState(false);

  if (!user) return null;

  const isAdmin = user.roles?.includes('admin');

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      
      // Basic validation
      if (!file.type.startsWith('image/')) {
        alert('Please upload a valid image file (JPG, PNG).');
        return;
      }
      if (file.size > 2 * 1024 * 1024) { // 2MB limit
        alert('File size too large. Max 2MB.');
        return;
      }

      setIsUploading(true);

      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64String = reader.result as string;
        try {
            // Call simulated backend
            const updatedUser = await updateUserAvatar(user.id, base64String);
            if (updatedUser) {
                // Update Context
                updateUser(updatedUser);
            }
        } catch (error) {
            console.error("Upload failed", error);
            alert("Failed to update profile image.");
        } finally {
            setIsUploading(false);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h1 className="text-3xl font-display font-bold text-white">Agent Profile</h1>

      {/* Identity Card */}
      <div className="glass-panel p-8 rounded-2xl border border-cyber-border relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4">
           <div className={`px-3 py-1 rounded border font-mono text-xs tracking-widest uppercase ${
             isAdmin 
               ? 'bg-cyber-accent/10 border-cyber-accent/50 text-cyber-accent' 
               : 'bg-cyber-primary/10 border-cyber-primary/50 text-cyber-primary'
           }`}>
             {isAdmin ? 'CLEARANCE: LEVEL 5 (ADMIN)' : 'CLEARANCE: LEVEL 3 (ANALYST)'}
           </div>
        </div>

        <div className="flex flex-col md:flex-row items-center md:items-start gap-8 relative z-10">
          <div className="relative group">
            <img 
              src={user.avatarUrl} 
              alt={user.email} 
              className="w-32 h-32 rounded-full border-4 border-cyber-border shadow-[0_0_20px_rgba(0,0,0,0.5)] object-cover"
            />
            <div className="absolute bottom-1 right-1 w-6 h-6 bg-cyber-success rounded-full border-4 border-cyber-dark" title="Online"></div>
            
            {/* Admin Upload Overlay */}
            {isAdmin && (
              <label htmlFor="profile-avatar-upload" className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                <input
                  id="profile-avatar-upload"
                  name="avatar"
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={isUploading}
                />
                {isUploading ? (
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                ) : (
                  <Camera className="text-white w-8 h-8" />
                )}
              </label>
            )}
          </div>
          
          <div className="text-center md:text-left space-y-2">
            <h2 className="text-4xl font-display font-bold text-white">{user.email}</h2>
            <p className="text-cyber-muted font-mono">{user.roles?.join(', ')}</p>
            <p className="text-gray-500 text-sm max-w-md pt-2">
              {isAdmin 
                ? 'Authorized to manage system protocols, override security locks, and access global threat intelligence feeds.'
                : 'Authorized for standard threat analysis, report generation, and red-team simulations.'}
            </p>
            {isAdmin && <p className="text-xs text-cyber-accent mt-2 flex items-center gap-1"><UploadCloud size={12}/> Admin Privilege: Hover image to update avatar.</p>}
          </div>
        </div>

        {/* Background decorative elements */}
        <div className="absolute -bottom-10 -right-10 w-64 h-64 bg-gradient-to-tl from-cyber-primary/10 to-transparent rounded-full blur-3xl pointer-events-none"></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Account Details */}
        <div className="glass-panel p-6 rounded-xl border border-cyber-border">
          <h3 className="text-xl font-display font-bold text-white mb-6 flex items-center gap-2">
            <UserCircle className="text-cyber-primary" /> Credentials
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-white/5">
              <span className="text-gray-400 text-sm">User ID</span>
              <span className="font-mono text-white text-sm">{user.id}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-white/5">
              <span className="text-gray-400 text-sm">MFA Status</span>
              <span className="text-cyber-success text-sm font-bold flex items-center gap-1">
                <Lock size={12} /> ENFORCED
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-white/5">
              <span className="text-gray-400 text-sm">Last Login</span>
              <span className="text-white text-sm font-mono">{new Date().toLocaleString()}</span>
            </div>
            <div className="pt-4">
              <button className="text-cyber-primary hover:text-white text-sm font-medium transition-colors">
                Change Access Password
              </button>
            </div>
          </div>
        </div>

        {/* Admin / Role Specific Panel */}
        <div className={`glass-panel p-6 rounded-xl border ${isAdmin ? 'border-cyber-accent/30' : 'border-cyber-border'}`}>
          <h3 className={`text-xl font-display font-bold mb-6 flex items-center gap-2 ${isAdmin ? 'text-cyber-accent' : 'text-white'}`}>
             {isAdmin ? <AlertTriangle /> : <Activity />}
             {isAdmin ? 'Admin Console' : 'Analyst Metrics'}
          </h3>

          {isAdmin ? (
            <div className="space-y-4">
              <p className="text-gray-400 text-sm mb-4">
                System-wide controls are active. Use caution when overriding defaults.
              </p>
              <button className="w-full py-3 bg-cyber-accent/10 border border-cyber-accent/50 text-cyber-accent rounded hover:bg-cyber-accent hover:text-black transition-all font-bold text-sm flex items-center justify-center gap-2">
                <Server size={16} /> FLUSH DNS CACHE
              </button>
              <button className="w-full py-3 bg-white/5 border border-white/10 text-white rounded hover:bg-white/10 transition-all font-bold text-sm flex items-center justify-center gap-2">
                <Key size={16} /> ROTATE API KEYS
              </button>
            </div>
          ) : (
             <div className="space-y-4">
               <div className="grid grid-cols-2 gap-4">
                 <div className="bg-black/30 p-4 rounded text-center">
                   <div className="text-2xl font-bold text-cyber-primary">142</div>
                   <div className="text-[10px] text-gray-500 uppercase tracking-wider">Scans Run</div>
                 </div>
                 <div className="bg-black/30 p-4 rounded text-center">
                   <div className="text-2xl font-bold text-cyber-success">98%</div>
                   <div className="text-[10px] text-gray-500 uppercase tracking-wider">Accuracy</div>
                 </div>
               </div>
               <div className="bg-cyber-primary/5 border border-cyber-primary/20 p-4 rounded text-sm text-gray-300">
                 <p>Your performance metrics are within the top 5% of the analyst pool.</p>
               </div>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;