import React, { useState, useEffect } from 'react';
import { Shield, Lock, Download, AlertCircle, CheckCircle, Activity, Globe, Server, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { generateAudit } from './api';

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const loadingMessages = [
    "Initializing CyberSecure Scanner...",
    "Resolving Hostname...",
    "Scanning Open Ports...",
    "Analyzing SSL/TLS Handshake...",
    "Checking HTTP Headers...",
    "Running Vulnerability Heuristics...",
    "Compiling Audit Report..."
  ];

  useEffect(() => {
    let interval;
    if (isLoading) {
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev + 1) % loadingMessages.length);
      }, 2500);
    } else {
      setLoadingStep(0);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleScan = async (e) => {
    e.preventDefault();
    if (!url) {
      setError("Please enter a valid URL");
      return;
    }

    try {
      new URL(url);
    } catch (_) {
      setError("Please enter a valid URL (e.g., https://example.com)");
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess(false);

    try {
      const blob = await generateAudit(url);

      // trigger download
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      const filename = `Audit_Report_${new URL(url).hostname}.pdf`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);

      setSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyber-blue opacity-20 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyber-accent opacity-10 blur-[120px] rounded-full"></div>
      </div>

      <header className="absolute top-6 left-6 z-20 flex items-center gap-2">
        <Shield className="w-8 h-8 text-cyber-accent" />
        <span className="text-xl font-bold tracking-wider text-white">CYBER<span className="text-cyber-accent">SECURE</span> INDIA</span>
      </header>

      <main className="z-10 w-full max-w-3xl flex flex-col items-center text-center space-y-12">

        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-6"
        >
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-cyber-blue/20 border border-cyber-blue/40 text-cyber-accent text-sm font-mono mb-4">
            <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            System Online & Ready
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyber-accent pb-2">
            Enterprise-Grade <br /> Security Audit
          </h1>
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto">
            Identify vulnerabilities instantly. Generates comprehensive PDF reports for compliance and safety analysis.
          </p>
        </motion.div>

        {/* Input Form */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="w-full relative group"
        >
          <div className="absolute -inset-0.5 bg-gradient-to-r from-cyber-blue to-cyber-accent rounded-xl blur opacity-30 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
          <form onSubmit={handleScan} className="relative bg-cyber-darker border border-slate-700/50 rounded-xl p-2 flex flex-col md:flex-row gap-2 shadow-2xl">
            <div className="relative flex-grow flex items-center">
              <Globe className="absolute left-4 text-slate-500 w-5 h-5" />
              <input
                type="text"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
                className="w-full bg-transparent text-white placeholder-slate-500 px-12 py-4 rounded-lg focus:outline-none focus:ring-1 focus:ring-cyber-accent/50 font-mono text-lg"
              />
            </div>
            <button
              type="button" // Use type="submit" for the form, but let's be explicit
              onClick={handleScan}
              disabled={isLoading}
              className="bg-cyber-blue hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed min-w-[160px]"
            >
              {isLoading ? (
                <>
                  <Activity className="w-5 h-5 animate-spin" />
                  <span>Generating Free Assessment...</span>

                </>
              ) : (
                <>
                  <Lock className="w-5 h-5" />
                  <span>Run Scan</span>
                </>
              )}
            </button>
          </form>
        </motion.div>

        {/* Status Indicators */}
        <div className="h-24 w-full flex items-center justify-center">
          <AnimatePresence mode="wait">
            {isLoading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col items-center gap-3"
              >
                <div className="w-64 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-cyber-accent"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 15, ease: "linear", repeat: Infinity }} // Indeterminate progress simulation
                  />
                </div>
                <p className="text-cyber-accent font-mono text-sm tracking-widest uppercase animate-pulse">
                  {loadingMessages[loadingStep]}
                </p>
              </motion.div>
            )}

            {error && !isLoading && (
              <motion.div
                key="error"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center gap-3 text-red-400 bg-red-900/20 border border-red-900/50 px-6 py-3 rounded-lg"
              >
                <AlertCircle className="w-6 h-6" />
                <span>{error}</span>
              </motion.div>
            )}

            {success && !isLoading && (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex flex-col items-center gap-2"
              >
                <div className="flex items-center gap-3 text-emerald-400 bg-emerald-900/20 border border-emerald-900/50 px-6 py-3 rounded-lg border-l-4 border-l-emerald-500">
                  <CheckCircle className="w-6 h-6" />
                  <span className="font-semibold">Audit Complete! Report Downloaded.</span>
                </div>
                <p className="text-slate-500 text-sm mt-2">Check your downloads folder for the PDF.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </main>

      <footer className="absolute bottom-6 w-full text-center text-slate-600 text-xs font-mono">
        <p>© 2026 CYBERSECURE INDIA SCANNER. SECURED BY DEFAULT.</p>
      </footer>
    </div>
  );
}

export default App;
