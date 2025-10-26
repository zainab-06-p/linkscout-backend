# UI Components (shadcn-friendly)

This folder contains four UI components taken from 21st.dev templates and prepared for a shadcn/Tailwind/TypeScript Next.js project:

- `animated-shader-hero.tsx` — full-screen animated WebGL shader hero
- `sidebar.tsx` — responsive animated sidebar (framer-motion)
- `ai-chat-input.tsx` — animated AI chat input with placeholder cycling
- `loader-10.tsx` — gooey loader

Also provided: small demo pages `demo-*.tsx` showing usage.

Important notes before using
1. These files assume a standard shadcn structure (Next.js with `components/ui` folder). If your project doesn't use `@/` path aliases, adjust imports accordingly.
2. The helper `cn` function is imported from `@/lib/utils`. If you don't have it, create a small utility:

```ts
// lib/utils.ts
export function cn(...args: Array<string | false | null | undefined>) {
  return args.filter(Boolean).join(' ');
}
```

Required NPM packages
- framer-motion
- lucide-react
- motion (for `motion/react` used in ai-chat-input) OR replace with `framer-motion` motion

Suggested install (run in your project root, PowerShell):

```powershell
npm install framer-motion lucide-react
# If you want the motion/react API used above, install `motion` (but framer-motion can be used instead)
npm install motion
```

Tailwind / shadcn / TypeScript setup
1. If you do not have a project scaffolded, follow shadcn CLI to create the base UI system. From your project root:

```powershell
npx shadcn@latest init
# or to add specific components:
npx shadcn@latest add https://21st.dev/r/ravikatiyar162/animated-shader-hero
npx shadcn@latest add https://21st.dev/r/aceternity/sidebar
npx shadcn@latest add https://21st.dev/r/preetsuthar17/ai-chat-input
npx shadcn@latest add https://21st.dev/r/ravikatiyar162/loader-10
```

2. Tailwind: if not present, install Tailwind CSS and configure with Next.js — follow the official Tailwind docs: https://tailwindcss.com/docs/guides/nextjs

3. TypeScript: `npm install -D typescript @types/react @types/node` and add `tsconfig.json`.

Default component path
- shadcn tends to use `components/ui` for reusable UI primitives. If your project places components elsewhere, create `components/ui` and keep these files there — it helps keep shadcn components discoverable and consistent with the rest of the ecosystem and the shadcn CLI.

Assets
- I used an Unsplash image URL in the sidebar demo. Replace with your preferred images.

Next steps I can do for you
1. Wire these components into your Next.js pages (index page with hero -> chat sidebar layout).
2. Replace `motion/react` usage with `framer-motion` for consistency.
3. Run a local dev build and fix any TypeScript errors.
