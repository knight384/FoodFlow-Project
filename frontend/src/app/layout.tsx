import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "FoodFlow",
  description: "Food-Service Demand Forecasting and Surplus Redistribution System.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} font-sans`}>
      <body className="bg-background text-textPrimary antialiased selection:bg-accent/30 selection:text-textPrimary">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
