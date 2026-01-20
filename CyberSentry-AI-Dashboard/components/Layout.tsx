import React from 'react';
import { useStore } from '../contexts/StoreContext';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, History, User, LogOut, Moon, Sun, Menu, X } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, theme, toggleTheme } = useStore();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  const isActive = (path: string) => location.pathname === path;

  const NavItem = ({ to, icon: Icon, label }: { to: string, icon: any, label: string }) => (
    <Link
      to={to}
      onClick={() => setIsMobileMenuOpen(false)}
      className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
        isActive(to)
          ? 'bg-cyber-accent/10 text-cyber-accent border-l-4 border-cyber-accent'
          : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-cyber-800'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </Link>
  );

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-cyber-950 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-300 overflow-hidden">
      
      {/* Premium Background Layer */}
      <div className="fixed inset-0 z-0 premium-bg-pattern pointer-events-none opacity-0 dark:opacity-100 transition-opacity duration-500"></div>
      <div className="fixed inset-0 z-0 cyber-grid pointer-events-none opacity-0 dark:opacity-100 transition-opacity duration-500"></div>

      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col w-64 border-r border-gray-200 dark:border-cyber-800 bg-white dark:bg-cyber-900/80 backdrop-blur-xl fixed h-full z-20">
        <div className="p-6 border-b border-gray-200 dark:border-cyber-800">
          <Link to="/" className="flex items-center space-x-2 text-cyber-accent group">
            <ShieldCheck size={32} className="drop-shadow-[0_0_8px_rgba(0,242,234,0.5)] group-hover:scale-110 transition-transform duration-300" />
            <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white group-hover:text-cyber-accent transition-colors">
              Cyber<span className="text-cyber-accent group-hover:text-white transition-colors">Sentry</span>
            </h1>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <NavItem to="/" icon={ShieldCheck} label="Scanner" />
          <NavItem to="/history" icon={History} label="History" />
          <NavItem to="/profile" icon={User} label="Profile" />
        </nav>

        <div className="p-4 border-t border-gray-200 dark:border-cyber-800 space-y-2">
           <button
            onClick={toggleTheme}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-cyber-800 transition-colors"
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
          </button>
          
          <button
            onClick={logout}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors"
          >
            <LogOut size={20} />
            <span>Sign Out</span>
          </button>

          <div className="px-4 py-2 mt-4">
             <div className="flex items-center space-x-3">
                <img src={user?.avatarUrl} alt="Avatar" className="w-8 h-8 rounded-full border border-cyber-accent" />
                <div className="text-sm">
                   <p className="font-semibold truncate w-32">{user?.username}</p>
                   <p className="text-xs text-gray-500 dark:text-gray-400">Pro Member</p>
                </div>
             </div>
          </div>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="md:hidden fixed w-full z-30 bg-white dark:bg-cyber-900 border-b border-gray-200 dark:border-cyber-800 px-4 py-3 flex justify-between items-center">
         <Link to="/" className="flex items-center space-x-2 text-cyber-accent">
            <ShieldCheck size={24} />
            <span className="font-bold text-lg text-gray-900 dark:text-white">CyberSentry</span>
         </Link>
         <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2">
            {isMobileMenuOpen ? <X /> : <Menu />}
         </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-20 bg-gray-900/50 md:hidden" onClick={() => setIsMobileMenuOpen(false)}>
          <div className="absolute right-0 top-0 h-full w-64 bg-white dark:bg-cyber-900 p-4 pt-20" onClick={e => e.stopPropagation()}>
             <nav className="space-y-2">
                <NavItem to="/" icon={ShieldCheck} label="Scanner" />
                <NavItem to="/history" icon={History} label="History" />
                <NavItem to="/profile" icon={User} label="Profile" />
                <hr className="border-gray-200 dark:border-cyber-800 my-2" />
                <button
                  onClick={toggleTheme}
                  className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-500 dark:text-gray-400"
                >
                  {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                  <span>Toggle Theme</span>
                </button>
                <button
                  onClick={logout}
                  className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-red-500"
                >
                  <LogOut size={20} />
                  <span>Sign Out</span>
                </button>
             </nav>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 md:ml-64 relative z-10 flex flex-col h-screen overflow-y-auto">
        <div className="flex-1 p-4 md:p-8 pt-20 md:pt-8 max-w-4xl mx-auto w-full">
          {children}
        </div>
        
        {/* Footer */}
        <footer className="w-full py-6 text-center text-sm text-gray-500 dark:text-gray-500">
           <p>
             Copyright 2026 CyberSentry AI <span className="hidden sm:inline">|</span> <br className="sm:hidden" />
             Designed And Developed by <span className="font-bold text-gray-800 dark:text-gray-200 tracking-wide">Team X</span>
           </p>
        </footer>
      </main>
    </div>
  );
};