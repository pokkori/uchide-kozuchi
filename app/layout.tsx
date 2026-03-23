import type { Metadata } from "next";
import "./globals.css";

const APP_URL = "https://uchide-kozuchi.vercel.app";

export const metadata: Metadata = {
  title: "打出の小槌AI - 願いを叶える5ステップ",
  description:
    "あなたの願い事を入力するだけ。AIが実現のための5つのステップを即座に提案します。夢を現実に変える魔法の槌、打出の小槌AIをお試しください。",
  keywords: ["願い事", "AI", "目標達成", "ステップ", "夢実現", "打出の小槌"],
  authors: [{ name: "ポッコリラボ" }],
  creator: "ポッコリラボ",
  publisher: "ポッコリラボ",
  metadataBase: new URL(APP_URL),
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: APP_URL,
    siteName: "打出の小槌AI",
    title: "打出の小槌AI - 願いを叶える5ステップ",
    description:
      "あなたの願い事を入力するだけ。AIが実現のための5つのステップを即座に提案します。",
    images: [
      {
        url: `${APP_URL}/og.png`,
        width: 1200,
        height: 630,
        alt: "打出の小槌AI - 願いを叶える5ステップ",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "打出の小槌AI - 願いを叶える5ステップ",
    description:
      "あなたの願い事を入力するだけ。AIが実現のための5つのステップを即座に提案します。",
    images: [`${APP_URL}/og.png`],
    creator: "@levona_design",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "打出の小槌AI",
  applicationCategory: "LifestyleApplication",
  operatingSystem: "Web",
  description:
    "あなたの願い事を入力するだけ。AIが実現のための5つのステップを即座に提案します。",
  url: APP_URL,
  author: {
    "@type": "Organization",
    name: "ポッコリラボ",
  },
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "JPY",
  },
  inLanguage: "ja",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
