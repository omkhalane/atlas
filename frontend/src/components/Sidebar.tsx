import React from 'react';
import { Home, MessageSquarePlus, Bot, Blocks, Clock, LineChart, Settings, Terminal, Activity, Brain, User } from 'lucide-react';
import { motion } from 'framer-motion';

const topIcons = [
  { id: 'home', icon: Home, label: 'Home' },
  { id: 'new', icon: MessageSquarePlus, label: 'New Chat' },
  { id: 'agents', icon: Bot, label: 'Agents' },
  { id: 'plugins', icon: Blocks, label: 'Plugins' },
  { id: 'history', icon: Clock, label: 'History' },
  { id: 'analytics', icon: LineChart, label: 'Analytics' },
];

const bottomIcons = [
  { id: 'terminal', icon: Terminal, label: 'Terminal' },
  { id: 'logs', icon: Activity, label: 'Logs' },
  { id: 'memory', icon: Brain, label: 'Memory' },
  { id: 'settings', icon: Settings, label: 'Settings' },
  { id: 'profile', icon: User, label: 'Profile' },
];

export const Sidebar: React.FC = () => {
  return (
    <div className="w-[72px] h-full bg-[#111214] flex flex-col justify-between items-center py-6 border-r border-[#ffffff0d] flex-shrink-0 z-50">
      
      <div className="flex flex-col gap-6">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4">
           <img src="/favicon.png" alt="Atlas" className="w-8 h-8 opacity-80 hover:opacity-100 transition-opacity" />
        </div>
        
        {topIcons.map((item) => (
          <motion.button
            key={item.id}
            whileHover={{ scale: 1.04, backgroundColor: 'rgba(255,255,255,0.05)' }}
            transition={{ duration: 0.15 }}
            className="w-12 h-12 flex items-center justify-center rounded-[12px] text-[#A6A6A6] hover:text-white cursor-pointer outline-none"
            title={item.label}
          >
            <item.icon size={24} strokeWidth={1.5} />
          </motion.button>
        ))}
      </div>

      <div className="flex flex-col gap-6">
        {bottomIcons.map((item) => (
          <motion.button
            key={item.id}
            whileHover={{ scale: 1.04, backgroundColor: 'rgba(255,255,255,0.05)' }}
            transition={{ duration: 0.15 }}
            className="w-12 h-12 flex items-center justify-center rounded-[12px] text-[#A6A6A6] hover:text-white cursor-pointer outline-none"
            title={item.label}
          >
            <item.icon size={24} strokeWidth={1.5} />
          </motion.button>
        ))}
      </div>
    </div>
  );
};
