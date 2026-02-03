import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { LayoutDashboard, Search, History, LogOut, Info, Users, Settings, ShieldAlert } from 'lucide-react';
import Logo from './Logo';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = (e: React.MouseEvent) => {
    e.stopPropagation();
    logout();
    navigate('/');
  };

  const handleProfileClick = () => {
    navigate('/app/profile');
  };

  return (
    <div className="min-h-screen bg-cyber-dark text-gray-100 cyber-grid flex">
      {/* Sidebar */}
      {/* Increased z-index to z-50 to ensure it floats above all main content overlays, charts, and animations */}
      <aside className="w-64 fixed inset-y-0 left-0 glass-panel z-50 hidden md:flex flex-col border-r border-cyber-border shadow-[4px_0_24px_rgba(0,0,0,0.4)]">
        <div className="h-16 flex items-center px-6 border-b border-cyber-border bg-cyber-panel/50 backdrop-blur-md">
          <Logo size="medium" />
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto custom-scrollbar">
          <NavItem to="/app/dashboard" icon={<LayoutDashboard size={20} />} label="Command Center" />
          <NavItem to="/app/scan" icon={<Search size={20} />} label="New Scan" />
          <NavItem to="/app/history" icon={<History size={20} />} label="Scan History" />
          <NavItem to="/app/recovery" icon={<ShieldAlert size={20} />} label="Recovery Assistant" />
          
          <div className="pt-4 mt-4 border-t border-cyber-border/50">
             <p className="px-4 text-xs font-mono text-gray-500 uppercase mb-2">System Info</p>
             <NavItem to="/app/about" icon={<Users size={20} />} label="About Sentry" />
             <NavItem to="/app/info" icon={<Info size={20} />} label="Tech Stack" />
          </div>
        </nav>

        <div className="p-4 border-t border-cyber-border bg-cyber-panel/30">
          {/* User Profile Section - Now Interactive */}
          <button 
            onClick={handleProfileClick}
            className="flex items-center w-full mb-4 p-2 rounded-lg hover:bg-white/10 transition-all duration-200 group text-left focus:outline-none focus:ring-2 focus:ring-cyber-primary/50 cursor-pointer"
            aria-label="User Profile"
          >
            <div className="relative">
              <img 
                src={user?.avatarUrl} 
                alt="User" 
                className="w-10 h-10 rounded-full border-2 border-cyber-primary group-hover:border-cyber-secondary transition-colors object-cover" 
              />
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-cyber-success rounded-full border-2 border-cyber-dark"></div>
            </div>
            <div className="ml-3 overflow-hidden">
              <p className="text-sm font-medium text-white truncate group-hover:text-cyber-primary transition-colors">{user?.email}</p>
              <p className="text-xs text-cyber-muted truncate group-hover:text-gray-300">{user?.roles?.join(', ')}</p>
            </div>
            <Settings size={16} className="ml-auto text-cyber-muted opacity-0 group-hover:opacity-100 transition-opacity" />
          </button>

          <button 
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm font-medium text-cyber-muted hover:text-cyber-accent hover:bg-white/5 rounded-md transition-colors border border-transparent hover:border-cyber-accent/20"
          >
            <LogOut size={18} className="mr-2" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 relative min-h-screen z-0">
        {/* Mobile Header (Simplified) */}
          <header className="md:hidden h-16 glass-panel flex items-center justify-between px-4 sticky top-0 z-40 border-b border-cyber-border">
            <Logo size="small" showText={false} />
            <button onClick={handleLogout} className="text-cyber-muted"><LogOut size={20} /></button>
          </header>

        <div className="p-6 max-w-7xl mx-auto pb-20">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

const NavItem: React.FC<{ to: string; icon: React.ReactNode; label: string }> = ({ to, icon, label }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 group ${
        isActive
          ? 'bg-cyber-primary/10 text-cyber-primary border border-cyber-primary/20 shadow-[0_0_15px_rgba(6,182,212,0.3)]'
          : 'text-gray-400 hover:bg-white/5 hover:text-white'
      }`
    }
  >
    <span className="mr-3 group-hover:scale-110 transition-transform">{icon}</span>
    {label}
  </NavLink>
);

export default Layout;