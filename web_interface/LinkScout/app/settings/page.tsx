"use client";
import React, { useState } from "react";
import { AppLayout } from "@/components/app-layout";
import { Settings as SettingsIcon, User, Bell, Shield, Palette, Database } from "lucide-react";

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  return (
    <AppLayout>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 md:p-6 border-b border-orange-500/20 bg-black/30 backdrop-blur-sm">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-2xl md:text-3xl font-bold bg-linear-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent flex items-center gap-2">
              <SettingsIcon className="h-6 w-6 md:h-8 md:w-8 text-orange-400" />
              Settings
            </h1>
            <p className="text-orange-100/70 mt-1 md:mt-2 text-sm md:text-base">
              Manage your account and preferences
            </p>
          </div>
        </div>

        {/* Settings Content */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-5xl mx-auto space-y-4 md:space-y-6">
            {/* Profile Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <User className="h-4 w-4 md:h-5 md:w-5 text-orange-400" />
                <h2 className="text-lg md:text-xl font-semibold text-orange-100">Profile</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-orange-100/70 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    placeholder="Your name"
                    className="w-full px-3 md:px-4 py-2 bg-black/30 border border-orange-500/20 rounded-lg text-orange-100 placeholder:text-orange-100/40 focus:outline-none focus:border-orange-500/50 text-sm md:text-base"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-orange-100/70 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="w-full px-3 md:px-4 py-2 bg-black/30 border border-orange-500/20 rounded-lg text-orange-100 placeholder:text-orange-100/40 focus:outline-none focus:border-orange-500/50 text-sm md:text-base"
                  />
                </div>
              </div>
            </div>

            {/* Appearance Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <Palette className="h-4 w-4 md:h-5 md:w-5 text-orange-400" />
                <h2 className="text-lg md:text-xl font-semibold text-orange-100">Appearance</h2>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 font-medium text-sm md:text-base">Dark Mode</p>
                  <p className="text-xs md:text-sm text-orange-100/60">Use dark theme across the app</p>
                </div>
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    darkMode ? 'bg-orange-500' : 'bg-white/20'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      darkMode ? 'translate-x-6' : ''
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Notifications Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <Bell className="h-4 w-4 md:h-5 md:w-5 text-orange-400" />
                <h2 className="text-lg md:text-xl font-semibold text-orange-100">Notifications</h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 font-medium text-sm md:text-base">Push Notifications</p>
                    <p className="text-xs md:text-sm text-orange-100/60">Receive notifications about activity</p>
                  </div>
                  <button
                    onClick={() => setNotifications(!notifications)}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      notifications ? 'bg-orange-500' : 'bg-white/20'
                    }`}
                  >
                    <span
                      className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                        notifications ? 'translate-x-6' : ''
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Data & Privacy Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <Database className="h-4 w-4 md:h-5 md:w-5 text-orange-400" />
                <h2 className="text-lg md:text-xl font-semibold text-orange-100">Data & Privacy</h2>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100 font-medium text-sm md:text-base">Auto-save History</p>
                    <p className="text-xs md:text-sm text-orange-100/60">Automatically save conversation history</p>
                  </div>
                  <button
                    onClick={() => setAutoSave(!autoSave)}
                    className={`relative w-12 h-6 rounded-full transition-colors ${
                      autoSave ? 'bg-orange-500' : 'bg-white/20'
                    }`}
                  >
                    <span
                      className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                        autoSave ? 'translate-x-6' : ''
                      }`}
                    />
                  </button>
                </div>
                <button className="w-full px-4 py-2 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 hover:bg-red-500/30 transition-colors text-sm md:text-base">
                  Clear All History
                </button>
              </div>
            </div>

            {/* Security Section */}
            <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <Shield className="h-4 w-4 md:h-5 md:w-5 text-orange-400" />
                <h2 className="text-lg md:text-xl font-semibold text-orange-100">Security</h2>
              </div>
              <div className="space-y-3">
                <button className="w-full px-4 py-2 bg-black/30 border border-orange-500/20 rounded-lg text-orange-100 hover:border-orange-500/50 transition-colors text-left text-sm md:text-base">
                  Change Password
                </button>
                <button className="w-full px-4 py-2 bg-black/30 border border-orange-500/20 rounded-lg text-orange-100 hover:border-orange-500/50 transition-colors text-left text-sm md:text-base">
                  Two-Factor Authentication
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
