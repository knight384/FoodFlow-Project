import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep charcoal background
        background: "#0a0a0a",
        // Slightly lighter charcoal for surfaces
        surface: "#171717",
        surfaceHighlight: "#262626",
        // Neutral gray for borders
        border: "#2d2d2d",
        // Text colors
        textPrimary: "#f5f5f5",
        textSecondary: "#a3a3a3",
        // Restrained accent color (e.g. muted blue-gray or subtle primary)
        accent: "#3b82f6", // we can keep a very muted version or just standard tailwind blue as accent, but user said "ONE restrained operational accent color". Let's use a muted blue-gray or slate-blue.
        accentHover: "#2563eb",
        // Status colors
        statusSurplus: "#10b981", // green
        statusShortage: "#ef4444", // red
        statusBalanced: "#f59e0b", // amber/neutral
        statusUnavailable: "#737373", // gray
        statusAdvisory: "#d97706", // restrained amber
      },
    },
  },
  plugins: [],
};

export default config;
