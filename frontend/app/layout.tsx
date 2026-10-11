import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Plus_Jakarta_Sans } from "next/font/google";

import { Providers } from "@/components/providers";
import { brand } from "@/lib/brand";

import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://project-bf77a013-c0b3-413c-a75.web.app";

export const metadata: Metadata = {
  title: `${brand.name} | Healthcare knowledge workspace`,
  description: brand.description,
  metadataBase: new URL(siteUrl),
  openGraph: {
    title: `${brand.name} | Healthcare knowledge workspace`,
    description: brand.description,
    siteName: brand.name,
    type: "website",
    url: siteUrl,
    images: [{ url: "/images/hero-clinician.jpg", width: 1200, height: 630, alt: brand.name }],
  },
  twitter: {
    card: "summary_large_image",
    title: brand.name,
    description: brand.description,
    images: ["/images/hero-clinician.jpg"],
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${jakarta.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
