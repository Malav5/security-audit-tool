import React, { useState, useEffect } from 'react';
import {
  Shield, Lock, Download, AlertCircle, CheckCircle,
  Activity, Globe, Server, FileText, LayoutDashboard,
  LogOut, User, Mail, Loader2, ArrowLeft, History, ExternalLink, Trash2, Clock, Crown, X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { generateAudit, downloadPDF, deleteScan, toggleAutomation, getSubscription, upgradeSubscription, cancelSubscription, createRazorpayOrder, verifyRazorpayPayment } from './api';
import { supabase } from './supabaseClient';
import PricingPage from './PricingPage';

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [revealedFixes, setRevealedFixes] = useState({});
  const [automatedHosts, setAutomatedHosts] = useState({});
  const [automationLoading, setAutomationLoading] = useState(false);

  // Auth State
  const [session, setSession] = useState(null);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [showAuth, setShowAuth] = useState(false);

  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);

  // Navigation State
  const [view, setView] = useState('home'); // 'home' or 'dashboard'
  const [userScans, setUserScans] = useState([]);
  const [scansLoading, setScansLoading] = useState(false);

  // Subscription State
  const [subscription, setSubscription] = useState(null);
  const [showPricing, setShowPricing] = useState(false);

  const loadingMessages = [
    "Initializing CyberSecure Enterprise Scanner...",
    "Scanning Attack Surface (Subdomains)...",
    "Resolving Hostname Heuristics...",
    "Scanning Critical Infrastructure Ports...",
    "Analyzing SSL/TLS Handshake Integrity...",
    "Checking Enterprise HTTP Security Headers...",
    "Mapping Vulnerabilities to GDPR/SOC2 Compliance...",
    "Generating Premium Remediation Guide..."
  ];

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setIsInitialLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setIsInitialLoading(false);
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

  // Fetch subscription when user logs in
  useEffect(() => {
    if (session) {
      fetchSubscription();
    }
  }, [session]);

  const fetchSubscription = async () => {
    try {
      const subData = await getSubscription(session.access_token);
      setSubscription(subData);
    } catch (err) {
      console.error('Error fetching subscription:', err);
    }
  };

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
          options: {
            emailRedirectTo: window.location.origin,
          }
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
    setScanResults(null);
    setRevealedFixes({});

    try {
      const token = session?.access_token;
      const data = await generateAudit(url, token);

      setScanResults(data);
      setSuccess(true);
      setView('results');
      if (session) fetchUserScans();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewHistoryScan = (scan) => {
    setScanResults({
      hostname: scan.hostname,
      grade: scan.risk_score,
      issues: scan.findings || [], // Load the saved findings
      pdf_filename: scan.pdf_url
    });
    setRevealedFixes({});
    setView('results');
  };

  const handleDownloadReport = async (filename) => {
    if (!session) {
      setShowAuth(true);
      return;
    }

    try {
      const blob = await downloadPDF(filename, session.access_token);
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      alert(err.message);
    }
  };

  const toggleFix = (index) => {
    setRevealedFixes(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const handleDeleteScan = async (e, scanId) => {
    e.stopPropagation(); // Don't open the report when clicking delete

    if (!window.confirm("Are you sure you want to delete this scan record?")) return;

    try {
      await deleteScan(scanId, session.access_token);
      // Update local state to remove the scan
      setUserScans(prev => prev.filter(s => s.id !== scanId));
    } catch (err) {
      alert(err.message);
    }
  };

  const handleToggleAutomation = async (e, hostname) => {
    e.stopPropagation();
    if (!session) {
      setShowAuth(true);
      return;
    }

    const currentState = automatedHosts[hostname] || false;
    const newState = !currentState;

    setAutomationLoading(true);
    try {
      await toggleAutomation(hostname, newState, session.access_token);
      setAutomatedHosts(prev => ({ ...prev, [hostname]: newState }));
    } catch (err) {
      alert(err.message + ". Make sure your local backend is running!");
    } finally {
      setAutomationLoading(false);
    }
  };

  const loadRazorpayScript = () => {
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const handleUpgrade = async (tier) => {
    if (!session) {
      setShowAuth(true);
      return;
    }

    if (tier === 'enterprise') {
      // Open contact sales email
      window.open('mailto:sales@cybersecure.com?subject=Enterprise Plan Inquiry', '_blank');
      setShowPricing(false);
      return;
    }

    try {
      if (tier === 'free') return;

      const res = await loadRazorpayScript();
      if (!res) {
        alert('Razorpay SDK failed to load. Are you online?');
        return;
      }

      // 1. Map tier to price (in Paise for Razorpay)
      const priceMap = {
        'basic': 2900,         // ₹29.00 -> 2900 paise
        'professional': 9900,  // ₹99.00 -> 9900 paise
        'enterprise': 29900    // ₹299.00 -> 29900 paise
      };

      const amount = priceMap[tier];

      // 2. Create order on backend
      const order = await createRazorpayOrder(amount, session.access_token);

      // 3. Open Razorpay Checkout
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || '', // We'll need to add this to .env
        amount: order.amount,
        currency: order.currency,
        name: "CyberSecure India",
        description: `Upgrade to ${tier.charAt(0).toUpperCase() + tier.slice(1)} Plan`,
        image: "https://kctecmuwsnshbdzrxfxy.supabase.co/storage/v1/object/public/assets/logo.png",
        order_id: order.id,
        handler: async function (response) {
          // 4. Verify payment on backend
          try {
            setIsLoading(true);
            await verifyRazorpayPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              tier: tier
            }, session.access_token);

            await fetchSubscription();
            setShowPricing(false);
            alert("Welcome to Premium! Your account has been upgraded.");
          } catch (err) {
            alert("Payment verification failed: " + err.message);
          } finally {
            setIsLoading(false);
          }
        },
        prefill: {
          email: session.user.email,
        },
        theme: {
          color: "#06b6d4",
        },
      };

      const paymentObject = new window.Razorpay(options);
      paymentObject.open();

    } catch (err) {
      alert(err.message);
    }
  };

  const handleCancelSubscription = async () => {
    if (!session) return;
    if (!window.confirm("Are you sure you want to cancel your subscription? You will retain access until the end of your billing cycle.")) return;

    try {
      await cancelSubscription(session.access_token);
      await fetchSubscription(); // Refresh data to show cancellation status
      alert("Your subscription has been scheduled for cancellation.");
    } catch (err) {
      alert(err.message);
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
          {!isInitialLoading && (
            session ? (
              <div className="flex items-center gap-3">
                {/* Subscription & Pricing Button - Disabled for LinkedIn Demo */}
                {/* {subscription && (
                  <button
                    onClick={() => setShowPricing(true)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all active:scale-95 ${subscription.tier === 'free'
                      ? "bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold hover:shadow-lg hover:shadow-cyan-500/20"
                      : "bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-semibold hover:bg-cyan-500/20"
                      }`}
                  >
                    <Crown className="w-4 h-4" />
                    <span className="hidden md:inline">
                      {subscription.tier === 'free' ? 'Upgrade' : 'Manage Plan'}
                    </span>
                  </button>
                )} */}

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
            )
          )}
        </div>

      </header>

      <main className="z-10 w-full max-w-7xl pt-20 px-4 md:px-12">
        <AnimatePresence mode="wait">
          {view === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center space-y-16"
            >
              {/* Hero Section - Split Layout for Width */}
              <div className="flex flex-col lg:flex-row items-center gap-12 text-center lg:text-left w-full">
                <div className="space-y-8 flex-[1.2]">
                  <div className="inline-flex items-center px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono tracking-widest uppercase">
                    <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                    Global Security Nodes Online
                  </div>
                  <h1 className="text-5xl md:text-8xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyan-400 pb-2 leading-[1.1]">
                    Enterprise <br /> Compliance <br /> Intelligence
                  </h1>
                  <p className="text-xl md:text-2xl text-slate-400 max-w-2xl">
                    Automated vulnerability discovery mapped to <span className="text-cyan-400 font-semibold">GDPR, SOC2, and ISO 27001</span>.
                    Monitor your global attack surface in real-time.
                  </p>

                  {/* Enhanced Input Form */}
                  <div className="w-full relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-cyan-400 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                    <form onSubmit={handleScan} className="relative bg-[#0F172A] border border-slate-700 rounded-xl p-2 flex flex-col sm:flex-row gap-2 shadow-2xl">
                      <div className="relative flex-grow flex items-center">
                        <Globe className="absolute left-4 text-slate-500 w-5 h-5" />
                        <input
                          type="text"
                          placeholder="Target domain (e.g. cloudflare.com)"
                          value={url}
                          onChange={(e) => setUrl(e.target.value)}
                          disabled={isLoading}
                          className="w-full bg-transparent text-white placeholder-slate-500 px-12 py-4 rounded-lg focus:outline-none font-mono text-lg"
                        />
                      </div>
                      <button
                        type="submit"
                        disabled={isLoading}
                        className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-4 px-10 rounded-lg shadow-lg flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50 text-lg"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Scanning...</span>
                          </>
                        ) : (
                          <>
                            <Activity className="w-5 h-5" />
                            <span>Run Enterprise Audit</span>
                          </>
                        )}
                      </button>
                    </form>
                  </div>
                </div>

                {/* Side feature grid */}
                <div className="hidden lg:grid grid-cols-2 gap-6 flex-1">
                  {[
                    { icon: Shield, title: "Compliance", desc: "Automated GDPR/SOC2 Mapping" },
                    { icon: Server, title: "Discovery", desc: "Deep Subdomain Enumeration" },
                    { icon: Lock, title: "Privacy", desc: "HSTS & SSL Integrity Audit" },
                    { icon: FileText, title: "Remediation", desc: "Nginx/Apache Hotfix Scripts" },
                    { icon: Activity, title: "Real-time", desc: "Live Vulnerability Heuristics" },
                    { icon: ExternalLink, title: "Portal", desc: "Interactive Interactive Dashboard" }
                  ].map((feat, i) => (
                    <div key={i} className="bg-slate-900/40 border border-slate-800 p-8 rounded-3xl hover:border-cyan-500/30 transition-all hover:bg-slate-900/60 group cursor-default">
                      <feat.icon className="w-10 h-10 text-cyan-400 mb-4 group-hover:scale-110 transition-transform" />
                      <h3 className="font-bold text-lg text-white mb-2">{feat.title}</h3>
                      <p className="text-slate-500 text-sm leading-relaxed">{feat.desc}</p>
                    </div>
                  ))}
                </div>
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
                      <div className="w-80 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.6)]"
                          initial={{ width: "0%" }}
                          animate={{ width: "100%" }}
                          transition={{ duration: 15, ease: "linear", repeat: Infinity }}
                        />
                      </div>
                      <p className="text-cyan-400 font-mono text-sm tracking-[0.4em] uppercase animate-pulse">
                        {loadingMessages[loadingStep]}
                      </p>
                    </motion.div>
                  )}

                  {error && !isLoading && (
                    <motion.div
                      key="error"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex items-center gap-3 text-red-100 bg-red-500/10 border border-red-500/20 px-8 py-4 rounded-2xl"
                    >
                      <AlertCircle className="w-5 h-5 text-red-500" />
                      <span className="text-base font-medium">{error}</span>
                    </motion.div>
                  )}

                  {success && !isLoading && (
                    <motion.div
                      key="success"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex flex-col items-center gap-4"
                    >
                      <div className="flex items-center gap-3 text-emerald-100 bg-emerald-500/10 border border-emerald-500/20 px-8 py-4 rounded-2xl">
                        <CheckCircle className="w-5 h-5 text-emerald-500" />
                        <span className="text-base font-bold">Audit Complete. Results Available Below.</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {view === 'results' && scanResults && (
            <motion.div
              key="results"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full space-y-8"
            >
              {/* Results Header */}
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-slate-900/40 border border-slate-800 p-8 rounded-2xl backdrop-blur-md">
                <div className="flex items-center gap-6">
                  <div className={`w-20 h-20 rounded-2xl flex items-center justify-center text-4xl font-black shadow-2xl ${scanResults.grade === 'A' ? 'bg-emerald-500 text-black shadow-emerald-500/20' :
                    scanResults.grade === 'F' ? 'bg-red-500 text-white shadow-red-500/20' :
                      'bg-orange-500 text-black shadow-orange-500/20'
                    }`}>
                    {scanResults.grade}
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold">{scanResults.hostname}</h2>
                    <p className="text-slate-400 font-mono tracking-tighter uppercase text-sm mt-1">
                      Enterprise Compliance Score: {scanResults.grade === 'A' ? 'Excellent' : scanResults.grade === 'F' ? 'Critical Action Required' : 'Manual Review Recommended'}
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-4 w-full md:w-auto justify-start md:justify-end">
                  <button
                    onClick={(e) => handleToggleAutomation(e, scanResults.hostname)}
                    disabled={automationLoading}
                    className={`flex-grow md:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-xl border font-bold transition disabled:opacity-50 ${automatedHosts[scanResults.hostname]
                      ? 'bg-emerald-500/10 border-emerald-500 text-emerald-500'
                      : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
                      }`}
                  >
                    {automationLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Clock className={`w-5 h-5 ${automatedHosts[scanResults.hostname] ? 'animate-pulse' : ''}`} />
                    )}
                    {automationLoading ? 'Processing...' : automatedHosts[scanResults.hostname] ? '24hr Auto-Scan Active' : 'Enable 24hr Auto-Scan'}
                  </button>
                  <button
                    onClick={() => handleDownloadReport(scanResults.pdf_filename)}
                    className="flex-grow md:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition shadow-lg shadow-cyan-500/10"
                  >
                    <Download className="w-5 h-5" />
                    {session ? 'Download Full PDF' : 'Sign in to Download PDF'}
                  </button>
                  <button
                    onClick={() => setView('home')}
                    className="flex-grow md:flex-none flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-slate-800 text-white font-bold hover:bg-slate-700 transition"
                  >
                    <ArrowLeft className="w-5 h-5" />
                    New Scan
                  </button>
                </div>
              </div>

              {/* Findings grid */}
              <div className="grid grid-cols-1 gap-6">
                <div className="flex items-center justify-between px-2">
                  <h3 className="text-xl font-bold flex items-center gap-2">
                    <Activity className="w-5 h-5 text-cyan-400" />
                    Detailed Security Artifacts ({scanResults.issues.length})
                  </h3>
                  {!session && (
                    <div className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-3 py-1 rounded-full flex items-center gap-2">
                      <Lock className="w-3 h-3" /> Sample Results Visualization
                    </div>
                  )}
                </div>

                {scanResults.issues.map((issue, idx) => (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    key={idx}
                    className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden group"
                  >
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div className="space-y-1">
                          <h4 className="text-lg font-bold group-hover:text-cyan-400 transition">{issue.title}</h4>
                          {issue.compliance && (
                            <div className="flex gap-2">
                              {issue.compliance.map(tag => (
                                <span key={tag} className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase ${issue.severity === 'HIGH' ? 'bg-red-500/10 text-red-500 border border-red-500/20' :
                          issue.severity === 'MEDIUM' ? 'bg-orange-500/10 text-orange-500 border border-orange-500/20' :
                            'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                          }`}>
                          {issue.severity}
                        </span>
                      </div>

                      <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <label className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Threat Impact</label>
                          {session ? (
                            <p className="text-slate-300 text-sm leading-relaxed">{issue.impact}</p>
                          ) : (
                            <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-500 text-xs italic">
                              <Lock className="w-3 h-3" /> Sign in to analyze impact vector
                            </div>
                          )}
                        </div>
                        <div className="space-y-4">
                          <div className="space-y-2">
                            <label className="text-[10px] uppercase tracking-widest text-cyan-500 font-bold">Remediation Guide</label>
                            {session ? (
                              <p className="text-slate-300 text-sm">{issue.fix}</p>
                            ) : (
                              <div className="flex items-center gap-2 p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/10 text-cyan-500/50 text-xs italic">
                                <Lock className="w-3 h-3" /> Sign in for step-by-step fix
                              </div>
                            )}
                          </div>

                          {issue.code_snippet && (
                            <div className="space-y-3">
                              {session ? (
                                <>
                                  <button
                                    onClick={() => toggleFix(idx)}
                                    className="flex items-center gap-2 text-xs font-bold text-cyan-400 border border-cyan-400/20 bg-cyan-400/5 hover:bg-cyan-400/10 px-4 py-2 rounded-lg transition"
                                  >
                                    {revealedFixes[idx] ? 'Hide Hotfix' : 'Reveal Technical Hotfix'}
                                    <ExternalLink className="w-3 h-3" />
                                  </button>

                                  <AnimatePresence>
                                    {revealedFixes[idx] && (
                                      <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                      >
                                        <pre className="bg-black/40 border border-slate-800 rounded-xl p-4 text-[10px] font-mono text-cyan-100/80 leading-relaxed overflow-x-auto">
                                          {issue.code_snippet}
                                        </pre>
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </>
                              ) : (
                                <button
                                  onClick={() => setShowAuth(true)}
                                  className="flex items-center gap-2 text-[10px] font-bold text-slate-500 border border-dashed border-slate-700 bg-slate-900/50 px-4 py-2 rounded-lg hover:border-cyan-500/50 hover:text-cyan-400 transition group"
                                >
                                  <Lock className="w-3 h-3 group-hover:scale-110 transition" />
                                  Login to view Nginx/Apache Hotfix
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
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
                    <div
                      key={scan.id}
                      onClick={() => handleViewHistoryScan(scan)}
                      className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-cyan-500/30 transition group cursor-pointer"
                    >
                      <div className="flex items-center gap-5">
                        <div className={`w-14 h-14 rounded-xl flex items-center justify-center font-bold text-2xl ${scan.risk_score === 'A' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' :
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
                        <button className="flex items-center gap-2 px-6 py-2 rounded-xl bg-slate-800 text-slate-300 text-sm hover:bg-slate-700 transition">
                          <ExternalLink className="w-4 h-4" /> View Details
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDownloadReport(scan.pdf_url); }}
                          className="flex items-center gap-2 px-6 py-2 rounded-xl bg-cyan-500 text-black text-sm font-bold hover:bg-cyan-400 transition shadow-lg shadow-cyan-500/10"
                        >
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

      {/* Pricing Modal */}
      <AnimatePresence>
        {showPricing && (
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowPricing(false)}
              className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            />
            <div className="relative min-h-screen">
              <button
                onClick={() => setShowPricing(false)}
                className="absolute top-6 right-6 z-50 p-2 rounded-lg bg-slate-800 text-white hover:bg-slate-700 transition"
              >
                <X className="w-6 h-6" />
              </button>
              <PricingPage
                session={session}
                subscription={subscription}
                onUpgrade={handleUpgrade}
                onCancel={handleCancelSubscription}
                onClose={() => setShowPricing(false)}
              />
            </div>
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
