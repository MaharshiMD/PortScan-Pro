import React, { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  Terminal, 
  Sliders, 
  Play, 
  Download, 
  Copy, 
  Check, 
  AlertCircle, 
  Cpu, 
  Clock, 
  Activity, 
  Laptop,
  CheckCircle,
  HelpCircle,
  Sparkles
} from 'lucide-react';

export default function App() {
  // Scan parameters
  const [target, setTarget] = useState('scanme.nmap.org');
  const [scanType, setScanType] = useState('common'); // 'common' or 'custom'
  const [startPort, setStartPort] = useState(1);
  const [endPort, setEndPort] = useState(100);
  const [threads, setThreads] = useState(60);
  const [timeout, setTimeoutVal] = useState(0.3);
  const [skipPing, setSkipPing] = useState(true);
  
  // App states
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState([]);
  const [results, setResults] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  
  const terminalEndRef = useRef(null);

  // Auto-scroll terminal logs
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Log printing helper
  const addLog = (message, type = 'info') => {
    setLogs(prev => [...prev, { text: message, type, time: new Date().toLocaleTimeString() }]);
  };

  // Run mock scan logic
  const runSimulatedScan = () => {
    addLog(`[*] [DEMO MODE] Resolving host: ${target}...`, 'info');
    
    setTimeout(() => {
      addLog(`[+] [DEMO MODE] Target resolved to: 45.33.32.156`, 'success');
      addLog(`[*] [DEMO MODE] Bypassing ICMP Ping sweep.`, 'warning');
      addLog(`[*] [DEMO MODE] Initializing scanner pool with ${threads} virtual threads...`, 'info');
    }, 600);

    setTimeout(() => {
      addLog(`[*] [DEMO MODE] Commencing port connection checks...`, 'info');
    }, 1200);

    // Dynamic scanning updates
    let currentPct = 10;
    const progressInterval = setInterval(() => {
      currentPct += Math.floor(Math.random() * 15) + 5;
      if (currentPct >= 90) {
        clearInterval(progressInterval);
        setProgress(90);
      } else {
        setProgress(currentPct);
        // Randomly output mock port checks
        if (currentPct % 3 === 0) {
          addLog(`[*] [DEMO MODE] Scanning port range index...`, 'muted');
        }
      }
    }, 300);

    setTimeout(() => {
      clearInterval(progressInterval);
      setProgress(100);
      
      const mockResult = {
        target: target,
        target_ip: '45.33.32.156',
        scan_time: 1.48 + (threads * 0.002),
        total_scanned: scanType === 'common' ? 12 : (endPort - startPort + 1),
        closed_ports_count: scanType === 'common' ? 9 : (endPort - startPort - 2),
        open_ports: [
          { port: 22, service: 'SSH', banner: 'SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7' },
          { port: 80, service: 'HTTP', banner: 'Server: Apache/2.4.25 (Debian)' },
          { port: 9929, service: 'nping-echo', banner: 'No banner available' }
        ].filter(p => {
          if (scanType === 'common') return true;
          return p.port >= startPort && p.port <= endPort;
        })
      };

      // Output found ports to terminal
      mockResult.open_ports.forEach(p => {
        addLog(`[+] Found OPEN port: ${p.port} [${p.service}] - Banner: ${p.banner}`, 'success');
      });

      addLog(`[+] Scan finished. Scanned ${mockResult.total_scanned} ports. Found ${mockResult.open_ports.length} open.`, 'success');
      setResults(mockResult);
      setIsScanning(false);
    }, 4000);
  };

  // Copy local code command to clipboard
  const handleCopyCode = () => {
    navigator.clipboard.writeText('python gui.py');
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  // Run scanner scan API
  const handleStartScan = async (e) => {
    e.preventDefault();
    if (!target.trim()) {
      setErrorMsg("Please provide a target IP or domain.");
      return;
    }
    
    setIsScanning(true);
    setResults(null);
    setErrorMsg(null);
    setProgress(5);
    setLogs([]);

    if (demoMode) {
      runSimulatedScan();
      return;
    }

    addLog(`[*] Initializing scan for: ${target}`, 'info');
    addLog(`[*] Options: threads=${threads}, timeout=${timeout}s, skip_ping=${skipPing}`, 'info');
    
    // Virtual animation while waiting for backend API
    let progressTimer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 85) {
          clearInterval(progressTimer);
          return 85;
        }
        return prev + Math.floor(Math.random() * 10) + 2;
      });
    }, 400);

    addLog(`[*] Directing API connection to serverless backend...`, 'info');

    try {
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          target: target.trim(),
          use_common: scanType === 'common',
          start_port: startPort,
          end_port: endPort,
          threads: threads,
          timeout: timeout,
          skip_ping: skipPing
        }),
      });

      clearInterval(progressTimer);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || `Server responded with status ${response.status}`);
      }

      const scanResult = await response.json();
      setProgress(100);
      addLog(`[+] API response successfully received. Parsing details...`, 'success');

      if (scanResult.open_ports && scanResult.open_ports.length > 0) {
        scanResult.open_ports.forEach(p => {
          addLog(`[+] Port ${p.port} is OPEN | Service: ${p.service} | Banner: ${p.banner}`, 'success');
        });
      } else {
        addLog(`[-] No open ports discovered in selected port range.`, 'warning');
      }

      addLog(`[+] Port scan complete. Total time: ${scanResult.scan_time.toFixed(2)} seconds.`, 'success');
      setResults(scanResult);
    } catch (err) {
      clearInterval(progressTimer);
      addLog(`[-] Scanning failed: ${err.message}`, 'error');
      setErrorMsg(err.message);
    } finally {
      setIsScanning(false);
    }
  };

  // Download Reports
  const downloadJSON = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan_report_${results.target}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadCSV = () => {
    if (!results) return;
    let csvContent = "Port,Service,Banner\n";
    results.open_ports.forEach(p => {
      csvContent += `${p.port},"${p.service.replace(/"/g, '""')}","${p.banner.replace(/"/g, '""')}"\n`;
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan_report_${results.target}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadHTML = () => {
    if (!results) return;
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>PortScan Pro Report: ${results.target}</title>
  <style>
    body { font-family: 'Outfit', sans-serif; background: #060913; color: #f1f5f9; padding: 40px; margin: 0; }
    .container { max-width: 800px; margin: 0 auto; background: #0c1224; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    h2 { margin-top: 0; border-bottom: 2px solid #00f2fe; padding-bottom: 10px; color: #fff; display: flex; align-items: center; gap: 10px; }
    .meta-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 25px; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
    .meta-item { font-size: 0.9rem; color: #94a3b8; }
    .meta-item strong { color: #00f2fe; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th { background: rgba(0,0,0,0.4); padding: 12px; font-weight: 600; font-size: 0.8rem; text-transform: uppercase; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.07); }
    td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem; }
    .port { color: #00f2fe; font-family: monospace; font-weight: bold; }
    .banner { font-family: monospace; color: #94a3b8; }
    .status { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
    .footer { text-align: center; margin-top: 30px; font-size: 0.8rem; color: #64748b; }
  </style>
</head>
<body>
  <div class="container">
    <h2>🛡️ PortScan Pro Audit Report</h2>
    <div class="meta-box">
      <div class="meta-item">Target Host: <strong>${results.target}</strong></div>
      <div class="meta-item">IP Address: <strong>${results.target_ip}</strong></div>
      <div class="meta-item">Time Elapsed: <strong>${results.scan_time.toFixed(2)}s</strong></div>
      <div class="meta-item">Ports Open: <strong>${results.open_ports.length}</strong></div>
    </div>
    <table>
      <thead>
        <tr>
          <th>Port</th>
          <th>Service</th>
          <th>Status</th>
          <th>Banner / Info</th>
        </tr>
      </thead>
      <tbody>
        ${results.open_ports.map(p => `
          <tr>
            <td class="port">${p.port}</td>
            <td>${p.service}</td>
            <td><span class="status">OPEN</span></td>
            <td class="banner">${p.banner}</td>
          </tr>
        `).join('')}
        ${results.open_ports.length === 0 ? `<tr><td colspan="4" style="text-align: center; color: #64748b; padding: 20px;">No open ports identified.</td></tr>` : ''}
      </tbody>
    </table>
    <div class="footer">
      Generated by PortScan Pro Web Client &middot; Powered by Vercel
    </div>
  </div>
</body>
</html>
    `;
    const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan_report_${results.target}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-container">
      {/* Upper Header */}
      <header className="header">
        <div className="logo-section">
          <div className="logo-icon">
            <Shield size={24} color="#060913" />
          </div>
          <div className="logo-text">
            <h1>PortScan Pro <span style={{ fontSize: '0.9rem', color: 'var(--accent-cyan)' }}>v2.0</span></h1>
            <div className="logo-subtitle">Advanced Network Security Auditor</div>
          </div>
        </div>
        <div className="badge-vercel">
          <svg width="12" height="12" viewBox="0 0 116 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M57.5 0L115 100H0L57.5 0Z" fill="white"/>
          </svg>
          <span>Vercel Certified Deployment</span>
        </div>
      </header>

      {/* Main Grid: Settings sidebar & display area */}
      <main className="dashboard-grid">
        {/* Settings Card */}
        <section className="card">
          <h2 className="card-title">
            <Sliders size={18} />
            Scanner Configuration
          </h2>
          
          <form onSubmit={handleStartScan}>
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <label className="form-label" htmlFor="target-input">Target IP / Domain</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Demo Mode</span>
                  <label className="switch">
                    <input 
                      type="checkbox" 
                      checked={demoMode} 
                      onChange={(e) => setDemoMode(e.target.checked)} 
                    />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
              <div className="form-input-container">
                <input 
                  id="target-input"
                  type="text" 
                  className="form-input" 
                  placeholder="e.g. scanme.nmap.org" 
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  disabled={isScanning}
                />
              </div>
            </div>

            {/* Scan type switch */}
            <div className="scan-type-buttons">
              <button 
                type="button"
                className={`btn-tab ${scanType === 'common' ? 'active' : ''}`}
                onClick={() => setScanType('common')}
                disabled={isScanning}
              >
                Common Ports (12)
              </button>
              <button 
                type="button"
                className={`btn-tab ${scanType === 'custom' ? 'active' : ''}`}
                onClick={() => setScanType('custom')}
                disabled={isScanning}
              >
                Custom Range
              </button>
            </div>

            {/* Custom port range selection */}
            {scanType === 'custom' && (
              <div className="form-group form-row">
                <div>
                  <label className="form-label" htmlFor="start-port-input">Start Port</label>
                  <input 
                    id="start-port-input"
                    type="number" 
                    className="form-input" 
                    min="1" 
                    max="65535"
                    value={startPort}
                    onChange={(e) => setStartPort(parseInt(e.target.value) || 1)}
                    disabled={isScanning}
                  />
                </div>
                <div>
                  <label className="form-label" htmlFor="end-port-input">End Port</label>
                  <input 
                    id="end-port-input"
                    type="number" 
                    className="form-input" 
                    min="1" 
                    max="65535"
                    value={endPort}
                    onChange={(e) => setEndPort(parseInt(e.target.value) || 1024)}
                    disabled={isScanning}
                  />
                </div>
              </div>
            )}

            {/* Threads adjustment */}
            <div className="slider-container">
              <div className="slider-header">
                <span className="form-label">Thread Capacity</span>
                <span className="slider-value">{threads} Worker Threads</span>
              </div>
              <input 
                type="range" 
                className="range-slider"
                min="10" 
                max="100" 
                step="5"
                value={threads}
                onChange={(e) => setThreads(parseInt(e.target.value))}
                disabled={isScanning}
              />
            </div>

            {/* Timeout settings */}
            <div className="form-group">
              <label className="form-label" htmlFor="timeout-input">Socket Timeout (Seconds)</label>
              <input 
                id="timeout-input"
                type="number" 
                step="0.1" 
                min="0.1" 
                max="3" 
                className="form-input"
                value={timeout}
                onChange={(e) => setTimeoutVal(parseFloat(e.target.value) || 0.5)}
                disabled={isScanning}
              />
            </div>

            {/* Skip ping checkbox */}
            <div className="switch-container">
              <span className="switch-label">Bypass Ping Discovery</span>
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={skipPing} 
                  onChange={(e) => setSkipPing(e.target.checked)}
                  disabled={isScanning}
                />
                <span className="slider"></span>
              </label>
            </div>
            
            {scanType === 'custom' && (endPort - startPort + 1) > 150 && !demoMode && (
              <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)', padding: '0.75rem', borderRadius: '8px' }}>
                <AlertCircle size={20} color="var(--accent-yellow)" style={{ flexShrink: 0 }} />
                <p style={{ fontSize: '0.75rem', color: 'var(--accent-yellow)', lineHeight: '1.4' }}>
                  Web scanning is constrained to a maximum of 150 ports. Adjust range or use <strong>Demo Mode</strong>.
                </p>
              </div>
            )}

            <button 
              type="submit" 
              className="btn-action" 
              disabled={isScanning || (scanType === 'custom' && (endPort - startPort + 1) > 150 && !demoMode)}
            >
              <Play size={16} fill="currentColor" />
              {isScanning ? 'Scan in Progress...' : 'Start Audit Scan'}
            </button>
          </form>
        </section>

        {/* Console / Display Panel */}
        <section style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Metrics Dashboard */}
          <div className="metrics-row">
            <div className="metric-card">
              <Activity className="metric-icon" />
              <div className="metric-value" style={{ color: results ? 'var(--accent-cyan)' : 'inherit' }}>
                {results ? results.open_ports.length : '0'}
              </div>
              <div className="metric-label">Open Ports</div>
            </div>
            
            <div className="metric-card">
              <Cpu className="metric-icon" />
              <div className="metric-value">
                {results ? results.total_scanned : '0'}
              </div>
              <div className="metric-label font-mono">Ports Checked</div>
            </div>

            <div className="metric-card">
              <Clock className="metric-icon" />
              <div className="metric-value">
                {results ? `${results.scan_time.toFixed(2)}s` : '0.00s'}
              </div>
              <div className="metric-label">Duration</div>
            </div>

            <div className="metric-card">
              <Shield className="metric-icon" style={{ color: results ? 'var(--accent-green)' : 'inherit' }} />
              <div className="metric-value" style={{ fontSize: '0.9rem', color: isScanning ? 'var(--accent-cyan)' : (results ? 'var(--accent-green)' : 'var(--text-muted)') }}>
                {isScanning ? 'SCANNING' : (results ? 'COMPLETE' : 'STANDBY')}
              </div>
              <div className="metric-label">Audit Status</div>
            </div>
          </div>

          {/* Terminal Console */}
          <div className="terminal-window">
            <div className="terminal-header">
              <div className="terminal-controls">
                <div className="terminal-dot red"></div>
                <div className="terminal-dot yellow"></div>
                <div className="terminal-dot green"></div>
              </div>
              <div className="terminal-title">
                <Terminal size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                Log Terminal output
              </div>
              <div style={{ width: '40px' }}></div>
            </div>
            
            <div className="terminal-body">
              {logs.length === 0 ? (
                <div className="terminal-line muted">
                  SYSTEM READY. Enter details and press "Start Audit Scan" to initialize socket auditing.
                  <span className="terminal-cursor"></span>
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className={`terminal-line ${log.type}`}>
                    <span className="terminal-line-time" style={{ color: 'var(--text-muted)', marginRight: '8px' }}>[{log.time}]</span>
                    {log.text}
                    {index === logs.length - 1 && isScanning && <span className="terminal-cursor"></span>}
                  </div>
                ))
              )}
              <div ref={terminalEndRef} />
            </div>

            {/* Progress line */}
            {isScanning && (
              <div className="progress-container">
                <div className="progress-header">
                  <span>Auditing socket connections...</span>
                  <span>{progress}%</span>
                </div>
                <div className="progress-bar-bg">
                  <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
                </div>
              </div>
            )}
          </div>

          {/* Data Report Grid */}
          <div className="card" style={{ flex: 1 }}>
            <div className="results-header">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                <CheckCircle size={18} color="var(--accent-green)" />
                Detected Open Sockets
              </h3>
              
              <div className="export-actions">
                <button 
                  className="btn-export" 
                  onClick={downloadJSON} 
                  disabled={!results || results.open_ports.length === 0}
                >
                  <Download size={14} /> JSON
                </button>
                <button 
                  className="btn-export" 
                  onClick={downloadCSV} 
                  disabled={!results || results.open_ports.length === 0}
                >
                  <Download size={14} /> CSV
                </button>
                <button 
                  className="btn-export" 
                  onClick={downloadHTML} 
                  disabled={!results || results.open_ports.length === 0}
                >
                  <Download size={14} /> HTML Report
                </button>
              </div>
            </div>

            {errorMsg && (
              <div style={{ display: 'flex', gap: '0.75rem', background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.2)', padding: '1rem', borderRadius: '8px', marginBottom: '1.25rem' }}>
                <AlertCircle size={20} color="var(--accent-red)" style={{ flexShrink: 0 }} />
                <div>
                  <h4 style={{ fontSize: '0.9rem', color: '#fff', marginBottom: '0.15rem' }}>Scan Error</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{errorMsg}</p>
                </div>
              </div>
            )}

            <div className="results-table-container">
              {results && results.open_ports.length > 0 ? (
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Port</th>
                      <th>Service Name</th>
                      <th>Connection Status</th>
                      <th>Banner Grab Info</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.open_ports.map((p, idx) => (
                      <tr key={idx}>
                        <td className="mono port-cell">{p.port}</td>
                        <td style={{ fontWeight: '500' }}>{p.service}</td>
                        <td>
                          <span className="badge-status open">
                            <span className="status-dot"></span>
                            Open
                          </span>
                        </td>
                        <td className="mono banner-cell" title={p.banner}>{p.banner}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-results">
                  <HelpCircle size={36} color="var(--text-muted)" style={{ margin: '0 auto 0.75rem auto', display: 'block' }} />
                  {results ? (
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                      No active services detected on scanned ports.
                    </p>
                  ) : (
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                      Configure targets and initiate a scan to gather diagnostic results.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
          
          {/* Desktop Banner / Guide */}
          <div className="desktop-banner">
            <div className="desktop-banner-content">
              <h4 className="desktop-banner-title">
                <Laptop size={16} />
                Need Unlimited High-Speed Scanning?
              </h4>
              <p className="desktop-banner-desc">
                The web console is perfect for lightweight common scans. For heavy-duty operations (up to 65k ports, multithreading, bypass security restrictions), run our desktop Tkinter app locally.
              </p>
              <div className="desktop-code-box">
                <span>python gui.py</span>
                <button 
                  className="btn-icon-only" 
                  onClick={handleCopyCode} 
                  title="Copy command"
                >
                  {copiedCode ? <Check size={14} color="var(--accent-green)" /> : <Copy size={14} />}
                </button>
              </div>
            </div>
            <div style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--accent-cyan)', marginBottom: '0.35rem' }}>
                <Sparkles size={12} />
                <span>Zero Installation</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '180px', lineHeight: '1.3' }}>
                Uses native python modules. No pip installs needed.
              </p>
            </div>
          </div>

        </section>
      </main>
    </div>
  );
}
