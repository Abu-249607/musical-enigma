import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Status colors for order tracking
        status: {
          neutral: "#e5e7eb", // gray-200
          yellow: "#fbbf24", // amber-400
          red: "#ef4444", // red-500
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
