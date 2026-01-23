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
          ? 'bg-blue-50 dark:bg-cyber-accent/10 text-blue-600 dark:text-cyber-accent border-l-4 border-blue-500 dark:border-cyber-accent shadow-sm'
          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-cyber-800'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </Link>
  );

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-cyber-950 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-300 overflow-hidden">
      
      {/* Premium Background Layer - Dark Mode */}
      <div className="fixed inset-0 z-0 premium-bg-pattern pointer-events-none opacity-0 dark:opacity-100 transition-opacity duration-500"></div>
      <div className="fixed inset-0 z-0 cyber-grid pointer-events-none opacity-0 dark:opacity-100 transition-opacity duration-500"></div>

      {/* Premium Background Layer - Light Mode */}
      <div className="fixed inset-0 z-0 light-premium-bg pointer-events-none opacity-100 dark:opacity-0 transition-opacity duration-500"></div>
      <div className="fixed inset-0 z-0 light-cyber-grid pointer-events-none opacity-100 dark:opacity-0 transition-opacity duration-500"></div>

      {/* Sidebar - Desktop */}
      <aside className="hidden md:flex flex-col w-64 border-r border-gray-200 dark:border-cyber-800 bg-white/80 dark:bg-cyber-900/80 backdrop-blur-xl fixed h-full z-20 shadow-[4px_0_24px_rgba(0,0,0,0.02)] dark:shadow-none">
        <div className="p-6 border-b border-gray-100 dark:border-cyber-800">
          <Link to="/" className="flex items-center space-x-2 group">
            <ShieldCheck size={32} className="text-blue-600 dark:text-cyber-accent drop-shadow-sm dark:drop-shadow-[0_0_8px_rgba(0,242,234,0.5)] group-hover:scale-110 transition-transform duration-300" />
            <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-cyber-accent transition-colors">
              Cyber<span className="text-blue-500 dark:text-cyber-accent group-hover:text-gray-900 dark:group-hover:text-white transition-colors">Sentry</span>
            </h1>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <NavItem to="/" icon={ShieldCheck} label="Scanner" />
          <NavItem to="/history" icon={History} label="History" />
          <NavItem to="/profile" icon={User} label="Profile" />
        </nav>

        <div className="p-4 border-t border-gray-100 dark:border-cyber-800 space-y-2">
           <button
            onClick={toggleTheme}
            className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-cyber-800 transition-colors"
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

          <Link to="/profile" className="block mt-4 group">
            <div className="px-4 py-2 rounded-xl transition-all duration-200 group-hover:bg-blue-50 dark:group-hover:bg-cyber-800/50 border border-transparent group-hover:border-blue-100 dark:group-hover:border-cyber-700">
               <div className="flex items-center space-x-3">
                  <div className="relative">
                    <img src={user?.avatarUrl} alt="Avatar" className="w-10 h-10 rounded-full border-2 border-white dark:border-cyber-700 shadow-sm group-hover:border-blue-200 dark:group-hover:border-cyber-accent transition-colors" />
                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-cyber-900 rounded-full"></div>
                  </div>
                  <div className="text-sm overflow-hidden">
                     <p className="font-bold truncate text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-cyber-accent transition-colors">{user?.username}</p>
                     <p className="text-xs text-blue-500 dark:text-gray-400 font-medium">View Profile</p>
                  </div>
               </div>
            </div>
          </Link>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="md:hidden fixed w-full z-30 bg-white/90 dark:bg-cyber-900/90 backdrop-blur-lg border-b border-gray-200 dark:border-cyber-800 px-4 py-3 flex justify-between items-center shadow-sm">
         <Link to="/" className="flex items-center space-x-2 text-blue-600 dark:text-cyber-accent">
            <ShieldCheck size={24} />
            <span className="font-bold text-lg text-gray-900 dark:text-white">CyberSentry</span>
         </Link>
         <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-gray-700 dark:text-gray-300">
            {isMobileMenuOpen ? <X /> : <Menu />}
         </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-20 bg-gray-900/50 backdrop-blur-sm md:hidden" onClick={() => setIsMobileMenuOpen(false)}>
          <div className="absolute right-0 top-0 h-full w-64 bg-white dark:bg-cyber-900 p-4 pt-20 shadow-2xl" onClick={e => e.stopPropagation()}>
             <nav className="space-y-2">
                <NavItem to="/" icon={ShieldCheck} label="Scanner" />
                <NavItem to="/history" icon={History} label="History" />
                <NavItem to="/profile" icon={User} label="Profile" />
                <hr className="border-gray-200 dark:border-cyber-800 my-2" />
                <button
                  onClick={toggleTheme}
                  className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-600 dark:text-gray-400"
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
             Designed And Developed by <span className="font-bold text-gray-700 dark:text-gray-200 tracking-wide">Team X</span>
           </p>
        </footer>
      </main>
    </div>
  );
};