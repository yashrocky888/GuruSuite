import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import "../styles/globals.css";
import StartupDiagnostics from "@/components/StartupDiagnostics";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GURU - Your Spiritual Guide for Vedic Astrology",
  description: "Discover your cosmic blueprint with Vedic astrology insights, predictions, and spiritual guidance",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Startup diagnostics (server-side)
  if (typeof window === 'undefined') {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://guru-api-660206747784.asia-south1.run.app/api/v1';
    console.log('🚀 Guru Web starting...');
    console.log(`📡 API Base URL: ${apiUrl}`);
  }
  
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <StartupDiagnostics />
        {children}
      </body>
    </html>
  );
}
