"use client";
import React from "react";
import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

const variants: Record<string, string> = {
  primary:
    "px-6 py-3 md:px-8 md:py-4 bg-linear-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white rounded-full font-semibold text-base md:text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-orange-500/25",
  secondary:
    "px-6 py-3 md:px-8 md:py-4 bg-white/10 hover:bg-white/20 border border-orange-300/30 hover:border-orange-300/50 text-orange-100 rounded-full font-semibold text-base md:text-lg transition-all duration-300 hover:scale-105 backdrop-blur-sm",
  ghost:
    "px-3 py-2 text-sm text-orange-100/70 hover:text-orange-100 hover:bg-white/5 rounded-md transition",
};

export const Button: React.FC<ButtonProps> = ({ variant = "primary", className, children, ...props }) => {
  return (
    <button className={cn(variants[variant], className)} {...props}>
      {children}
    </button>
  );
};

export default Button;
