import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "特定商取引法に基づく表記 | 打出の小槌AI",
  description: "打出の小槌AIの特定商取引法に基づく表記です。",
};

const legalItems = [
  { label: "販売事業者", value: "ポッコリラボ" },
  { label: "運営責任者", value: "非公開（問い合わせ窓口からご連絡ください）" },
  { label: "所在地", value: "非公開（問い合わせ窓口からご連絡ください）" },
  { label: "電話番号", value: "非公開（お問い合わせいただいた場合は遅滞なく開示いたします）" },
  {
    label: "連絡先",
    value: "X（旧Twitter）: @levona_design",
    link: "https://twitter.com/levona_design",
    linkLabel: "ポッコリラボのX（旧Twitter）アカウント",
  },
  { label: "サービス名", value: "打出の小槌AI" },
  { label: "サービスURL", value: "https://uchide-kozuchi.vercel.app" },
  {
    label: "提供するサービス",
    value: "AIを活用した願い事実現ステップ提案サービス",
  },
  {
    label: "料金",
    value: "無料（現時点では有料サービスはありません）",
  },
  {
    label: "支払方法",
    value: "現時点では有料サービスはございません",
  },
  {
    label: "サービスの提供時期",
    value: "ご利用登録後、即時ご利用いただけます",
  },
  {
    label: "返品・キャンセル",
    value:
      "デジタルコンテンツのため、提供開始後の返品・キャンセルはお受けできません（現在無料サービスのみ）",
  },
  {
    label: "動作環境",
    value:
      "インターネット接続環境、モダンWebブラウザ（Chrome, Safari, Firefox, Edge 最新版推奨）",
  },
];

export default function LegalPage() {
  return (
    <main className="min-h-screen py-12 px-4" style={{ backgroundColor: "#1a1208" }}>
      <div className="max-w-2xl mx-auto">
        <div
          className="rounded-2xl p-8"
          style={{
            backdropFilter: "blur(12px)",
            backgroundColor: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          <h1
            className="text-2xl font-bold mb-8"
            style={{
              background: "linear-gradient(90deg, #f59e0b, #fcd34d)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            特定商取引法に基づく表記
          </h1>

          <div className="space-y-4">
            {legalItems.map(({ label, value, link, linkLabel }) => (
              <div
                key={label}
                className="border-b border-white/10 pb-4 last:border-0"
              >
                <dt className="text-amber-300 text-xs font-semibold uppercase tracking-wider mb-1">
                  {label}
                </dt>
                <dd className="text-gray-300 text-sm leading-relaxed">
                  {link ? (
                    <>
                      <span>{value.split(":")[0]}: </span>
                      <a
                        href={link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-amber-400 hover:underline"
                        aria-label={linkLabel}
                      >
                        {value.split(":")[1]?.trim()}
                      </a>
                    </>
                  ) : (
                    value
                  )}
                </dd>
              </div>
            ))}
          </div>

          <p className="text-gray-500 text-xs mt-8 pt-4 border-t border-white/10">
            本表記は、特定商取引に関する法律第11条に基づき表示しています。
          </p>

          <div className="mt-8">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-amber-400 hover:text-amber-300 transition-colors text-sm"
              aria-label="トップページに戻る"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <path
                  d="M10 3L5 8L10 13"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              トップページに戻る
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
