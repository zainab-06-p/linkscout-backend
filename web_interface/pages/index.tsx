"use client";
import React, { useState } from "react";
import Hero from "../components/ui/animated-shader-hero";
import { Sidebar } from "../components/ui/sidebar";
import { AIChatInput } from "../components/ui/ai-chat-input";
import { GooeyLoader } from "../components/ui/loader-10";

export default function HomePage() {
  const [started, setStarted] = useState(false);

  return (
    <div className="min-h-screen w-full">
      {!started ? (
        <Hero
          trustBadge={{ text: "Trusted by forward-thinking teams.", icons: ["✨"] }}
          headline={{ line1: "Launch Your", line2: "Workflow Into Orbit" }}
          subtitle={"Supercharge productivity with AI-powered automation and integrations built for the next generation of teams — fast, seamless, and limitless."}
          buttons={{
            primary: { text: "Get Started", onClick: () => setStarted(true) },
            secondary: { text: "Explore", onClick: () => console.log('explore') }
          }}
        />
      ) : (
        // Keep the shader background (Hero canvas remains mounted). Overlay the app UI.
        <div className="relative w-full h-screen">
          {/* Hero canvas still provides background visual */}
          <div className="absolute inset-0 pointer-events-none" />

          <div className="relative z-20 flex h-full">
            <Sidebar>
              {/* Sidebar content will be provided by children when used in pages/components */}
            </Sidebar>

            <main className="flex-1 p-6 flex flex-col gap-4">
              <div className="max-w-4xl w-full">
                <h1 className="text-2xl font-bold text-white">AI Chat</h1>
                <div className="mt-4">
                  <AIChatInput />
                </div>
              </div>
            </main>
          </div>
        </div>
      )}
    </div>
  );
}
