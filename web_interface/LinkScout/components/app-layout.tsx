"use client";
import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShaderBackground } from "./ui/shader-background";
import { Sidebar, SidebarBody, SidebarLink } from "./ui/sidebar";
import { 
  Home, 
  Search, 
  History, 
  Settings, 
  Download,
  Sparkles,
  Menu
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AppLayoutProps {
  children: React.ReactNode;
  showHero?: boolean;
}

export function AppLayout({ children, showHero = false }: AppLayoutProps) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  const links = [
    {
      label: "Home",
      href: "/",
      icon: <Home className="h-5 w-5 shrink-0" />,
    },
    {
      label: "Search",
      href: "/search",
      icon: <Search className="h-5 w-5 shrink-0" />,
    },
    {
      label: "History",
      href: "/history",
      icon: <History className="h-5 w-5 shrink-0" />,
    },
    {
      label: "Extensions",
      href: "/extensions",
      icon: <Download className="h-5 w-5 shrink-0" />,
    },
    {
      label: "Settings",
      href: "/settings",
      icon: <Settings className="h-5 w-5 shrink-0" />,
    },
  ];

  return (
    <div className="relative w-full h-screen overflow-hidden">
      <ShaderBackground 
        blur={!showHero} 
        overlay={!showHero}
        overlayOpacity={0.8}
      >
        <div className="flex flex-col md:flex-row w-full h-full">
          {/* Sidebar */}
          <Sidebar open={open} setOpen={setOpen}>
            <SidebarBody className="justify-between gap-6 md:gap-10">
              <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
                <div className="hidden md:block">
                  {open ? <Logo /> : <LogoIcon />}
                </div>
                <div className="mt-4 md:mt-8 flex flex-col gap-2">
                  {links.map((link, idx) => (
                    <SidebarLink 
                      key={idx} 
                      link={link}
                      className={cn(
                        pathname === link.href && "bg-orange-500/20 text-orange-300 border-orange-500/40"
                      )}
                    />
                  ))}
                </div>
              </div>
              <div>
                <SidebarLink
                  link={{
                    label: "LinkScout AI",
                    href: "#",
                    icon: (
                      <div className="h-7 w-7 shrink-0 rounded-full bg-linear-to-br from-orange-400 to-yellow-500 flex items-center justify-center">
                        <Sparkles className="h-4 w-4 text-black" />
                      </div>
                    ),
                  }}
                />
              </div>
            </SidebarBody>
          </Sidebar>

          {/* Main Content - Now properly positioned for mobile */}
          <main className="flex-1 overflow-y-auto overflow-x-hidden w-full">
            {children}
          </main>
        </div>
      </ShaderBackground>
    </div>
  );
}

const Logo = () => {
  return (
    <Link
      href="/"
      className="relative z-20 flex items-center space-x-2 py-1 text-sm font-semibold text-white"
    >
      <div className="h-6 w-6 shrink-0 rounded-md bg-linear-to-br from-orange-400 to-yellow-500 flex items-center justify-center">
        <Sparkles className="h-4 w-4 text-black" />
      </div>
      <span className="font-bold text-lg bg-linear-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent">
        LinkScout
      </span>
    </Link>
  );
};

const LogoIcon = () => {
  return (
    <Link
      href="/"
      className="relative z-20 flex items-center space-x-2 py-1 text-sm font-semibold text-white"
    >
      <div className="h-6 w-6 shrink-0 rounded-md bg-linear-to-br from-orange-400 to-yellow-500 flex items-center justify-center">
        <Sparkles className="h-4 w-4 text-black" />
      </div>
    </Link>
  );
};
