"use client";
import React, { useState } from "react";
import { AppLayout } from "@/components/app-layout";
import { History as HistoryIcon, Clock, Search, Trash2, Filter, TrendingUp } from "lucide-react";

interface HistoryItem {
  id: string;
  query: string;
  timestamp: Date;
  responses: number;
}

const mockHistory: HistoryItem[] = [
  {
    id: "1",
    query: "How to implement authentication in Next.js?",
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 mins ago
    responses: 3
  },
  {
    id: "2",
    query: "Best practices for React performance optimization",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    responses: 5
  },
  {
    id: "3",
    query: "Explain WebGL shader programming",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    responses: 7
  },
  {
    id: "4",
    query: "TypeScript advanced types tutorial",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
    responses: 4
  },
  {
    id: "5",
    query: "How to deploy to Vercel with custom domain?",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
    responses: 2
  },
];

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 60) return `${diffMins} minutes ago`;
  if (diffHours < 24) return `${diffHours} hours ago`;
  return `${diffDays} days ago`;
}

export default function HistoryPage() {
  const [filter, setFilter] = useState<'all' | 'today' | 'week' | 'month'>('all');
  
  const totalQueries = mockHistory.length;
  const totalResponses = mockHistory.reduce((acc, item) => acc + item.responses, 0);

  return (
    <AppLayout>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 md:p-6 border-b border-orange-500/20 bg-black/30 backdrop-blur-sm">
          <div className="max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold bg-linear-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent flex items-center gap-2">
                  <HistoryIcon className="h-6 w-6 md:h-8 md:w-8 text-orange-400" />
                  Search History
                </h1>
                <p className="text-orange-100/70 mt-1 md:mt-2 text-sm md:text-base">
                  View and manage your recent AI conversations
                </p>
              </div>
              
              {/* Filter Buttons */}
              <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                {(['all', 'today', 'week', 'month'] as const).map((filterOption) => (
                  <button
                    key={filterOption}
                    onClick={() => setFilter(filterOption)}
                    className={`px-3 md:px-4 py-2 rounded-lg text-xs md:text-sm font-medium transition-all whitespace-nowrap ${
                      filter === filterOption
                        ? 'bg-orange-500/30 text-orange-100 border border-orange-500/50'
                        : 'bg-white/5 text-orange-100/60 border border-orange-500/20 hover:bg-white/10'
                    }`}
                  >
                    {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Stats */}
            <div className="grid grid-cols-3 gap-2 md:gap-4 mt-4 md:mt-6">
              <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-lg md:rounded-xl p-3 md:p-4">
                <div className="flex items-center gap-1 md:gap-2 text-orange-400 mb-1">
                  <Search className="h-3 w-3 md:h-4 md:w-4" />
                  <span className="text-[10px] md:text-xs font-medium">Total Queries</span>
                </div>
                <p className="text-lg md:text-2xl font-bold text-orange-100">{totalQueries}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-lg md:rounded-xl p-3 md:p-4">
                <div className="flex items-center gap-1 md:gap-2 text-cyan-400 mb-1">
                  <TrendingUp className="h-3 w-3 md:h-4 md:w-4" />
                  <span className="text-[10px] md:text-xs font-medium">Total Responses</span>
                </div>
                <p className="text-lg md:text-2xl font-bold text-orange-100">{totalResponses}</p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-lg md:rounded-xl p-3 md:p-4">
                <div className="flex items-center gap-1 md:gap-2 text-sky-400 mb-1">
                  <Clock className="h-3 w-3 md:h-4 md:w-4" />
                  <span className="text-[10px] md:text-xs font-medium">Avg. per Query</span>
                </div>
                <p className="text-lg md:text-2xl font-bold text-orange-100">{(totalResponses / totalQueries).toFixed(1)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-5xl mx-auto space-y-3 md:space-y-4">
            {mockHistory.map((item) => (
              <div
                key={item.id}
                className="group bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6 hover:bg-white/10 hover:border-orange-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-orange-500/10"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 text-orange-100 mb-2">
                      <Search className="h-4 w-4 text-orange-400 shrink-0" />
                      <h3 className="font-medium line-clamp-2 text-sm md:text-base">{item.query}</h3>
                    </div>
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs md:text-sm text-orange-100/60">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatRelativeTime(item.timestamp)}
                      </span>
                      <span className="px-2 py-1 bg-orange-500/20 rounded-md text-orange-300 text-xs font-medium w-fit">
                        {item.responses} responses
                      </span>
                    </div>
                  </div>
                  <button
                    className="p-2 rounded-lg text-orange-100/60 hover:text-red-400 hover:bg-red-500/10 transition-colors md:opacity-0 md:group-hover:opacity-100"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4 md:h-5 md:w-5" />
                  </button>
                </div>
              </div>
            ))}

            {mockHistory.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12 md:py-20 text-center">
                <div className="w-12 h-12 md:w-16 md:h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                  <HistoryIcon className="h-6 w-6 md:h-8 md:w-8 text-orange-400/50" />
                </div>
                <h2 className="text-lg md:text-xl font-semibold text-orange-100 mb-2">
                  No History Yet
                </h2>
                <p className="text-sm md:text-base text-orange-100/60">
                  Your AI conversations will appear here
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
