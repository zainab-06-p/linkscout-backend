"use client";
import React, { useState, useEffect, useRef } from "react";
import { AppLayout } from "@/components/app-layout";
import { AIChatInput } from "@/components/ui/ai-chat-input";
import { AnalysisResults } from "@/components/analysis-results";
import { MessageSquare, Sparkles, Zap, Brain, Link2, Loader2 } from "lucide-react";

interface Message {
  id: string;
  type: "user" | "ai" | "analysis";
  content: string;
  timestamp: Date;
  analysisData?: any;
}

const examplePrompts = [
  { icon: <Brain className="h-4 w-4" />, text: "Paste a URL to analyze an article", color: "from-orange-400 to-yellow-400" },
  { icon: <Zap className="h-4 w-4" />, text: "Verify claims with AI-powered analysis", color: "from-sky-400 to-blue-500" },
  { icon: <Sparkles className="h-4 w-4" />, text: "Get credibility scores instantly", color: "from-orange-500 to-indigo-500" },
];

export default function SearchPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentAnalysisData, setCurrentAnalysisData] = useState<any>(null);
  const messagesRef = useRef<HTMLDivElement | null>(null);

  const handleFeedback = async (feedbackType: 'correct' | 'incorrect' | 'aggressive' | 'lenient') => {
    if (!currentAnalysisData) return;
    
    try {
      const response = await fetch('http://localhost:5000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: currentAnalysisData.title || 'Analysis feedback',
          predicted_score: currentAnalysisData.misinformation_percentage || 0,
          feedback_type: feedbackType,
          timestamp: new Date().toISOString()
        }),
      });
      
      if (response.ok) {
        console.log('✅ Feedback submitted successfully');
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    setIsAnalyzing(true);

    // Check if input is URL or text
    const isURL = message.trim().startsWith('http://') || 
                  message.trim().startsWith('https://') || 
                  message.trim().match(/^www\./i) ||
                  message.trim().match(/\.(com|org|net|edu|gov|co\.|io|ai|tech)/i);
    
    try {
      // Add loading message
      const loadingMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: isURL ? "🔍 Fetching and analyzing URL content..." : "🤖 Analyzing text with AI...",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      let requestBody;
      
      if (isURL) {
        // For URLs: First scrape the content, then analyze
        const urlToAnalyze = message.trim().match(/^https?:\/\//i) 
          ? message.trim() 
          : `https://${message.trim()}`;
        
        // Scrape URL content
        const scrapeResponse = await fetch('/api/scrape-url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: urlToAnalyze }),
        });

        if (!scrapeResponse.ok) {
          throw new Error('Failed to fetch URL content. Please check the URL and try again.');
        }

        const scrapedData = await scrapeResponse.json();
        
        if (!scrapedData.success || !scrapedData.paragraphs || scrapedData.paragraphs.length === 0) {
          throw new Error('No content found at this URL. Please try a different URL.');
        }

        requestBody = {
          url: urlToAnalyze,
          title: scrapedData.title || 'Untitled',
          paragraphs: scrapedData.paragraphs,
        };
      } else {
        // For text: Analyze directly
        requestBody = {
          title: 'Direct Text Analysis',
          paragraphs: [{ index: 0, text: message, type: 'p' }],
        };
      }

      // Call backend API for analysis
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Analysis failed. Please ensure the backend server is running on port 5000.');
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Analysis failed');
      }

      // Remove loading message and add analysis result
      setMessages((prev) => prev.filter(m => m.id !== loadingMessage.id));
      
      const analysisMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: "analysis",
        content: "Analysis complete",
        timestamp: new Date(),
        analysisData: data,
      };
      setMessages((prev) => [...prev, analysisMessage]);
      setCurrentAnalysisData(data); // Store for feedback
      
    } catch (error) {
      // Remove loading message and show error
      setMessages((prev) => prev.filter(m => m.content.includes('Analyzing') || m.content.includes('Fetching')));
      
      const errorMessage: Message = {
        id: (Date.now() + 3).toString(),
        type: "ai",
        content: `❌ ${error instanceof Error ? error.message : 'Analysis failed. Please make sure the backend server is running on port 5000.'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    const el = messagesRef.current;
    if (!el) return;
    try {
      el.scrollTo({ top: el.scrollHeight, behavior });
    } catch (e) {
      el.scrollTop = el.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom("smooth");
  }, [messages]);

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-hidden">
        {/* Header - Compact on mobile */}
        <div className="px-3 py-2 md:p-6 border-b border-orange-500/12 bg-black/20 backdrop-blur-sm shrink-0">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-base md:text-3xl font-bold bg-linear-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent flex items-center gap-2">
              <Sparkles className="h-4 w-4 md:h-8 md:w-8 text-orange-400 shrink-0" />
              <span className="truncate">LinkScout AI Analysis</span>
            </h1>
            <p className="text-orange-100/70 mt-0.5 md:mt-2 text-[10px] md:text-base leading-tight">AI-powered misinformation detection</p>
          </div>
        </div>

        {/* Main Chat Area - Optimized for mobile */}
        <div className="flex-1 flex flex-col bg-black/10 relative overflow-hidden">
          <div className="w-full h-full flex flex-col">
            {/* Message List - Full width on mobile with proper padding */}
            <div 
              ref={messagesRef} 
              role="log" 
              aria-live="polite" 
              aria-relevant="additions text" 
              className="flex-1 w-full overflow-y-auto overscroll-contain px-2 md:px-6 py-3 md:py-6" 
              style={{ 
                paddingBottom: messages.length === 0 ? '20px' : 'calc(100px + env(safe-area-inset-bottom))',
                WebkitOverflowScrolling: 'touch'
              }}
            >
              <div className="max-w-4xl mx-auto">
                {messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center min-h-[calc(100vh-250px)] md:min-h-[400px] text-center px-3">
                    <MessageSquare className="h-10 w-10 md:h-16 md:w-16 text-orange-400 mb-3 md:mb-6" />
                    <h2 className="text-xl md:text-3xl font-bold text-orange-100 mb-1.5 md:mb-3">LinkScout AI Analysis</h2>
                    <p className="text-orange-100/60 mb-5 md:mb-8 text-sm md:text-lg max-w-md px-4">Paste a URL or text to analyze for misinformation</p>
                    {/* Example Prompts - Scrollable on mobile */}
                    <div className="grid grid-cols-1 gap-2.5 md:gap-3 w-full max-w-xl">
                      {examplePrompts.map((prompt, index) => (
                        <div
                          key={index}
                          className="w-full flex items-center gap-2.5 md:gap-3 p-3 md:p-4 bg-white/6 border border-orange-500/12 rounded-xl text-left"
                          aria-label={`Example prompt: ${prompt.text}`}
                        >
                          <div className={`w-9 h-9 md:w-12 md:h-12 rounded-lg bg-linear-to-br ${prompt.color} flex items-center justify-center shrink-0`}>
                            <div className="text-white">{prompt.icon}</div>
                          </div>
                          <span className="text-orange-100 text-xs md:text-base font-medium leading-snug">{prompt.text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col gap-3 md:gap-4 pb-2">
                    {messages.map((message) => (
                      <div key={message.id} className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}>
                        {message.type === "analysis" ? (
                          <div className="w-full">
                            <AnalysisResults data={message.analysisData} onFeedback={handleFeedback} />
                          </div>
                        ) : (
                          <div
                            className={`max-w-full md:max-w-[85%] rounded-xl md:rounded-2xl p-3 md:p-4 ${
                              message.type === "user"
                                ? "bg-linear-to-r from-orange-500 to-yellow-500 text-white shadow-lg shadow-orange-500/20"
                                : "bg-white/8 backdrop-blur-sm text-orange-50 border border-orange-500/12"
                            }`}
                            role="article"
                            aria-label={message.type === "user" ? "Your message" : "AI message"}
                          >
                            <p className="text-xs md:text-base leading-relaxed break-words">{message.content}</p>
                            <span className={`text-[10px] md:text-xs mt-1.5 md:mt-2 block ${message.type === "user" ? "text-white/60" : "text-orange-100/50"}`}>
                              {message.timestamp.toLocaleTimeString()}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Chat Input - Fixed at bottom with enhanced mobile support */}
            <div className="w-full shrink-0 relative z-[100]">
              <div 
                className="fixed inset-x-0 bottom-0 md:relative md:bottom-auto bg-gradient-to-t from-black via-black/95 to-transparent md:bg-transparent pt-4 md:pt-0" 
                style={{ paddingBottom: 'max(env(safe-area-inset-bottom, 12px), 12px)' }}
              >
                <div className="mx-auto px-2.5 md:px-6 pb-2 md:pb-0 max-w-4xl">
                  <div className="backdrop-blur-xl bg-gradient-to-b from-black/50 to-black/70 md:bg-white/8 rounded-xl md:rounded-xl p-2.5 md:p-3 shadow-2xl border border-orange-500/40 md:border-orange-500/20">
                    {/* Swipe indicator - Mobile only */}
                    <div className="w-full flex justify-center md:hidden mb-1.5">
                      <div className="w-10 h-0.5 bg-white/30 rounded-full" aria-hidden="true" />
                    </div>
                    <AIChatInput 
                      autoFocus={false}
                      onSubmit={handleSendMessage} 
                      onFocus={() => {
                        // Scroll to bottom when keyboard appears
                        setTimeout(() => scrollToBottom("smooth"), 150);
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
