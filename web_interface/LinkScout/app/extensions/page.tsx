"use client";
import React from "react";
import { AppLayout } from "@/components/app-layout";
import { Download, Chrome, Zap, Shield, Sparkles, Check, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: <Zap className="h-6 w-6" />,
    title: "Smart Detection in 8 Ways",
    description: "Analyzes articles from multiple angles - checking the writing style, verifying facts, examining sources, identifying propaganda tactics, spotting contradictions, and detecting fake images"
  },
  {
    icon: <Shield className="h-6 w-6" />,
    title: "Instant Fact Verification",
    description: "Automatically checks claims against reliable sources and a database of known misinformation, giving you accurate results in seconds"
  },
  {
    icon: <Sparkles className="h-6 w-6" />,
    title: "Gets Smarter Over Time",
    description: "Uses advanced AI that learns from your feedback to become more accurate with every use, helping you spot fake news and misleading content"
  },
];

const browsers = [
  {
    name: "Chrome",
    icon: <Chrome className="h-8 w-8" />,
    downloadUrl: "#",
    supported: true
  },
  {
    name: "Firefox",
    icon: <Globe className="h-8 w-8" />,
    downloadUrl: "#",
    supported: true
  },
  {
    name: "Edge",
    icon: <Globe className="h-8 w-8" />,
    downloadUrl: "#",
    supported: true
  },
];

export default function ExtensionsPage() {
  const [isDownloading, setIsDownloading] = React.useState(false);
  const [downloadError, setDownloadError] = React.useState<string | null>(null);

  const handleDownloadExtension = async () => {
    try {
      setIsDownloading(true);
      setDownloadError(null);

      console.log('📥 Starting extension download...');

      // Fetch the extension ZIP file from the backend
      const response = await fetch('/api/download-extension', {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }

      // Get the blob data
      const blob = await response.blob();
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'linkscout-extension.zip';
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      console.log('✅ Extension downloaded successfully!');
      
      // Show success message
      alert('✅ Extension downloaded! Extract the ZIP file and follow the installation instructions below.');

    } catch (error) {
      console.error('❌ Download failed:', error);
      const errorMsg = error instanceof Error ? error.message : 'Download failed';
      setDownloadError(errorMsg);
      alert(`❌ ${errorMsg}\n\nPlease ensure the backend server is running on port 5000.`);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full overflow-y-auto">
        {/* Hero Section - Mobile optimized */}
        <div className="px-4 py-6 md:p-12 border-b border-orange-500/20 bg-black/30 backdrop-blur-sm">
          <div className="max-w-5xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 bg-orange-500/10 border border-orange-500/30 rounded-full text-orange-300 text-xs md:text-sm mb-4 md:mb-6">
              <Sparkles className="h-3 w-3 md:h-4 md:w-4" />
              <span>Browser Extension</span>
            </div>
            <h1 className="text-2xl md:text-5xl font-bold bg-linear-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent mb-3 md:mb-4 px-2">
              LinkScout Browser Extension
            </h1>
            <p className="text-sm md:text-xl text-orange-100/70 max-w-2xl mx-auto mb-6 md:mb-8 px-4">
              Transform your browsing experience with AI-powered search and insights, available right in your browser
            </p>
            <div className="flex flex-col sm:flex-row flex-wrap gap-3 md:gap-4 justify-center px-4">
              <Button 
                variant="primary" 
                onClick={handleDownloadExtension}
                disabled={isDownloading}
                className="w-full sm:w-auto whitespace-nowrap flex items-center justify-center"
              >
                {isDownloading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 md:h-5 md:w-5 border-b-2 border-white" />
                    <span className="ml-2 text-sm md:text-base">Downloading...</span>
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 md:h-5 md:w-5" />
                    <span className="ml-2 text-sm md:text-base">Download Extension</span>
                  </>
                )}
              </Button>
              <Button variant="secondary" className="w-full sm:w-auto text-sm md:text-base whitespace-nowrap flex items-center justify-center">
                View Demo
              </Button>
            </div>
            {downloadError && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-xs md:text-sm max-w-md mx-auto">
                ❌ {downloadError}
              </div>
            )}
          </div>
        </div>

        {/* Features Section - Mobile optimized */}
        <div className="px-4 py-6 md:p-12 border-b border-orange-500/20">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-xl md:text-3xl font-bold text-orange-100 text-center mb-6 md:mb-12">
              Why Use LinkScout Extension?
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6 hover:bg-white/10 hover:border-orange-500/40 active:bg-white/15 md:hover:bg-white/10 transition-all duration-300"
                >
                  <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg bg-linear-to-br from-orange-400 to-yellow-500 flex items-center justify-center mb-3 md:mb-4 text-white">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg md:text-xl font-semibold text-orange-100 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-orange-100/60 text-sm md:text-base">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Browser Support Section - Mobile optimized */}
        <div className="px-4 py-6 md:p-12">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-xl md:text-3xl font-bold text-orange-100 text-center mb-6 md:mb-12">
              Available For Your Browser
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
              {browsers.map((browser, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-6 md:p-8 hover:bg-white/10 hover:border-orange-500/40 active:bg-white/15 md:hover:bg-white/10 transition-all duration-300 flex flex-col items-center text-center"
                >
                  <div className="w-14 h-14 md:w-16 md:h-16 rounded-full bg-white/10 flex items-center justify-center mb-3 md:mb-4 text-orange-300">
                    {browser.icon}
                  </div>
                  <h3 className="text-lg md:text-xl font-semibold text-orange-100 mb-2">
                    {browser.name}
                  </h3>
                  {browser.supported ? (
                    <>
                      <div className="flex items-center gap-1 text-green-400 text-sm mb-3 md:mb-4">
                        <Check className="h-4 w-4" />
                        <span>Supported</span>
                      </div>
                      <button 
                        className="w-full px-4 md:px-6 py-2.5 md:py-3 bg-black/30 hover:bg-black/50 active:bg-black/60 md:hover:bg-black/50 border border-orange-500/30 hover:border-orange-500/50 text-orange-100 rounded-lg font-medium text-sm md:text-base transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={handleDownloadExtension}
                        disabled={isDownloading}
                      >
                        {isDownloading ? 'Downloading...' : `Install for ${browser.name}`}
                      </button>
                    </>
                  ) : (
                    <span className="text-orange-100/40 text-sm">Coming Soon</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Installation Steps - Mobile optimized */}
        <div className="px-4 py-6 md:p-12 border-t border-orange-500/20 bg-gradient-to-b from-black/20 to-transparent">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-xl md:text-3xl font-bold text-orange-100 text-center mb-2 md:mb-4">
              📦 How to Install the Extension
            </h2>
            <p className="text-sm md:text-base text-orange-100/60 text-center mb-6 md:mb-12 max-w-2xl mx-auto">
              Follow these simple steps to install LinkScout extension in your browser. The process takes less than 2 minutes!
            </p>
            
            <div className="space-y-3 md:space-y-6">
              {[
                {
                  title: "Download the Extension",
                  description: "Click the 'Download Extension' button above to download the ZIP file to your computer",
                  tip: "💡 Save it somewhere you can easily find it, like your Downloads folder"
                },
                {
                  title: "Extract the ZIP File",
                  description: "Right-click the downloaded ZIP file and select 'Extract All' or 'Extract Here'",
                  tip: "📁 This will create a folder named 'extension' containing all the extension files"
                },
                {
                  title: "Open Browser Extensions Page",
                  description: "Open your browser and navigate to:",
                  code: "chrome://extensions (Chrome) or edge://extensions (Edge)",
                  tip: "⌨️ You can copy and paste this directly into your browser's address bar"
                },
                {
                  title: "Enable Developer Mode",
                  description: "Find the 'Developer mode' toggle switch in the top right corner and turn it ON",
                  tip: "🔧 This allows you to load extensions that aren't from the Chrome Web Store"
                },
                {
                  title: "Load the Extension",
                  description: "Click the 'Load unpacked' button and select the folder you extracted in Step 2",
                  tip: "📂 Make sure to select the 'extension' folder, not the ZIP file"
                },
                {
                  title: "Pin to Toolbar (Optional)",
                  description: "Click the puzzle piece icon in your browser toolbar and pin LinkScout for easy access",
                  tip: "📌 This makes the extension icon always visible in your toolbar"
                },
                {
                  title: "Start Using LinkScout!",
                  description: "Click the LinkScout icon in your toolbar to start analyzing articles and detecting misinformation",
                  tip: "🎉 You're all set! Visit any news article and click the extension to analyze it"
                }
              ].map((step, index) => (
                <div
                  key={index}
                  className="flex gap-3 md:gap-4 items-start bg-white/5 backdrop-blur-sm border border-orange-500/20 rounded-xl p-4 md:p-6 hover:bg-white/8 hover:border-orange-500/30 transition-all duration-300"
                >
                  <div className="shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full bg-gradient-to-br from-orange-500 to-yellow-500 flex items-center justify-center text-white font-bold text-sm md:text-lg shadow-lg">
                    {index + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base md:text-xl font-bold text-orange-100 mb-1.5 md:mb-2">
                      {step.title}
                    </h3>
                    <p className="text-sm md:text-base text-orange-100/80 mb-2 leading-relaxed">
                      {step.description}
                    </p>
                    {step.code && (
                      <div className="bg-black/40 border border-orange-500/30 rounded-lg p-2.5 md:p-3 mb-2">
                        <code className="text-xs md:text-sm text-orange-300 font-mono">
                          {step.code}
                        </code>
                      </div>
                    )}
                    <div className="text-xs md:text-sm text-yellow-300/80 flex items-start gap-1.5">
                      <span className="shrink-0">{step.tip.split(' ')[0]}</span>
                      <span>{step.tip.substring(step.tip.indexOf(' ') + 1)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Troubleshooting Section */}
            <div className="mt-8 md:mt-12 bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-orange-500/30 rounded-xl p-4 md:p-6">
              <h3 className="text-lg md:text-2xl font-bold text-orange-100 mb-3 md:mb-4 flex items-center gap-2">
                <span>🔧</span>
                <span>Troubleshooting</span>
              </h3>
              <div className="space-y-3 md:space-y-4">
                <div>
                  <p className="text-sm md:text-base font-semibold text-orange-100 mb-1">
                    Can't find "Load unpacked" button?
                  </p>
                  <p className="text-xs md:text-sm text-orange-100/70">
                    Make sure Developer Mode is enabled (toggle in top right corner)
                  </p>
                </div>
                <div>
                  <p className="text-sm md:text-base font-semibold text-orange-100 mb-1">
                    Extension not working after installation?
                  </p>
                  <p className="text-xs md:text-sm text-orange-100/70">
                    Refresh the page you want to analyze, then click the extension icon
                  </p>
                </div>
                <div>
                  <p className="text-sm md:text-base font-semibold text-orange-100 mb-1">
                    Need help?
                  </p>
                  <p className="text-xs md:text-sm text-orange-100/70">
                    Contact us at support@linkscout.ai or visit our help center
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

