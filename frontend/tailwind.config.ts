import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    // CRITICAL FIX: Point to the "src" folder where your code lives now
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // CRITICAL FIX: This satisfies the "border-border" error
        border: "hsl(var(--border))", 
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
      },
    },
  },
  plugins: [],
};
export default config;

