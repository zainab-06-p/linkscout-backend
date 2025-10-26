"use client";
import React, { useState } from "react";
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Globe, 
  Lightbulb, 
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Image as ImageIcon,
  Tag,
  Users,
  Brain,
  ThumbsUp,
  ThumbsDown,
  Zap
} from "lucide-react";

interface AnalysisResultsProps {
  data: any;
  onFeedback?: (feedbackType: 'correct' | 'incorrect' | 'aggressive' | 'lenient') => void;
}

export function AnalysisResults({ data, onFeedback }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'sources' | 'images'>('overview');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overview: true,
    correct: true,
    wrong: true,
    internet: true,
    recommendation: true,
    matters: true
  });
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [showFeedback, setShowFeedback] = useState(true);

  if (!data || !data.success) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6 bg-red-500/10 border border-red-500/30 rounded-2xl">
        <div className="flex items-start gap-3">
          <XCircle className="h-6 w-6 text-red-400 shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-bold text-red-100">Analysis Failed</h3>
            <p className="text-red-200/70 mt-1 text-sm">
              {data?.error || 'Unable to analyze content. Please try again.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const percentage = data.misinformation_percentage || 0;
  const verdict = data.verdict || 'UNKNOWN';
  
  // Determine color scheme based on percentage
  let verdictColor = 'text-green-400';
  let bgGradient = 'from-green-500/20 to-emerald-500/20';
  let borderColor = 'border-green-500/30';
  
  if (percentage > 60) {
    verdictColor = 'text-red-400';
    bgGradient = 'from-red-500/20 to-rose-500/20';
    borderColor = 'border-red-500/30';
  } else if (percentage > 30) {
    verdictColor = 'text-yellow-400';
    bgGradient = 'from-yellow-500/20 to-amber-500/20';
    borderColor = 'border-yellow-500/30';
  }

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  return (
    <div className="w-full space-y-3 md:space-y-4">
      {/* Verdict Card - Mobile optimized */}
      <div className={`bg-gradient-to-br ${bgGradient} border ${borderColor} rounded-xl md:rounded-2xl p-4 md:p-6 backdrop-blur-sm`}>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 md:gap-4">
          <div className="flex-1 w-full">
            <div className="flex items-center gap-2 md:gap-3 mb-1.5 md:mb-2">
              {percentage < 30 ? (
                <CheckCircle2 className="h-6 w-6 md:h-8 md:w-8 text-green-400 shrink-0" />
              ) : percentage < 60 ? (
                <AlertTriangle className="h-6 w-6 md:h-8 md:w-8 text-yellow-400 shrink-0" />
              ) : (
                <XCircle className="h-6 w-6 md:h-8 md:w-8 text-red-400 shrink-0" />
              )}
              <h2 className={`text-xl md:text-3xl font-bold ${verdictColor} truncate`}>
                {verdict}
              </h2>
            </div>
            {data.title && (
              <p className="text-orange-100/70 text-xs md:text-base line-clamp-2">{data.title}</p>
            )}
          </div>
          <div className="text-center self-end md:self-auto">
            <div className={`text-4xl md:text-6xl font-bold ${verdictColor} tabular-nums`}>
              {percentage.toFixed(1)}%
            </div>
            <div className="text-orange-100/60 text-xs md:text-sm mt-0.5 md:mt-1">Risk Score</div>
          </div>
        </div>

        {/* Progress Bar - Slimmer on mobile */}
        <div className="mt-4 md:mt-6 bg-black/20 rounded-full h-2 md:h-3 overflow-hidden">
          <div 
            className={`h-full rounded-full transition-all duration-1000 ${
              percentage < 30 ? 'bg-gradient-to-r from-green-400 to-emerald-500' :
              percentage < 60 ? 'bg-gradient-to-r from-yellow-400 to-amber-500' :
              'bg-gradient-to-r from-red-400 to-rose-500'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>

        {/* Quick Stats - Compact on mobile */}
        {data.overall && (
          <div className="grid grid-cols-3 gap-2 md:gap-3 mt-4 md:mt-6">
            <div className="bg-black/20 rounded-lg p-2 md:p-3 text-center">
              <div className="text-lg md:text-2xl font-bold text-orange-100 tabular-nums">{data.overall.total_paragraphs || 0}</div>
              <div className="text-[10px] md:text-xs text-orange-100/60 mt-0.5 md:mt-1 leading-tight">Total Paragraphs</div>
            </div>
            <div className="bg-black/20 rounded-lg p-2 md:p-3 text-center">
              <div className="text-lg md:text-2xl font-bold text-red-400 tabular-nums">{data.overall.fake_paragraphs || 0}</div>
              <div className="text-[10px] md:text-xs text-orange-100/60 mt-0.5 md:mt-1 leading-tight">High Risk</div>
            </div>
            <div className="bg-black/20 rounded-lg p-2 md:p-3 text-center">
              <div className="text-lg md:text-2xl font-bold text-yellow-400 tabular-nums">{data.overall.suspicious_paragraphs || 0}</div>
              <div className="text-[10px] md:text-xs text-orange-100/60 mt-0.5 md:mt-1 leading-tight">Medium Risk</div>
            </div>
          </div>
        )}
      </div>

      {/* Tabs - Horizontal scroll on mobile */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide -mx-2 px-2 md:mx-0 md:px-0">
        {['overview', 'details', 'sources', 'images'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={`px-3 md:px-4 py-1.5 md:py-2 rounded-lg font-medium text-xs md:text-sm whitespace-nowrap transition-all shrink-0 ${
              activeTab === tab
                ? 'bg-gradient-to-r from-orange-500 to-yellow-500 text-white shadow-lg'
                : 'bg-white/5 text-orange-100/70 active:bg-white/12 md:hover:bg-white/10'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content - Mobile optimized spacing */}
      <div className="space-y-3 md:space-y-4">
        {activeTab === 'overview' && (
          <>
            {/* Categories */}
            {data.pretrained_models?.categories && data.pretrained_models.categories.length > 0 && (
              <Section title="Categories" icon={<Tag className="h-4 w-4 md:h-5 md:w-5" />} gradient="from-yellow-500/20 to-amber-500/20">
                <div className="flex flex-wrap gap-1.5 md:gap-2">
                  {data.pretrained_models.categories.map((cat: string, idx: number) => (
                    <span key={idx} className="px-2 md:px-3 py-1 bg-gradient-to-r from-yellow-400 to-amber-500 text-white text-[10px] md:text-xs font-bold rounded-full whitespace-nowrap">
                      {cat}
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {/* Entities */}
            {data.pretrained_models?.named_entities && data.pretrained_models.named_entities.length > 0 && (
              <Section title="Key Entities" icon={<Users className="h-4 w-4 md:h-5 md:w-5" />} gradient="from-purple-500/20 to-pink-500/20">
                <div className="flex flex-wrap gap-1.5 md:gap-2">
                  {data.pretrained_models.named_entities.slice(0, 10).map((entity: string, idx: number) => (
                    <span key={idx} className="px-2 md:px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-[10px] md:text-xs font-semibold rounded-full shadow-lg whitespace-nowrap">
                      {entity}
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {/* What's Correct */}
            {data.what_is_right && data.what_is_right !== 'See conclusion' && data.what_is_right !== 'See full conclusion' && (
              <CollapsibleSection
                title="What's Correct"
                icon={<CheckCircle2 className="h-4 w-4 md:h-5 md:w-5" />}
                gradient="from-green-500/20 to-emerald-500/20"
                borderColor="border-green-500/30"
                isExpanded={expandedSections.correct}
                onToggle={() => toggleSection('correct')}
              >
                <div className="text-green-50 whitespace-pre-line leading-relaxed text-xs md:text-base">
                  {data.what_is_right.replace(/\*\*/g, '').replace(/WHAT IS CORRECT:/gi, '').trim()}
                </div>
              </CollapsibleSection>
            )}

            {/* What's Wrong */}
            {data.what_is_wrong && data.what_is_wrong !== 'See conclusion' && data.what_is_wrong !== 'See full conclusion' && (
              <CollapsibleSection
                title="What's Wrong"
                icon={<XCircle className="h-4 w-4 md:h-5 md:w-5" />}
                gradient="from-red-500/20 to-rose-500/20"
                borderColor="border-red-500/30"
                isExpanded={expandedSections.wrong}
                onToggle={() => toggleSection('wrong')}
              >
                <div className="text-red-50 whitespace-pre-line leading-relaxed text-xs md:text-base">
                  {data.what_is_wrong.replace(/\*\*/g, '').replace(/WHAT IS WRONG:/gi, '').trim()}
                </div>
              </CollapsibleSection>
            )}

            {/* What Internet Says */}
            {data.internet_says && data.internet_says !== 'See conclusion' && data.internet_says !== 'See full conclusion' && (
              <CollapsibleSection
                title="What the Internet Says"
                icon={<Globe className="h-4 w-4 md:h-5 md:w-5" />}
                gradient="from-blue-500/20 to-cyan-500/20"
                borderColor="border-blue-500/30"
                isExpanded={expandedSections.internet}
                onToggle={() => toggleSection('internet')}
              >
                <div className="text-blue-50 whitespace-pre-line leading-relaxed text-xs md:text-base">
                  {data.internet_says.replace(/\*\*/g, '').replace(/WHAT THE INTERNET SAYS:/gi, '').trim()}
                </div>
              </CollapsibleSection>
            )}

            {/* Recommendation */}
            {data.recommendation && data.recommendation !== 'Verify with credible sources' && data.recommendation.length > 30 && (
              <CollapsibleSection
                title="Recommendation"
                icon={<Lightbulb className="h-4 w-4 md:h-5 md:w-5" />}
                gradient="from-yellow-500/20 to-amber-500/20"
                borderColor="border-yellow-500/30"
                isExpanded={expandedSections.recommendation}
                onToggle={() => toggleSection('recommendation')}
              >
                <div className="text-yellow-50 whitespace-pre-line leading-relaxed text-xs md:text-base">
                  {data.recommendation.replace(/\*\*/g, '').replace(/MY RECOMMENDATION:/gi, '').replace(/RECOMMENDATION:/gi, '').trim()}
                </div>
              </CollapsibleSection>
            )}

            {/* Why It Matters */}
            {data.why_matters && data.why_matters !== 'Critical thinking is essential' && data.why_matters.length > 30 && (
              <CollapsibleSection
                title="Why This Matters"
                icon={<AlertCircle className="h-4 w-4 md:h-5 md:w-5" />}
                gradient="from-purple-500/20 to-violet-500/20"
                borderColor="border-purple-500/30"
                isExpanded={expandedSections.matters}
                onToggle={() => toggleSection('matters')}
              >
                <div className="text-purple-50 whitespace-pre-line leading-relaxed">
                  {data.why_matters.replace(/\*\*/g, '').replace(/WHY THIS MATTERS:/gi, '').replace(/Why this matters:/gi, '').trim()}
                </div>
              </CollapsibleSection>
            )}
          </>
        )}

        {activeTab === 'details' && (
          <>
            {/* Combined Credibility Analysis - EXACTLY Like Extension */}
            {data.combined_analysis && (
              <Section 
                title="🎯 Overall Credibility Analysis" 
                icon={<Brain className="h-5 w-5" />} 
                gradient="from-white/5 to-white/10"
                borderColor="border-orange-500/20"
              >
                <div className="space-y-4">
                  {/* Credibility Meter */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm md:text-base font-semibold text-orange-100/80">Risk Score</span>
                      <span className="text-3xl md:text-5xl font-bold tabular-nums" style={{ color: data.combined_analysis.verdict_color || '#f59e0b' }}>
                        {Math.round(data.combined_analysis.overall_score || 0)}/100
                      </span>
                    </div>
                    
                    {/* Meter Bar */}
                    <div className="relative bg-gray-200 rounded-xl h-8 md:h-10 overflow-hidden">
                      <div 
                        className="h-full rounded-xl transition-all duration-1000"
                        style={{
                          width: `${Math.min(data.combined_analysis.overall_score || 0, 100)}%`,
                          background: `linear-gradient(90deg, ${
                            (data.combined_analysis.overall_score || 0) > 50 ? '#ef4444' :
                            (data.combined_analysis.overall_score || 0) > 35 ? '#f59e0b' :
                            (data.combined_analysis.overall_score || 0) > 20 ? '#3b82f6' :
                            '#10b981'
                          }, ${
                            (data.combined_analysis.overall_score || 0) > 50 ? '#dc2626dd' :
                            (data.combined_analysis.overall_score || 0) > 35 ? '#d97706dd' :
                            (data.combined_analysis.overall_score || 0) > 20 ? '#2563ebdd' :
                            '#059669dd'
                          })`
                        }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="font-bold text-xs md:text-sm tracking-wide" style={{
                          color: (data.combined_analysis.overall_score || 0) > 50 ? 'white' : '#1f2937'
                        }}>
                          {data.combined_analysis.verdict || 'UNKNOWN'}
                        </span>
                      </div>
                    </div>
                    
                    {/* Legend */}
                    <div className="flex justify-between mt-1.5 text-[10px] md:text-xs text-orange-100/40">
                      <span>0 - Highly Credible</span>
                      <span>100 - Not Credible</span>
                    </div>
                  </div>
                  
                  {/* Quick Stats */}
                  {data.overall && (
                    <div className="grid grid-cols-2 gap-3 md:gap-4">
                      <div className="bg-gray-100 dark:bg-black/20 p-4 rounded-lg text-center border border-gray-300 dark:border-red-500/20">
                        <div className="text-2xl md:text-3xl font-bold text-red-500">{data.overall.fake_paragraphs || 0}</div>
                        <div className="text-[11px] md:text-xs text-gray-600 dark:text-orange-100/60 mt-1">High Risk Paragraphs</div>
                      </div>
                      <div className="bg-gray-100 dark:bg-black/20 p-4 rounded-lg text-center border border-gray-300 dark:border-yellow-500/20">
                        <div className="text-2xl md:text-3xl font-bold text-yellow-500">{data.overall.suspicious_paragraphs || 0}</div>
                        <div className="text-[11px] md:text-xs text-gray-600 dark:text-orange-100/60 mt-1">Medium Risk Paragraphs</div>
                      </div>
                    </div>
                  )}
                  
                  {/* Detection Systems Note */}
                  <div className="p-3 md:p-4 bg-yellow-100 dark:bg-yellow-500/20 border-l-4 border-yellow-500 rounded-lg">
                    <div className="text-xs md:text-sm text-yellow-900 dark:text-yellow-100 leading-relaxed">
                      <strong className="block mb-1">📊 Analysis Based On:</strong>
                      8 detection systems including linguistic patterns, claim verification, source credibility, entity verification, propaganda detection, network analysis, contradiction detection, and AI propagation analysis.
                    </div>
                  </div>
                </div>
              </Section>
            )}
            
            {/* Suspicious Items */}
            {data.chunks && data.chunks.length > 0 && (
              <Section title={`Suspicious Paragraphs (${data.chunks.length})`} icon={<AlertTriangle className="h-5 w-5" />}>
                <div className="space-y-3">
                  {data.chunks.slice(0, 10).map((chunk: any, idx: number) => (
                    <div 
                      key={idx}
                      className={`p-4 rounded-lg border ${
                        chunk.severity === 'high' 
                          ? 'bg-red-500/10 border-red-500/30' 
                          : 'bg-yellow-500/10 border-yellow-500/30'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-sm font-bold text-orange-100">Paragraph {chunk.index + 1}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                          chunk.severity === 'high' ? 'bg-red-500 text-white' : 'bg-yellow-500 text-white'
                        }`}>
                          {chunk.suspicious_score}/100
                        </span>
                      </div>
                      <p className="text-sm text-orange-100/80 italic mb-2">"{chunk.text_preview}"</p>
                      {chunk.why_flagged && (
                        <p className="text-xs text-orange-100/70">{chunk.why_flagged}</p>
                      )}
                    </div>
                  ))}
                </div>
              </Section>
            )}
          </>
        )}

        {activeTab === 'sources' && (
          <>
            {/* Research Sources */}
            {((data.research_sources && data.research_sources.length > 0) || 
              (data.sources_found && data.sources_found.length > 0)) ? (
              <Section title={`Research Sources (${(data.research_sources || data.sources_found || []).length})`} icon={<Globe className="h-5 w-5" />}>
                <div className="space-y-2">
                  {(data.research_sources || data.sources_found || []).map((source: any, idx: number) => {
                    const isString = typeof source === 'string';
                    const url = isString ? source : (source.url || source.link || '#');
                    const title = isString ? `Source ${idx + 1}` : (source.title || source.name || `Source ${idx + 1}`);
                    const snippet = !isString && source.snippet ? source.snippet : '';
                    
                    return (
                      <a
                        key={idx}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 md:p-4 bg-white/5 active:bg-white/12 md:hover:bg-white/10 border border-orange-500/20 active:border-orange-500/40 md:hover:border-orange-500/40 rounded-lg transition-all"
                      >
                        <div className="flex items-start gap-2">
                          <Globe className="h-4 w-4 text-orange-400 shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-orange-100 line-clamp-2">{title}</div>
                            {snippet && (
                              <div className="text-xs text-orange-100/60 mt-1 line-clamp-2">{snippet}</div>
                            )}
                            <div className="text-xs text-orange-400/60 mt-1 truncate">{url}</div>
                          </div>
                        </div>
                      </a>
                    );
                  })}
                </div>
              </Section>
            ) : (
              <Section title="Research Sources" icon={<Globe className="h-5 w-5" />}>
                <div className="text-center py-8">
                  <Globe className="h-12 w-12 text-orange-400/40 mx-auto mb-3" />
                  <p className="text-orange-100/60 text-sm">
                    No external sources were found for verification.
                  </p>
                  <p className="text-orange-100/40 text-xs mt-2">
                    This could mean the content is unique or not widely covered.
                  </p>
                </div>
              </Section>
            )}
          </>
        )}

        {activeTab === 'images' && (
          <>
            {data.image_analysis && data.image_analysis.analyzed_images > 0 ? (
              <>
                <Section 
                  title="Image Analysis Summary" 
                  icon={<ImageIcon className="h-5 w-5" />}
                  gradient={data.image_analysis.ai_generated_count > 0 ? "from-red-500/20 to-rose-500/20" : "from-green-500/20 to-emerald-500/20"}
                >
                  <p className="text-orange-100 leading-relaxed">
                    {data.image_analysis.summary}
                  </p>
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    <div className="bg-black/20 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-blue-400">{data.image_analysis.analyzed_images}</div>
                      <div className="text-xs text-orange-100/60 mt-1">Analyzed</div>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-red-400">{data.image_analysis.ai_generated_count}</div>
                      <div className="text-xs text-orange-100/60 mt-1">AI-Generated</div>
                    </div>
                    <div className="bg-black/20 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-green-400">{data.image_analysis.real_images_count || 0}</div>
                      <div className="text-xs text-orange-100/60 mt-1">Real Photos</div>
                    </div>
                  </div>
                </Section>
              </>
            ) : (
              <Section title="Image Analysis" icon={<ImageIcon className="h-5 w-5" />}>
                <p className="text-orange-100/60 text-center py-8">
                  {data.image_analysis?.total_images === 0 
                    ? '📷 No images found on this page' 
                    : '🖼️ No image analysis data available'}
                </p>
              </Section>
            )}
          </>
        )}
      </div>

      {/* RL Feedback Section */}
      {showFeedback && !feedbackGiven && (
        <div className="bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border border-purple-500/30 rounded-xl p-4 md:p-6">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="h-5 w-5 text-purple-400" />
            <h3 className="text-base md:text-lg font-bold text-purple-100">Help Improve AI Accuracy</h3>
          </div>
          <p className="text-xs md:text-sm text-purple-100/70 mb-4">
            Your feedback trains our AI to be more accurate over time using Reinforcement Learning!
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3">
            <button
              onClick={() => {
                if (onFeedback) onFeedback('correct');
                setFeedbackGiven(true);
                setTimeout(() => setShowFeedback(false), 3000);
              }}
              className="px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-medium text-xs md:text-sm active:scale-95 md:hover:scale-105 transition-transform flex items-center justify-center gap-1.5"
            >
              <ThumbsUp className="h-4 w-4" />
              <span>Accurate</span>
            </button>
            <button
              onClick={() => {
                if (onFeedback) onFeedback('incorrect');
                setFeedbackGiven(true);
                setTimeout(() => setShowFeedback(false), 3000);
              }}
              className="px-3 py-2 bg-gradient-to-r from-red-500 to-rose-500 text-white rounded-lg font-medium text-xs md:text-sm active:scale-95 md:hover:scale-105 transition-transform flex items-center justify-center gap-1.5"
            >
              <ThumbsDown className="h-4 w-4" />
              <span>Inaccurate</span>
            </button>
            <button
              onClick={() => {
                if (onFeedback) onFeedback('aggressive');
                setFeedbackGiven(true);
                setTimeout(() => setShowFeedback(false), 3000);
              }}
              className="px-3 py-2 bg-gradient-to-r from-yellow-500 to-amber-500 text-white rounded-lg font-medium text-xs md:text-sm active:scale-95 md:hover:scale-105 transition-transform flex items-center justify-center gap-1.5"
            >
              <AlertTriangle className="h-4 w-4" />
              <span>Too Strict</span>
            </button>
            <button
              onClick={() => {
                if (onFeedback) onFeedback('lenient');
                setFeedbackGiven(true);
                setTimeout(() => setShowFeedback(false), 3000);
              }}
              className="px-3 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg font-medium text-xs md:text-sm active:scale-95 md:hover:scale-105 transition-transform flex items-center justify-center gap-1.5"
            >
              <AlertCircle className="h-4 w-4" />
              <span>Too Lenient</span>
            </button>
          </div>
        </div>
      )}

      {/* Feedback Success Message */}
      {feedbackGiven && showFeedback && (
        <div className="bg-green-500/20 border border-green-500/30 rounded-xl p-4 text-center">
          <p className="text-sm md:text-base text-green-100 font-medium">
            ✅ Thank you! Your feedback helps improve our AI accuracy.
          </p>
        </div>
      )}
    </div>
  );
}

// Helper Components - Mobile optimized
function PhaseCard({ title, score, icon, details }: { title: string; score: number; icon: string; details: string[] }) {
  const percentage = Math.min(Math.max(score, 0), 100);
  
  let barColor = 'from-green-400 to-emerald-500';
  let bgColor = 'bg-green-500/10';
  let borderColor = 'border-green-500/30';
  
  if (percentage > 70) {
    barColor = 'from-red-400 to-rose-500';
    bgColor = 'bg-red-500/10';
    borderColor = 'border-red-500/30';
  } else if (percentage > 40) {
    barColor = 'from-yellow-400 to-amber-500';
    bgColor = 'bg-yellow-500/10';
    borderColor = 'border-yellow-500/30';
  }
  
  return (
    <div className={`p-3 md:p-4 ${bgColor} border ${borderColor} rounded-lg`}>
      <div className="flex items-start gap-2 md:gap-3 mb-2">
        <span className="text-lg md:text-xl shrink-0">{icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-xs md:text-sm font-semibold text-orange-100 mb-1">{title}</div>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-black/20 rounded-full h-1.5 md:h-2 overflow-hidden">
              <div 
                className={`h-full rounded-full bg-gradient-to-r ${barColor} transition-all duration-500`}
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="text-xs md:text-sm font-bold text-orange-200 tabular-nums shrink-0">
              {percentage.toFixed(0)}%
            </span>
          </div>
          {details && details.length > 0 && (
            <div className="mt-2 space-y-0.5">
              {details.map((detail, idx) => (
                <div key={idx} className="text-[10px] md:text-xs text-orange-100/60">
                  {detail}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreMeter({ label, score, description }: { label: string; score: number; description?: string }) {
  const percentage = Math.min(Math.max(score, 0), 100);
  
  let barColor = 'bg-gradient-to-r from-green-400 to-emerald-500';
  if (percentage > 70) {
    barColor = 'bg-gradient-to-r from-red-400 to-rose-500';
  } else if (percentage > 40) {
    barColor = 'bg-gradient-to-r from-yellow-400 to-amber-500';
  }
  
  return (
    <div className="p-3 bg-white/5 rounded-lg border border-orange-500/20">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-orange-100">{label}</span>
        <span className="text-xs font-bold text-orange-200 tabular-nums">{percentage.toFixed(1)}%</span>
      </div>
      <div className="bg-black/20 rounded-full h-2 overflow-hidden mb-1">
        <div 
          className={`h-full rounded-full transition-all duration-1000 ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {description && (
        <p className="text-xs text-orange-100/60 mt-1">{description}</p>
      )}
    </div>
  );
}
function Section({ 
  title, 
  icon, 
  children, 
  gradient = "from-white/5 to-white/10",
  borderColor = "border-orange-500/20"
}: { 
  title: string; 
  icon?: React.ReactNode; 
  children: React.ReactNode;
  gradient?: string;
  borderColor?: string;
}) {
  return (
    <div className={`bg-gradient-to-br ${gradient} border ${borderColor} rounded-xl p-3 md:p-6 backdrop-blur-sm`}>
      <div className="flex items-center gap-2 mb-3 md:mb-4">
        <div className="shrink-0">{icon}</div>
        <h3 className="text-base md:text-lg font-bold text-orange-100">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function CollapsibleSection({
  title,
  icon,
  children,
  gradient = "from-white/5 to-white/10",
  borderColor = "border-orange-500/20",
  isExpanded,
  onToggle
}: {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  gradient?: string;
  borderColor?: string;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <div className={`bg-gradient-to-br ${gradient} border ${borderColor} rounded-xl backdrop-blur-sm overflow-hidden`}>
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 md:p-6 active:bg-white/8 md:hover:bg-white/5 transition-all"
      >
        <div className="flex items-center gap-2">
          <div className="shrink-0">{icon}</div>
          <h3 className="text-sm md:text-lg font-bold text-orange-100 text-left">{title}</h3>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 md:h-5 md:w-5 text-orange-100/60 shrink-0" />
        ) : (
          <ChevronDown className="h-4 w-4 md:h-5 md:w-5 text-orange-100/60 shrink-0" />
        )}
      </button>
      {isExpanded && (
        <div className="px-3 md:px-6 pb-3 md:pb-6 text-sm md:text-base">
          {children}
        </div>
      )}
    </div>
  );
}
