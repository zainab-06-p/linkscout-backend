"use client" 

import * as React from "react"
import { useState, useEffect, useRef } from "react";
import { Lightbulb, Mic, Globe, Paperclip, Send } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
 
const PLACEHOLDERS = [
  "Generate website with HextaUI",
  "Create a new project with Next.js",
  "What is the meaning of life?",
  "What is the best way to learn React?",
  "How to cook a delicious meal?",
  "Summarize this article",
];

interface AIChatInputProps {
  onSubmit?: (message: string) => void;
  onFocus?: () => void;
  autoFocus?: boolean;
}

const AIChatInput = ({ onSubmit, onFocus, autoFocus = false }: AIChatInputProps = {}) => {
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [showPlaceholder, setShowPlaceholder] = useState(true);
  const [isActive, setIsActive] = useState(false);
  const [thinkActive, setThinkActive] = useState(false);
  const [deepSearchActive, setDeepSearchActive] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
 
  // Cycle placeholder text when input is inactive
  useEffect(() => {
    if (isActive || inputValue) return;
 
    const interval = setInterval(() => {
      setShowPlaceholder(false);
      setTimeout(() => {
        setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDERS.length);
        setShowPlaceholder(true);
      }, 400);
    }, 3000);
 
    return () => clearInterval(interval);
  }, [isActive, inputValue]);
 
  // Close input when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        if (!inputValue) setIsActive(false);
      }
    };
 
    document.addEventListener("mousedown", handleClickOutside as EventListener);
    return () => document.removeEventListener("mousedown", handleClickOutside as EventListener);
  }, [inputValue]);
 
  const handleActivate = () => setIsActive(true);
  // notify parent when input is focused/activated
  const handleActivateWithCallback = () => {
    setIsActive(true);
    if (onFocus) onFocus();
  };

  // auto-focus when requested
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      try {
        inputRef.current.focus();
      } catch (e) {}
    }
  }, [autoFocus]);

  const handleSubmit = () => {
    if (inputValue.trim() && onSubmit) {
      onSubmit(inputValue.trim());
      setInputValue("");
      setIsActive(false);
    }
  };

  // small ripple effect for send button
  const createRipple = (e: React.MouseEvent) => {
    const button = e.currentTarget as HTMLButtonElement;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.nativeEvent.offsetX - radius}px`;
    circle.style.top = `${e.nativeEvent.offsetY - radius}px`;
    circle.className = 'ls-ripple';
    const ripple = button.getElementsByClassName('ls-ripple')[0];
    if (ripple) ripple.remove();
    button.appendChild(circle);
    setTimeout(() => circle.remove(), 500);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };
 
  const containerVariants: any = {
    collapsed: {
      height: 68,
      boxShadow: "0 2px 8px 0 rgba(0,0,0,0.08)",
      transition: { type: "spring", stiffness: 120, damping: 18 },
    },
    expanded: {
      height: 128,
      boxShadow: "0 8px 32px 0 rgba(0,0,0,0.16)",
      transition: { type: "spring", stiffness: 120, damping: 18 },
    },
  };
 
  const placeholderContainerVariants: any = {
    initial: {},
    animate: { transition: { staggerChildren: 0.025 } },
    exit: { transition: { staggerChildren: 0.015, staggerDirection: -1 } },
  };
 
  const letterVariants: any = {
    initial: {
      opacity: 0,
      filter: "blur(12px)",
      y: 10,
    },
    animate: {
      opacity: 1,
      filter: "blur(0px)",
      y: 0,
      transition: {
        opacity: { duration: 0.25 },
        filter: { duration: 0.4 },
        y: { type: "spring", stiffness: 80, damping: 20 },
      },
    },
    exit: {
      opacity: 0,
      filter: "blur(12px)",
      y: -10,
      transition: {
        opacity: { duration: 0.2 },
        filter: { duration: 0.3 },
        y: { type: "spring", stiffness: 80, damping: 20 },
      },
    },
  };
 
  return (
    <div className="w-full">
      <motion.div
        ref={wrapperRef}
        className="w-full max-w-3xl mx-auto"
        variants={containerVariants}
        animate={isActive || inputValue ? "expanded" : "collapsed"}
        initial="collapsed"
        style={{ overflow: "hidden", borderRadius: 32, background: "#fff" }}
        onClick={handleActivateWithCallback}
      >
        <div className="flex flex-col items-stretch w-full h-full">
          {/* Input Row */}
          <div className="flex items-center gap-2 p-2 md:p-3 rounded-full bg-white w-full shadow-sm md:shadow-md transition-shadow" aria-hidden={false}>
            <button
              className="p-2 md:p-3 rounded-full hover:bg-gray-100 transition shrink-0"
              title="Attach file"
              type="button"
              tabIndex={-1}
              aria-label="Attach file"
            >
              <Paperclip size={18} className="md:w-5 md:h-5" />
            </button>
 
            {/* Text Input & Placeholder */}
            <div className="relative flex-1 min-w-0">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-1 border-0 outline-0 rounded-md py-2 text-sm md:text-base bg-transparent w-full font-normal relative z-10"
                onFocus={handleActivateWithCallback}
                ref={inputRef}
                autoComplete="off"
                aria-label="Message input"
                aria-describedby="ls-chat-input-hint"
              />
              <div className="absolute left-0 top-0 w-full h-full pointer-events-none flex items-center px-3 py-2 z-0">
                <AnimatePresence mode="wait">
                  {showPlaceholder && !isActive && !inputValue && (
                    <motion.span
                      key={placeholderIndex}
                      className="absolute left-0 top-1/2 -translate-y-1/2 text-gray-400 select-none pointer-events-none text-sm md:text-base"
                      style={{
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        zIndex: 0,
                      }}
                      variants={placeholderContainerVariants}
                      initial="initial"
                      animate="animate"
                      exit="exit"
                    >
                      {PLACEHOLDERS[placeholderIndex]
                        .split("")
                        .map((char, i) => (
                          <motion.span
                            key={i}
                            variants={letterVariants}
                            style={{ display: "inline-block" }}
                          >
                            {char === " " ? "\u00A0" : char}
                          </motion.span>
                        ))}
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            </div>
 
            <button
              className="p-2 md:p-3 rounded-full hover:bg-gray-100 transition shrink-0"
              title="Voice input"
              type="button"
              tabIndex={-1}
            >
              <Mic size={18} className="md:w-5 md:h-5" />
            </button>
            <button
              className="relative overflow-hidden flex items-center gap-1 bg-black hover:bg-zinc-700 text-white p-2 md:p-3 rounded-full font-medium justify-center shrink-0 shadow"
              title="Send"
              type="button"
              tabIndex={0}
              aria-label="Send message"
              onClick={(e) => {
                createRipple(e as React.MouseEvent);
                handleSubmit();
              }}
            >
              <Send size={16} className="md:w-[18px] md:h-[18px]" />
            </button>
          </div>
 
          {/* Expanded Controls */}
          <motion.div
            className="w-full flex justify-start px-3 md:px-4 items-center text-xs md:text-sm"
            variants={{
              hidden: {
                opacity: 0,
                y: 20,
                pointerEvents: "none" as const,
                transition: { duration: 0.25 },
              },
              visible: {
                opacity: 1,
                y: 0,
                pointerEvents: "auto" as const,
                transition: { duration: 0.35, delay: 0.08 },
              },
            }}
            initial="hidden"
            animate={isActive || inputValue ? "visible" : "hidden"}
            style={{ marginTop: 8 }}
          >
              <div className="flex gap-2 md:gap-3 items-center">
              {/* Think Toggle */}
              <button
                className={`flex items-center gap-1 px-3 md:px-4 py-1.5 md:py-2 rounded-full transition-all font-medium group text-xs md:text-sm ${
                  thinkActive
                    ? "bg-blue-600/10 outline outline-blue-600/60 text-blue-950"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
                title="Think"
                type="button"
                onClick={(e: React.MouseEvent) => {
                  e.stopPropagation();
                  setThinkActive((a) => !a);
                }}
                aria-pressed={thinkActive}
              >
                <Lightbulb
                  className="group-hover:fill-yellow-300 transition-all w-4 h-4 md:w-[18px] md:h-[18px]"
                />
                Think
              </button>
 
              {/* Deep Search Toggle */}
              <motion.button
                className={`flex items-center px-3 md:px-4 gap-1 py-1.5 md:py-2 rounded-full transition font-medium whitespace-nowrap overflow-hidden justify-start text-xs md:text-sm ${
                  deepSearchActive
                    ? "bg-blue-600/10 outline outline-blue-600/60 text-blue-950"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
                title="Deep Search"
                type="button"
                onClick={(e: React.MouseEvent) => {
                  e.stopPropagation();
                  setDeepSearchActive((a) => !a);
                }}
                initial={false}
                animate={{
                  width: deepSearchActive ? 125 : 36,
                  paddingLeft: deepSearchActive ? 8 : 9,
                }}
                aria-pressed={deepSearchActive}
              >
                <div className="flex-1">
                  <Globe size={16} className="md:w-[18px] md:h-[18px]" />
                </div>
                <motion.span
                className="pb-0.5"
                  initial={false}
                  animate={{
                    opacity: deepSearchActive ? 1 : 0,
                  }}
                >
                  Deep Search
                </motion.span>
              </motion.button>
            </div>
          </motion.div>

          {/* Keyboard hint (visually small, accessible) */}
          <div id="ls-chat-input-hint" className="sr-only">
            Press Enter to send, Shift+Enter for newline.
          </div>
        </div>
      </motion.div>
    </div>
  );
};
 
export { AIChatInput };
