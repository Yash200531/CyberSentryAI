import React, { useState } from 'react';
import { useStore } from '../contexts/StoreContext';
import { Verdict } from '../types';
import { Trash2, ExternalLink, MessageSquare, Clock, Search, Filter } from 'lucide-react';

export const HistoryPage: React.FC = () => {
  const { history, clearHistory } = useStore();
  const [searchQuery, setSearchQuery] = useState('');

  // Filter logic
  const filteredHistory = history.filter(item => 
    item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.verdict.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.reasoning.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const getVerdictBadge = (verdict: Verdict) => {
    let colorClass = '';
    switch(verdict) {
      case Verdict.SAFE: colorClass = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800'; break;
      case Verdict.SPAM: colorClass = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800'; break;
      case Verdict.SUSPICIOUS: colorClass = 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400 border-orange-200 dark:border-orange-800'; break;
      default: colorClass = 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400 border-gray-200 dark:border-gray-700';
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-bold border ${colorClass}`}>
        {verdict}
      </span>
    );
  };

  return (
    <div className="space-y-6 page-animate">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Scan History</h2>
          <p className="text-gray-500 dark:text-gray-400">Archive of your past analyses</p>
        </div>
        
        {/* Search and Actions */}
        <div className="w-full md:w-auto flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1 sm:min-w-[250px]">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" size={16} />
             <input
                 type="text"
                 placeholder="Search content, verdict, type..."
                 value={searchQuery}
                 onChange={(e) => setSearchQuery(e.target.value)}
                 className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-gray-200 dark:border-cyber-700 bg-white dark:bg-cyber-900 focus:ring-1 focus:ring-cyber-accent focus:border-cyber-accent outline-none text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 transition-all"
             />
          </div>

          {history.length > 0 && (
            <button 
              onClick={clearHistory}
              className="flex items-center justify-center space-x-2 text-red-500 hover:text-red-600 dark:hover:text-red-400 transition-colors px-4 py-2 rounded-lg bg-red-50 hover:bg-red-100 dark:bg-red-900/10 dark:hover:bg-red-900/20 whitespace-nowrap"
            >
              <Trash2 size={16} />
              <span className="text-sm font-medium">Clear Logs</span>
            </button>
          )}
        </div>
      </div>

      {history.length === 0 ? (
        <div className="text-center py-20 bg-white dark:bg-cyber-800 rounded-2xl border border-dashed border-gray-300 dark:border-cyber-600">
          <Clock size={48} className="mx-auto text-gray-300 dark:text-cyber-600 mb-4" />
          <p className="text-gray-500 dark:text-gray-400 text-lg">No history logs found.</p>
          <p className="text-gray-400 text-sm mt-2">Start scanning links or text to populate this list.</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-cyber-800 rounded-xl shadow-sm border border-gray-200 dark:border-cyber-700 overflow-hidden">
          {filteredHistory.length === 0 ? (
             <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                <Filter size={32} className="mx-auto mb-2 opacity-50"/>
                <p>No results found for "{searchQuery}"</p>
             </div>
          ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gray-50 dark:bg-cyber-900 border-b border-gray-200 dark:border-cyber-700">
                <tr>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Verdict</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Content</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Score</th>
                  <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-cyber-700">
                {filteredHistory.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-cyber-700/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getVerdictBadge(item.verdict)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-start space-x-2">
                        <div className="mt-1 text-gray-400 flex-shrink-0">
                          {item.type === 'LINK' ? <ExternalLink size={14} /> : <MessageSquare size={14} />}
                        </div>
                        <div>
                           <p className="text-sm text-gray-900 dark:text-gray-200 line-clamp-2 font-mono max-w-md break-all">
                            {item.content}
                           </p>
                           <p className="text-xs text-gray-500 mt-1 line-clamp-1">{item.reasoning}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                       <div className="flex items-center space-x-2">
                          <div className="w-16 bg-gray-200 dark:bg-cyber-900 rounded-full h-2 overflow-hidden">
                             <div 
                                className={`h-full rounded-full ${item.score > 80 ? 'bg-green-500' : item.score > 50 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                                style={{ width: `${item.score}%` }}
                             />
                          </div>
                          <span className="text-xs font-mono">{item.score}/100</span>
                       </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(item.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          )}
        </div>
      )}
    </div>
  );
};