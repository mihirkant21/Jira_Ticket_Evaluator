"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Ticket, Github, ArrowRight, Zap, CheckCircle2, ShieldAlert, ShieldCheck, FileCode2, TestTube2 } from 'lucide-react';

export default function Home() {
  const [jiraId, setJiraId] = useState('');
  const [prUrl, setPrUrl] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jiraId || !prUrl) return;
    
    setIsEvaluating(true);
    setError('');
    setResult(null);
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jira_id: jiraId, github_pr_url: prUrl })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Evaluation failed');
      }
      
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      
      {/* Decorative Blur Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-purple-500/20 rounded-full blur-3xl" />

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-xl w-full"
      >
        <div className="text-center mb-10 text-white">
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: "spring" }}
            className="flex justify-center mb-6"
          >
            <div className="p-4 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-2xl shadow-xl shadow-purple-500/20">
              <Zap className="w-10 h-10 text-white" />
            </div>
          </motion.div>
          
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            Jira Ticket Evaluator
          </h1>
          <p className="text-slate-400 text-lg">
            AI-powered semantic verification of your Pull Requests against explicit Jira requirements.
          </p>
        </div>

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="glass-card rounded-3xl p-8 relative overflow-hidden"
        >
          {/* Subtle shimmer effect on the card */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full hover:animate-[shimmer_2s_infinite]" />

          <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
            
            {/* Jira Ticket Input */}
            <div className="space-y-2">
              <label htmlFor="jiraId" className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Ticket className="w-4 h-4 text-blue-400" />
                Jira Ticket ID
              </label>
              <div className="relative group">
                <input
                  type="text"
                  id="jiraId"
                  placeholder="e.g., PROJ-123"
                  value={jiraId}
                  onChange={(e) => setJiraId(e.target.value)}
                  className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-4 py-3.5 text-slate-100 placeholder-slate-500 outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-300"
                  required
                />
                <div className="absolute inset-0 border border-blue-500 rounded-xl opacity-0 group-hover:opacity-20 transition-opacity pointer-events-none" />
              </div>
            </div>

            {/* GitHub PR Input */}
            <div className="space-y-2">
              <label htmlFor="prUrl" className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Github className="w-4 h-4 text-purple-400" />
                GitHub PR URL
              </label>
              <div className="relative group">
                <input
                  type="url"
                  id="prUrl"
                  placeholder="https://github.com/org/repo/pull/45"
                  value={prUrl}
                  onChange={(e) => setPrUrl(e.target.value)}
                  className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl px-4 py-3.5 text-slate-100 placeholder-slate-500 outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-300"
                  required
                />
                <div className="absolute inset-0 border border-purple-500 rounded-xl opacity-0 group-hover:opacity-20 transition-opacity pointer-events-none" />
              </div>
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isEvaluating}
              className={`w-full relative group overflow-hidden rounded-xl p-0.5 mt-4 transition-all ${
                isEvaluating ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 flex justify-center items-center opacity-70 group-hover:opacity-100 transition-opacity duration-500 bg-[length:200%_auto] animate-gradient" />
              <div className="relative bg-slate-900/40 backdrop-blur-sm px-6 py-4 rounded-[10px] flex justify-center items-center gap-3">
                {isEvaluating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span className="text-white font-medium">Initializing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <span className="text-white font-semibold flex items-center gap-2">
                      Start Evaluation <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </span>
                  </>
                )}
              </div>
            </motion.button>
          </form>
        </motion.div>

        {/* Feature blocks beneath (Only show if no result) */}
        {!result && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 1 }}
            className="mt-12 flex justify-center gap-6 text-sm text-slate-400"
          >
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Stage 1 Validation
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              10-Stage Pipeline
            </div>
          </motion.div>
        )}

        {/* Error Display */}
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-center"
          >
            {error}
          </motion.div>
        )}

        {/* Results Display */}
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 space-y-6"
          >
            <div className="glass-card rounded-2xl p-6 text-center border-t border-t-white/10">
              <h2 className="text-2xl font-bold mb-2 flex items-center justify-center gap-3">
                {result.overall_verdict === 'PASS' ? (
                  <><ShieldCheck className="w-8 h-8 text-emerald-400" /> <span className="text-emerald-400">PASSED</span></>
                ) : result.overall_verdict === 'PARTIAL' ? (
                  <><ShieldAlert className="w-8 h-8 text-amber-400" /> <span className="text-amber-400">PARTIAL PASS</span></>
                ) : (
                  <><ShieldAlert className="w-8 h-8 text-red-400" /> <span className="text-red-400">FAILED</span></>
                )}
              </h2>
              <p className="text-slate-300">{result.summary}</p>
              
              {result.planner_decisions && (
                <div className="mt-4 pt-4 border-t border-white/5 text-xs text-blue-400/80 italic">
                  <Zap className="w-3 h-3 inline mr-1 mb-1" />
                  Planner Logic: {result.planner_decisions}
                </div>
              )}
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-200 pl-2">Requirement Breakdown</h3>
              
              {result.requirements?.map((req: any, idx: number) => (
                <div key={idx} className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-5 shadow-lg">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1 pr-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold uppercase tracking-wider text-blue-400">REQ-{req.id}</span>
                        {req.classification && (
                          <span className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-400 rounded border border-slate-700 uppercase tracking-tighter">
                            {req.classification}
                          </span>
                        )}
                      </div>
                      <p className="text-slate-200 font-medium">{req.statement}</p>
                    </div>
                    <div>
                      {req.verdict === 'PASS' ? (
                        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/30">PASS</span>
                      ) : (
                        <span className="px-3 py-1 bg-red-500/20 text-red-400 text-xs font-bold rounded-full border border-red-500/30">FAIL</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                    <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800">
                      <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2 flex items-center gap-2">
                        <FileCode2 className="w-3 h-3" /> Code Evidence
                      </h4>
                      <p className="text-sm text-slate-300 whitespace-pre-wrap font-mono">
                        {req.evidence 
                          ? (typeof req.evidence === 'object' ? JSON.stringify(req.evidence, null, 2) : String(req.evidence))
                          : "No significant evidence found."}
                      </p>
                      {req.confidence && (
                        <div className="mt-3 text-xs text-slate-500">
                          AI Confidence: {(req.confidence * 100).toFixed(0)}%
                        </div>
                      )}
                    </div>
                    
                    <div className="bg-slate-950/50 rounded-lg p-4 border border-slate-800">
                      <h4 className="text-xs font-semibold text-slate-400 uppercase mb-2 flex items-center gap-2">
                        <TestTube2 className="w-3 h-3" /> Generated Test Result
                      </h4>
                      <p className={`text-sm ${req.test_result === 'PASS' ? 'text-emerald-400/80' : 'text-red-400/80'}`}>
                        {req.test_result}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>
    </main>
  );
}
