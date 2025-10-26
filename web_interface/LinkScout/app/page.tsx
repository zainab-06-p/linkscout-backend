"use client";
import React from "react";
import Hero from "@/components/ui/animated-shader-hero";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  const handleGetExtension = () => {
    // Redirect to extensions page where user can read instructions
    router.push('/extensions');
  };

  return (
    <Hero
      trustBadge={{ text: "Trusted by 10,000+ teams worldwide", icons: ["✨", "🚀", "⚡"] }}
      headline={{ 
        line1: "AI-Powered Link", 
        line2: "Intelligence Platform" 
      }}
      subtitle={"LinkScout revolutionizes how you discover, organize, and leverage web content. Our AI analyzes, categorizes, and provides intelligent insights on your links—making research effortless and knowledge management seamless."}
      buttons={{
        primary: { text: "Start Exploring", onClick: () => router.push('/search') },
        secondary: { 
          text: "Get Extension", 
          onClick: handleGetExtension 
        }
      }}
    />
  );
}
