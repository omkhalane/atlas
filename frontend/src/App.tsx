import { useState, useEffect, useRef } from 'react'
import './App.css'

interface AgentEvent {
  type: string;
  content?: string;
  action?: string;
  parameters?: any;
  result?: any;
  error?: string;
}

function App() {
  const [task, setTask] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [execId, setExecId] = useState<string | null>(null)
  
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [activeTab, setActiveTab] = useState('browser')
  
  const [files, setFiles] = useState<{name: string, path: string}[]>([])
  const [browserActive, setBrowserActive] = useState(true)
  
  const [planTasks, setPlanTasks] = useState<string[]>([])
  const [currentTaskIdx, setCurrentTaskIdx] = useState<number>(-1)
  
  const [securityHalt, setSecurityHalt] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [events])

  const handleExecute = async () => {
    if (!task.trim()) return;
    setIsExecuting(true)
    setEvents([{ type: 'user_prompt', content: task }])
    setSecurityHalt(null)
    setFiles([])
    setBrowserActive(true)
    setPlanTasks([])
    setCurrentTaskIdx(-1)
    
    try {
      const res = await fetch('http://localhost:8000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: task })
      })
      const data = await res.json()
      setExecId(data.exec_id)
      setTask('')
    } catch (err) {
      console.error(err)
      setIsExecuting(false)
    }
  }

  useEffect(() => {
    if (!execId) return;
    
    const es = new EventSource(`http://localhost:8000/api/stream/${execId}`)
    
    es.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        
        if (msg.type === "security_halt") {
          setSecurityHalt(msg)
          return
        }
        
        if (msg.type === "file_written") {
          setFiles(prev => {
             if (!prev.find(f => f.path === msg.path)) {
                return [...prev, {name: msg.name, path: msg.path}]
             }
             return prev
          })
          return
        }
        
        if (msg.type === "plan") {
           setPlanTasks(msg.tasks || [])
           return
        }
        
        if (msg.type === "thought" && msg.current_task_idx !== undefined) {
           setCurrentTaskIdx(msg.current_task_idx)
        }
        
        setEvents(prev => [...prev, msg])
        
        if (msg.type === "finish" || msg.type === "error") {
          setIsExecuting(false)
          es.close()
        }
      } catch (e) {
        console.error("Failed to parse SSE message", e)
      }
    }
    
    es.onerror = () => {
      es.close()
    }
    
    return () => es.close()
  }, [execId])

  const handleApprove = async () => {
    if (!execId) return;
    try {
      await fetch(`http://localhost:8000/api/approve/${execId}`, { method: 'POST' })
      setSecurityHalt(null)
    } catch (err) {}
  }

  const handleDeny = () => {
    setSecurityHalt(null)
  }
  
  // Syntax highlight for JSON blocks
  const formatJson = (obj: any) => {
      if (!obj) return "";
      const str = JSON.stringify(obj, null, 2);
      return str;
  }

  return (
    <div className="app-container">
      {/* THIN SIDEBAR (Leftmost) */}
      <div className="sidebar-left">
         <div className="sidebar-icon">⊞</div>
         <div className="sidebar-icon">+</div>
         <div className="sidebar-icon">🌐</div>
         <div className="sidebar-icon">🕒</div>
         <div className="sidebar-icon">📦</div>
         <div className="sidebar-icon">📄</div>
         <div className="sidebar-icon">🐛</div>
         
         <div className="sidebar-bottom">
            <div className="sidebar-icon">⚙</div>
            <div className="avatar">Om</div>
         </div>
      </div>

      <div className="main-content">
        {/* CHAT PANE */}
        <div className="chat-pane">
          <div className="chat-history">
            {events.map((ev, idx) => {
              if (ev.type === 'user_prompt') {
                return (
                  <div key={idx} className="message-wrapper">
                    <div className="user-message">{ev.content}</div>
                  </div>
                )
              }
              if (ev.type === 'thought') {
                return (
                  <div key={idx} className="agent-text">
                    {ev.content}
                  </div>
                )
              }
              if (ev.type === 'action') {
                return (
                  <div key={idx} className="message-wrapper">
                    <div className="agent-cmd-line">
                      &gt;_ Ran command {ev.action === 'command' ? ev.parameters?.command : ev.action}
                    </div>
                    {ev.action !== 'command' && (
                        <div className="command-card">
                          <div className="command-header">
                            <span>command</span>
                            <span>📋</span>
                          </div>
                          <div className="command-body">
                            {formatJson(ev.parameters)}
                          </div>
                        </div>
                    )}
                  </div>
                )
              }
              if (ev.type === 'observation') {
                return (
                  <div key={idx} className="command-card">
                    <div className="command-header">
                      <span>output</span>
                      <span>📋</span>
                    </div>
                    <div className="command-body">
                      {ev.content}
                    </div>
                  </div>
                )
              }
              if (ev.type === 'finish') {
                return (
                  <div key={idx} className="agent-text" style={{color: '#fff', marginTop: 12}}>
                    Done.
                  </div>
                )
              }
              if (ev.type === 'error') {
                return (
                  <div key={idx} className="agent-text" style={{color: '#ef4444'}}>
                    Error: {ev.error}
                  </div>
                )
              }
              return null;
            })}
            <div ref={messagesEndRef} />
          </div>
          
          {/* FLOATING STEER INPUT */}
          <div className="steer-container">
            {planTasks.length > 0 && (
               <div className="steer-checklist">
                  <div className="checklist-header">
                     <span>Tasks</span>
                     <span>{currentTaskIdx + 1}/{planTasks.length} ⌃</span>
                  </div>
                  {planTasks.map((t, i) => (
                    <div key={i} className="checklist-item">
                      {i < currentTaskIdx ? (
                         <span className="checklist-icon done">✅</span>
                      ) : i === currentTaskIdx ? (
                         <span className="checklist-icon spinner">↻</span>
                      ) : (
                         <span className="checklist-icon">○</span>
                      )}
                      <span>{t}</span>
                    </div>
                  ))}
               </div>
            )}
            <div className="steer-input-row">
              <button className="icon-btn">📎</button>
              <button className="icon-btn tag">✴ Opus 5 ⌄</button>
              <input 
                type="text" 
                className="steer-input"
                placeholder={isExecuting ? "Reply to steer the agent..." : "Send another message to update direction"}
                value={task}
                onChange={(e) => setTask(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleExecute()}
              />
              <button onClick={handleExecute} className={`steer-submit ${task ? 'active' : ''}`}>
                 {isExecuting ? '⏹' : '↑'}
              </button>
            </div>
          </div>
        </div>

        {/* WORKSPACE PANE */}
        <div className="workspace-pane">
          <div className="tabs-header">
            <button className={`tab ${activeTab === 'browser' ? 'active' : ''}`} onClick={() => setActiveTab('browser')}>🌐 Browser</button>
            <button className={`tab ${activeTab === 'files' ? 'active' : ''}`} onClick={() => setActiveTab('files')}>📁 Files ({files.length})</button>
          </div>
          
          <div className="tab-content">
            {activeTab === 'browser' && browserActive && (
              <div className="browser-frame">
                 <div className="browser-toolbar">
                    <div className="mac-dots"><span></span><span></span><span></span></div>
                    <div className="browser-nav">
                        <span>←</span><span>→</span><span>↻</span>
                    </div>
                    <div className="browser-url">
                        <span style={{opacity: 0.5}}>🔒</span>
                        cloud.browser-use.com/v4/session
                    </div>
                    <div className="browser-nav">
                        <span>+</span>
                    </div>
                 </div>
                 <div className="browser-viewport">
                    <img 
                       src={`http://localhost:8000/api/browser_screenshot?t=${new Date().getTime()}`} 
                       style={{width: '100%', height: '100%', objectFit: 'contain'}} 
                       alt="Live Browser"
                       onError={(e) => {
                           e.currentTarget.style.display = 'none';
                           e.currentTarget.parentElement!.innerHTML = '<div style="opacity: 0.2"><svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 22h20L12 2z"/></svg></div>';
                       }}
                    />
                 </div>
              </div>
            )}
            
            {activeTab === 'files' && (
              <div className="file-list">
                 {files.map((f, i) => (
                   <div key={i} className="file-row">
                     <div className="file-name">
                        <span>📄</span>
                        <span>{f.name}</span>
                     </div>
                     <div className="file-meta">
                        <span>{(Math.random() * 500 + 10).toFixed(0)} KB</span>
                        <span>⬇</span>
                     </div>
                   </div>
                 ))}
              </div>
            )}
            
          </div>
        </div>
      </div>

      {/* Security Modal */}
      {securityHalt && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header warning">
              <h3>⚠️ HUMAN APPROVAL REQUIRED</h3>
            </div>
            <div className="modal-body">
              <p>{securityHalt.detail}</p>
              <div className="code-preview" style={{background: '#111', padding: '12px', marginTop: '12px', fontFamily: 'monospace'}}>
                <strong>Target Path:</strong> {securityHalt.data?.path}
              </div>
            </div>
            <div className="modal-actions">
              <button onClick={handleDeny} className="btn-deny">DENY</button>
              <button onClick={handleApprove} className="btn-approve">APPROVE</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
