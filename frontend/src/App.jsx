import React, { useState, useEffect } from 'react';
import {
  Shield, Lock, Download, AlertCircle, CheckCircle,
  Activity, Globe, Server, FileText, LayoutDashboard,
  LogOut, User, Mail, Loader2, ArrowLeft, History, ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { generateAudit } from './api';
import { supabase } from './supabaseClient';

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Auth State
  const [session, setSession] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  // Navigation State
  const [view, setView] = useState('home'); // 'home' or 'dashboard'
  const [userScans, setUserScans] = useState([]);
  const [scansLoading, setScansLoading] = useState(false);

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
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

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

  useEffect(() => {
    if (view === 'dashboard' && session) {
      fetchUserScans();
    }
  }, [view, session]);

  const fetchUserScans = async () => {
    setScansLoading(true);
    const { data, error } = await supabase
      .from('scans')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching scans:', error);
    } else {
      setUserScans(data || []);
    }
    setScansLoading(false);
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setError('');

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email: authEmail,
          password: authPassword,
        });
        if (error) throw error;
        alert('Check your email for the confirmation link!');
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email: authEmail,
          password: authPassword,
        });
        if (error) throw error;
      }
      setShowAuth(false);
      setAuthPassword('');
    } catch (err) {
      setError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setView('home');
  };

  const handleScan = async (e) => {
    e.preventDefault();
    if (!url) {
      setError("Please enter a valid URL");
      return;
    }

    try {
      new URL(url.startsWith('http') ? url : `https://${url}`);
    } catch (_) {
      setError("Please enter a valid URL (e.g., example.com)");
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess(false);

    try {
      const token = session?.access_token;
      const blob = await generateAudit(url, token);

      // trigger download
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      const hostname = url.replace(/^(?:https?:\/\/)?(?:www\.)?/i, "").split('/')[0];
      const filename = `Audit_Report_${hostname}.pdf`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);

      setSuccess(true);
      if (session) fetchUserScans(); // Refresh dashboard data
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden bg-[#0A0F1C] text-white">
      {/* Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600 opacity-10 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-500 opacity-10 blur-[120px] rounded-full"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-[0.03]"></div>
      </div>

      {/* Navbar */}
      <header className="absolute top-0 left-0 w-full p-6 z-30 flex justify-between items-center">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => setView('home')}>
          <Shield className="w-8 h-8 text-cyan-400" />
          <span className="text-xl font-bold tracking-wider">CYBER<span className="text-cyan-400">SECURE</span> INDIA</span>
        </div>

        <div className="flex items-center gap-4">
          {session ? (
            <div className="flex items-center gap-3">
              <button
                onClick={() => setView(view === 'dashboard' ? 'home' : 'dashboard')}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800/50 border border-slate-700 hover:bg-slate-700 transition"
              >
                {view === 'dashboard' ? <Globe className="w-4 h-4" /> : <LayoutDashboard className="w-4 h-4" />}
                <span className="hidden md:inline">{view === 'dashboard' ? 'Home' : 'Dashboard'}</span>
              </button>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-900/20 border border-red-900/50 hover:bg-red-900/40 text-red-400 transition"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden md:inline">Sign Out</span>
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowAuth(true)}
              className="flex items-center gap-2 px-6 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-600 text-white font-semibold transition shadow-lg shadow-cyan-500/20"
            >
              <User className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </header>

      <main className="z-10 w-full max-w-5xl pt-20">
        <AnimatePresence mode="wait">
          {view === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center text-center space-y-12"
            >
              {/* Hero Section */}
              <div className="space-y-6 max-w-3xl">
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono mb-4 tracking-widest uppercase">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                  System Online & Ready
                </div>
                <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyan-400 pb-2">
                  Enterprise-Grade <br /> Security Audit
                </h1>
                <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto">
                  Identify vulnerabilities instantly. Log in to unlock full remediation guides and detailed impact analysis.
                </p>
              </div>

              {/* Input Form */}
              <div className="w-full max-w-2xl relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-cyan-400 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                <form onSubmit={handleScan} className="relative bg-[#0F172A] border border-slate-700 rounded-xl p-2 flex flex-col md:flex-row gap-2 shadow-2xl">
                  <div className="relative flex-grow flex items-center">
                    <Globe className="absolute left-4 text-slate-500 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Enter website URL (e.g. google.com)"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      disabled={isLoading}
                      className="w-full bg-transparent text-white placeholder-slate-500 px-12 py-4 rounded-lg focus:outline-none font-mono text-lg"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-4 px-8 rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 min-w-[200px]"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Scanning...</span>
                      </>
                    ) : (
                      <>
                        <Activity className="w-5 h-5" />
                        <span>Run {session ? 'Premium' : 'Free'} Scan</span>
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Status Indicators */}
              <div className="h-32 w-full flex items-center justify-center">
                <AnimatePresence mode="wait">
                  {isLoading && (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="flex flex-col items-center gap-4"
                    >
                      <div className="w-64 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.5)]"
                          initial={{ width: "0%" }}
                          animate={{ width: "100%" }}
                          transition={{ duration: 15, ease: "linear", repeat: Infinity }}
                        />
                      </div>
                      <p className="text-cyan-400 font-mono text-xs tracking-[0.3em] uppercase animate-pulse">
                        {loadingMessages[loadingStep]}
                      </p>
                    </motion.div>
                  )}

                  {error && !isLoading && (
                    <motion.div
                      key="error"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex items-center gap-3 text-red-400 bg-red-950/20 border border-red-900/30 px-6 py-3 rounded-lg"
                    >
                      <AlertCircle className="w-5 h-5" />
                      <span className="text-sm font-medium">{error}</span>
                    </motion.div>
                  )}

                  {success && !isLoading && (
                    <motion.div
                      key="success"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex flex-col items-center gap-3"
                    >
                      <div className="flex items-center gap-3 text-emerald-400 bg-emerald-950/20 border border-emerald-900/30 px-6 py-3 rounded-lg">
                        <CheckCircle className="w-5 h-5" />
                        <span className="text-sm font-semibold">{session ? 'Premium Report' : 'Free Assessment'} Downloaded!</span>
                      </div>
                      {!session && (
                        <p className="text-slate-500 text-xs">Login to unlock detailed fixes and vulnerability metrics.</p>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {view === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <div className="flex justify-between items-end border-b border-slate-800 pb-6">
                <div>
                  <h2 className="text-3xl font-bold text-white">Security Dashboard</h2>
                  <p className="text-slate-400 mt-1">Manage and review your organization's scan history.</p>
                </div>
                <button
                  onClick={() => setView('home')}
                  className="px-4 py-2 rounded-lg bg-cyan-500/10 text-cyan-400 text-sm font-semibold hover:bg-cyan-500/20 transition flex items-center gap-2"
                >
                  <ArrowLeft className="w-4 h-4" /> New Scan
                </button>
              </div>

              {scansLoading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                  <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
                  <p className="text-slate-500 font-mono text-sm tracking-widest uppercase">Loading Scan History...</p>
                </div>
              ) : userScans.length > 0 ? (
                <div className="grid grid-cols-1 gap-4">
                  {userScans.map((scan) => (
                    <div key={scan.id} className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-slate-700 transition group">
                      <div className="flex items-center gap-5">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center font-bold text-2xl ${scan.risk_score === 'A+' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' :
                            scan.risk_score === 'B' ? 'bg-orange-500/10 text-orange-500 border border-orange-500/20' :
                              'bg-red-500/10 text-red-500 border border-red-500/20'
                          }`}>
                          {scan.risk_score}
                        </div>
                        <div>
                          <h3 className="text-lg font-bold group-hover:text-cyan-400 transition">{scan.hostname}</h3>
                          <div className="flex items-center gap-4 mt-1">
                            <span className="text-xs text-slate-500 flex items-center gap-1">
                              <History className="w-3 h-3" /> {new Date(scan.created_at).toLocaleDateString()}
                            </span>
                            <span className="text-xs text-slate-500 flex items-center gap-1">
                              <AlertCircle className="w-3 h-3" /> {scan.issue_count} Issues Detected
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-sm hover:bg-slate-700 transition cursor-not-allowed opacity-50">
                          <ExternalLink className="w-4 h-4" /> View Online
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500 text-black text-sm font-bold hover:bg-cyan-400 transition shadow-lg shadow-cyan-500/10">
                          <Download className="w-4 h-4" /> Download PDF
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-20 bg-slate-900/30 border border-slate-800 border-dashed rounded-2xl">
                  <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-500">
                    <History className="w-8 h-8" />
                  </div>
                  <h3 className="text-xl font-bold text-white">No Scan History</h3>
                  <p className="text-slate-500 mt-2 max-w-sm mx-auto">You haven't performed any scans yet. Run your first audit to see the results here.</p>
                  <button
                    onClick={() => setView('home')}
                    className="mt-6 px-6 py-2 rounded-lg bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition"
                  >
                    Run Your First Scan
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Auth Modal */}
      <AnimatePresence>
        {showAuth && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowAuth(false)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl"
            >
              <div className="text-center space-y-2 mb-8">
                <div className="w-12 h-12 bg-cyan-500/10 rounded-xl flex items-center justify-center mx-auto text-cyan-400">
                  <Shield className="w-6 h-6" />
                </div>
                <h2 className="text-2xl font-bold">{isSignUp ? 'Create Account' : 'Welcome Back'}</h2>
                <p className="text-slate-400 text-sm">Access premium reports and scan history.</p>
              </div>

              <form onSubmit={handleAuth} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-mono text-slate-500 uppercase tracking-widest pl-1">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      type="email"
                      required
                      value={authEmail}
                      onChange={(e) => setAuthEmail(e.target.value)}
                      placeholder="name@company.com"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 focus:outline-none focus:border-cyan-500/50 transition"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-mono text-slate-500 uppercase tracking-widest pl-1">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                    <input
                      type="password"
                      required
                      value={authPassword}
                      onChange={(e) => setAuthPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-12 pr-4 focus:outline-none focus:border-cyan-500/50 transition"
                    />
                  </div>
                </div>

                {error && (
                  <div className="text-red-400 text-xs py-2 text-center bg-red-950/20 border border-red-900/30 rounded-lg">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={authLoading}
                  className="w-full bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-3 rounded-xl shadow-lg shadow-cyan-500/10 transition flex items-center justify-center gap-2"
                >
                  {authLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : isSignUp ? 'Sign Up' : 'Sign In'}
                </button>
              </form>

              <div className="mt-6 text-center text-sm">
                <button
                  onClick={() => setIsSignUp(!isSignUp)}
                  className="text-slate-400 hover:text-cyan-400 transition"
                >
                  {isSignUp ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <footer className="absolute bottom-6 w-full text-center text-slate-600 text-[10px] font-mono tracking-widest uppercase">
        <p>© 2026 CYBERSECURE INDIA. ENTERPRISE VULNERABILITY MANAGEMENT.</p>
      </footer>
    </div>
  );
}

export default App;
