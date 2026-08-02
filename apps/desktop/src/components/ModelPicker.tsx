import React, { useState } from 'react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { ChevronDown, Check, Zap, BrainCircuit, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const models = [
  { id: 'gemini-3.1-pro', name: 'Gemini 3.1 Pro', provider: 'Google', icon: BrainCircuit, tags: ['Reasoning', 'Premium'] },
  { id: 'gemini-3.1-flash', name: 'Gemini 3.1 Flash', provider: 'Google', icon: Zap, tags: ['Fast'] },
  { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', provider: 'Anthropic', icon: BrainCircuit, tags: ['Premium'] },
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', icon: BrainCircuit, tags: ['Premium'] },
  { id: 'local-llama-3', name: 'Llama 3 8B', provider: 'Local', icon: Lock, tags: ['Private', 'Fast'] },
];

export const ModelPicker: React.FC = () => {
  const [selected, setSelected] = useState(models[0]);
  const [open, setOpen] = useState(false);

  return (
    <DropdownMenu.Root open={open} onOpenChange={setOpen}>
      <DropdownMenu.Trigger asChild>
        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[var(--color-bg-hover)] hover:bg-[var(--color-bg-selected)] border border-[var(--color-border-subtle)] transition-colors text-[13px] font-medium text-[var(--color-text-primary)] group outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]">
          <selected.icon size={14} className="text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)] transition-colors" />
          <span>{selected.name}</span>
          <ChevronDown size={14} className={`text-[var(--color-text-tertiary)] transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
        </button>
      </DropdownMenu.Trigger>

      <AnimatePresence>
        {open && (
          <DropdownMenu.Portal forceMount>
            <DropdownMenu.Content asChild align="start" sideOffset={8}>
              <motion.div
                initial={{ opacity: 0, y: 4, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 4, scale: 0.98 }}
                transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
                className="w-64 bg-[var(--color-bg-modal)] rounded-xl border border-[var(--color-border-subtle)] shadow-[0_10px_40px_rgba(0,0,0,0.5)] p-1 z-[100] origin-bottom-left overflow-hidden"
              >
                <div className="px-2 py-1.5 border-b border-[var(--color-border-subtle)] mb-1">
                  <span className="text-[11px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider">Models</span>
                </div>
                
                {models.map(model => (
                  <DropdownMenu.Item
                    key={model.id}
                    className="flex items-center justify-between px-2 py-2 rounded-lg cursor-pointer outline-none hover:bg-[var(--color-bg-hover)] focus:bg-[var(--color-bg-hover)] data-[state=checked]:bg-[var(--color-bg-selected)] transition-colors group"
                    onClick={() => setSelected(model)}
                  >
                    <div className="flex items-center gap-2.5">
                      <model.icon size={15} className={selected.id === model.id ? 'text-[var(--color-text-primary)]' : 'text-[var(--color-text-secondary)]'} />
                      <div className="flex flex-col">
                        <span className={`text-[13px] ${selected.id === model.id ? 'text-[var(--color-text-primary)] font-medium' : 'text-[var(--color-text-secondary)]'}`}>
                          {model.name}
                        </span>
                        <span className="text-[11px] text-[var(--color-text-tertiary)]">
                          {model.provider}
                        </span>
                      </div>
                    </div>
                    {selected.id === model.id && (
                      <Check size={14} className="text-[var(--color-text-primary)]" />
                    )}
                  </DropdownMenu.Item>
                ))}
              </motion.div>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        )}
      </AnimatePresence>
    </DropdownMenu.Root>
  );
};
