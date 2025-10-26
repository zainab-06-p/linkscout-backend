"use client";

import { cn } from "@/lib/utils";
import Link, { LinkProps } from "next/link";
import React, { useState, createContext, useContext } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, X } from "lucide-react";

interface Links {
  label: string;
  href: string;
  icon: React.JSX.Element | React.ReactNode;
}

interface SidebarContextProps {
  open: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  animate: boolean;
}

const SidebarContext = createContext<SidebarContextProps | undefined>(
  undefined
);

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider");
  }
  return context;
};

export const SidebarProvider = ({
  children,
  open: openProp,
  setOpen: setOpenProp,
  animate = true,
}: {
  children?: React.ReactNode;
  open?: boolean;
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  animate?: boolean;
}) => {
  const [openState, setOpenState] = useState(false);

  const open = openProp !== undefined ? openProp : openState;
  const setOpen = setOpenProp !== undefined ? setOpenProp : setOpenState;

  return (
    <SidebarContext.Provider value={{ open, setOpen, animate }}>
      {children}
    </SidebarContext.Provider>
  );
};

export const Sidebar = ({
  children,
  open,
  setOpen,
  animate,
}: {
  children?: React.ReactNode;
  open?: boolean;
  setOpen?: React.Dispatch<React.SetStateAction<boolean>>;
  animate?: boolean;
}) => {
  return (
    <SidebarProvider open={open} setOpen={setOpen} animate={animate}>
      {children}
    </SidebarProvider>
  );
};

export const SidebarBody = (props: React.ComponentProps<"div">) => {
  return (
    <>
      <DesktopSidebar {...props} />
      <MobileSidebar {...props} />
    </>
  );
};

export const DesktopSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<"div">) => {
  return (
    <div
      className={cn(
        "h-full px-4 py-4 hidden md:flex md:flex-col bg-black/20 backdrop-blur-md border-r border-orange-500/20 w-[280px] shrink-0 overflow-y-auto",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const MobileSidebar = ({
  className,
  children,
  ...props
}: React.ComponentProps<"div">) => {
  const { open, setOpen } = useSidebar();
  return (
    <>
      {/* Mobile Header - Always visible */}
      <div
        className={cn(
          "h-14 px-4 flex flex-row md:hidden items-center justify-between bg-black/40 backdrop-blur-md border-b border-orange-500/20 w-full shrink-0"
        )}
        {...props}
      >
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 shrink-0 rounded-md bg-linear-to-br from-orange-400 to-yellow-500 flex items-center justify-center">
            <div className="h-3 w-3 text-black">✨</div>
          </div>
          <span className="font-bold text-sm bg-linear-to-r from-orange-300 to-yellow-300 bg-clip-text text-transparent">
            LinkScout
          </span>
        </div>
        <button
          onClick={() => setOpen(!open)}
          className="p-2 rounded-lg hover:bg-white/10 active:bg-white/20 transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="h-5 w-5 text-orange-200" />
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {open && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9998] md:hidden"
              onClick={() => setOpen(false)}
            />
            
            {/* Sidebar Panel */}
            <motion.div
              initial={{ x: "-100%", opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: "-100%", opacity: 0 }}
              transition={{
                duration: 0.3,
                ease: "easeInOut",
              }}
              className={cn(
                "fixed top-0 left-0 h-full w-[280px] bg-gradient-to-br from-black via-black/95 to-orange-950/20 backdrop-blur-xl border-r border-orange-500/30 p-6 z-[9999] flex flex-col justify-between overflow-y-auto",
                className
              )}
            >
              {/* Close button */}
              <button
                className="absolute right-4 top-4 p-2 rounded-lg hover:bg-white/10 active:bg-white/20 transition-colors"
                onClick={() => setOpen(false)}
                aria-label="Close menu"
              >
                <X className="h-5 w-5 text-orange-200" />
              </button>
              
              {/* Menu content */}
              <div className="pt-12">
                {children}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export const SidebarLink = ({
  link,
  className,
  ...props
}: {
  link: Links;
  className?: string;
  props?: LinkProps;
}) => {
  const { open, setOpen } = useSidebar();
  
  return (
    <Link
      href={link.href}
      onClick={() => {
        // Close mobile menu when clicking a link
        if (open) {
          setOpen(false);
        }
      }}
      className={cn(
        "flex items-center gap-3 group/sidebar py-3 px-3 rounded-lg transition-all duration-200 hover:bg-white/10 active:bg-white/20 md:hover:bg-white/5 md:hover:backdrop-blur-sm hover:border-orange-500/30 active:border-orange-500/50 border border-transparent text-orange-100/80 hover:text-orange-100",
        className
      )}
      {...props}
    >
      <div className="transition-transform duration-200 group-hover/sidebar:scale-110 shrink-0 text-orange-300">
        {link.icon}
      </div>
      <span className="text-sm md:text-sm group-hover/sidebar:translate-x-1 transition duration-150 whitespace-pre font-medium">
        {link.label}
      </span>
    </Link>
  );
};
