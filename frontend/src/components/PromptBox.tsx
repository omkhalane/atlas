import React, { useRef, useEffect, useState } from 'react';
import { Paperclip, Mic, MicOff, ArrowUp, X, File as FileIcon, Image as ImageIcon } from 'lucide-react';
import { useStore } from '../store/useStore';
import { motion, AnimatePresence } from 'framer-motion';
import { ModelPicker } from './ModelPicker';

export const PromptBox: React.FC = () => {
  const { taskInput, setTaskInput, isExecuting, setIsExecuting, setExecId, activeConversationId } = useStore();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  
  // Voice & Media state
  const [isListening, setIsListening] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Setup Speech Recognition
    if ('webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        
        if (finalTranscript) {
          setTaskInput((prev: string) => prev + (prev.endsWith(' ') ? '' : ' ') + finalTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        textareaRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (recognitionRef.current) {
         recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTaskInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachments(prev => [...prev, ...Array.from(e.target.files!)]);
    }
    // reset
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleExecute = async () => {
    if ((!taskInput.trim() && attachments.length === 0) || isExecuting) return;
    
    setIsExecuting(true);
    try {
      // If we had a real backend supporting file uploads, we'd use FormData here.
      // For now, just send the text goal.
      const payload = { 
         goal: taskInput + (attachments.length > 0 ? ` [Attached ${attachments.length} files]` : ''),
         conversation_id: activeConversationId
      };
      
      const res = await fetch('http://localhost:8000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setExecId(data.exec_id);
      setTaskInput('');
      setAttachments([]);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (err) {
      console.error(err);
      setIsExecuting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleExecute();
    }
  };

  return (
    <motion.div 
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-[860px] px-4 z-40"
    >
      <div 
        className={`bg-[var(--color-bg-card)] rounded-[24px] shadow-[0_10px_40px_rgba(0,0,0,0.6)] border transition-all duration-200 flex flex-col p-2 gap-2 ${
          isFocused || isListening ? 'border-[var(--color-border-active)] shadow-[0_0_20px_rgba(255,255,255,0.05)]' : 'border-[var(--color-border-subtle)]'
        }`}
      >
        {/* Attachments Preview Area */}
        <AnimatePresence>
          {attachments.length > 0 && (
            <motion.div 
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="flex flex-wrap gap-2 px-3 pt-2"
            >
              {attachments.map((file, i) => (
                <div key={i} className="flex items-center gap-2 bg-[var(--color-bg-hover)] border border-[var(--color-border-subtle)] rounded-lg py-1.5 px-2.5 max-w-[200px]">
                  {file.type.startsWith('image/') ? (
                    <ImageIcon size={14} className="text-[var(--color-text-secondary)] shrink-0" />
                  ) : (
                    <FileIcon size={14} className="text-[var(--color-text-secondary)] shrink-0" />
                  )}
                  <span className="text-[12px] text-[var(--color-text-primary)] truncate flex-1">{file.name}</span>
                  <button onClick={() => removeAttachment(i)} className="text-[var(--color-text-tertiary)] hover:text-white shrink-0">
                    <X size={14} />
                  </button>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex px-3 pt-2">
          <textarea 
            ref={textareaRef}
            value={taskInput}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={isListening ? "Listening..." : "Ask Atlas to do anything... (Ctrl+L)"}
            className={`flex-1 bg-transparent border-none outline-none text-[var(--color-text-primary)] text-[15px] placeholder-[var(--color-text-tertiary)] font-primary resize-none min-h-[44px] max-h-[200px] py-1 leading-relaxed scrollbar-thin ${isListening ? 'text-[var(--color-accent)] placeholder-[var(--color-accent)]' : ''}`}
            rows={1}
            autoFocus
          />
        </div>

        <div className="flex items-center justify-between px-2 pb-1 pt-2">
          <div className="flex items-center gap-2">
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="w-8 h-8 flex items-center justify-center rounded-lg text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-hover)] transition-colors outline-none"
            >
              <Paperclip size={18} strokeWidth={2} />
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileSelect} 
              className="hidden" 
              multiple 
            />
            <ModelPicker />
          </div>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={toggleListening}
              className={`w-8 h-8 flex items-center justify-center rounded-lg transition-colors outline-none ${
                isListening 
                  ? 'bg-[var(--color-danger-transparent)] text-[var(--color-danger)] animate-pulse' 
                  : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-hover)]'
              }`}
            >
              {isListening ? <MicOff size={18} strokeWidth={2} /> : <Mic size={18} strokeWidth={2} />}
            </button>

            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleExecute}
              disabled={(!taskInput.trim() && attachments.length === 0) || isExecuting}
              className={`w-9 h-9 flex items-center justify-center rounded-full transition-colors ${
                (taskInput.trim() || attachments.length > 0) && !isExecuting ? 'bg-[var(--color-accent)] text-black shadow-lg shadow-white/10' : 'bg-[var(--color-bg-hover)] text-[var(--color-text-tertiary)] cursor-not-allowed'
              }`}
            >
              {isExecuting ? (
                <div className="w-3.5 h-3.5 bg-black rounded-sm animate-pulse" /> // Stop square
              ) : (
                <ArrowUp size={18} strokeWidth={2.5} />
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
