'use client';

import React from 'react';
import { User } from '../lib/types';
import { Activity, BookOpen, Landmark, History, LogIn, User as UserIcon, LogOut, Globe } from 'lucide-react';

interface NavbarProps {
  onOpenHandbook: () => void;
  onOpenSchemes: () => void;
  onOpenHistory: () => void;
  onOpenAuth: () => void;
  user: User | null;
  onLogout: () => void;
  language: string;
  onLanguageChange: (lang: string) => void;
  systemOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenHandbook,
  onOpenSchemes,
  onOpenHistory,
  onOpenAuth,
  user,
  onLogout,
  language,
  onLanguageChange,
  systemOnline,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 text-white shadow-md shadow-brand-500/20">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-black tracking-tight text-slate-900">GeneRisk</span>
              <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[10px] font-extrabold text-brand-700 border border-brand-200">
                2.0 AI
              </span>
            </div>
            <p className="text-[11px] font-medium text-slate-500 hidden sm:block">
              AI Genomic Risk Intelligence &amp; Public Health Portal
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Handbook Button */}
          <button
            type="button"
            onClick={onOpenHandbook}
            className="flex items-center space-x-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-brand-50 hover:border-brand-300 hover:text-brand-700 transition-all shadow-2xs"
            title="Genomics 101 Educational Handbook"
          >
            <BookOpen className="h-3.5 w-3.5 text-brand-600" />
            <span className="hidden md:inline">DNA Handbook</span>
          </button>

          {/* Cancer & Diseases Awareness */}
          <a
            href="#disease-awareness"
            className="flex items-center space-x-1.5 rounded-xl border border-rose-200 bg-rose-50/70 px-3 py-1.5 text-xs font-bold text-rose-800 hover:bg-rose-100 transition-all shadow-2xs"
            title="Cancer & Common Diseases Awareness Hub"
          >
            <span className="text-rose-600">🎗️</span>
            <span className="hidden md:inline">Cancer &amp; Diseases</span>
          </a>

          {/* Govt Schemes Button */}
          <button
            type="button"
            onClick={onOpenSchemes}
            className="flex items-center space-x-1.5 rounded-xl border border-emerald-200 bg-emerald-50/70 px-3 py-1.5 text-xs font-bold text-emerald-800 hover:bg-emerald-100 transition-all shadow-2xs"
            title="Ayushman Bharat & Govt Healthcare Schemes"
          >
            <Landmark className="h-3.5 w-3.5 text-emerald-700" />
            <span className="hidden md:inline">Govt Schemes</span>
          </button>

          {/* History Button */}
          <button
            type="button"
            onClick={onOpenHistory}
            className="flex items-center space-x-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-all shadow-2xs"
            title="My Saved Reports (MongoDB)"
          >
            <History className="h-3.5 w-3.5 text-indigo-600" />
            <span className="hidden md:inline">History</span>
          </button>

          {/* User Profile / Auth */}
          {user ? (
            <div className="flex items-center space-x-2 rounded-xl bg-slate-100 px-3 py-1 text-xs">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-600 text-white font-bold text-[10px]">
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              <span className="font-bold text-slate-800 hidden sm:inline truncate max-w-[100px]">
                {user.full_name}
              </span>
              <button
                type="button"
                onClick={onLogout}
                className="text-slate-400 hover:text-rose-600 transition-colors ml-1"
                title="Log out"
              >
                <LogOut className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenAuth}
              className="flex items-center space-x-1.5 rounded-xl bg-slate-900 px-3.5 py-1.5 text-xs font-bold text-white hover:bg-slate-800 transition-colors shadow-xs"
            >
              <LogIn className="h-3.5 w-3.5 text-brand-300" />
              <span>Sign In</span>
            </button>
          )}

          {/* Language Selector */}
          <div className="flex items-center space-x-1 rounded-xl border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-700">
            <Globe className="h-3.5 w-3.5 text-slate-400" />
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="bg-transparent text-xs font-bold focus:outline-none cursor-pointer"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="kn">ಕನ್ನಡ (Kannada)</option>
              <option value="es">Español</option>
            </select>
          </div>
        </div>
      </div>
    </header>
  );
};
