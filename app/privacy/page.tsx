import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "プライバシーポリシー | 打出の小槌AI",
  description: "打出の小槌AIのプライバシーポリシーです。",
};

export default function PrivacyPage() {
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
            プライバシーポリシー
          </h1>

          <div className="text-gray-300 space-y-6 text-sm leading-relaxed">
            <section>
              <h2 className="text-amber-300 font-semibold mb-2">1. 基本方針</h2>
              <p>
                ポッコリラボ（以下「当サービス」）は、利用者のプライバシーを尊重し、個人情報の保護に努めます。本プライバシーポリシーは、打出の小槌AI（以下「本サービス」）における個人情報の取り扱いについて定めるものです。
              </p>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">2. 収集する情報</h2>
              <p>本サービスでは以下の情報を収集する場合があります。</p>
              <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                <li>入力された願い事のテキスト（AI処理のためのみ使用。保存しません）</li>
                <li>アクセスログ（IPアドレス、ブラウザ情報、アクセス日時）</li>
                <li>ブラウザのlocalStorageに保存される連続利用日数データ（端末上のみ）</li>
              </ul>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">3. 情報の利用目的</h2>
              <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                <li>サービスの提供・改善</li>
                <li>不正利用の防止</li>
                <li>サービスの利用状況の分析</li>
              </ul>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">4. 第三者提供</h2>
              <p>
                当サービスは、法令に基づく場合を除き、利用者の個人情報を第三者に提供しません。ただし、AI処理のためにAnthropicのAPIを使用しており、入力テキストはAnthropicのサーバーに送信されます。詳細はAnthropicのプライバシーポリシーをご確認ください。
              </p>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">5. Cookieの使用</h2>
              <p>
                本サービスは、サービス改善のためにGoogle Analyticsを使用する場合があります。Cookieを無効にすることで、情報収集を拒否することができます。
              </p>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">6. セキュリティ</h2>
              <p>
                当サービスは、個人情報の漏洩・紛失・改ざんを防ぐため、適切なセキュリティ対策を実施しています。
              </p>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">7. お問い合わせ</h2>
              <p>
                プライバシーポリシーに関するお問い合わせは、X（旧Twitter）の
                <a
                  href="https://twitter.com/levona_design"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-amber-400 hover:underline ml-1"
                  aria-label="ポッコリラボのXアカウント（新しいタブで開きます）"
                >
                  @levona_design
                </a>
                までご連絡ください。
              </p>
            </section>

            <section>
              <h2 className="text-amber-300 font-semibold mb-2">8. 改定</h2>
              <p>
                本プライバシーポリシーは、必要に応じて改定する場合があります。改定後のポリシーは本ページに掲載します。
              </p>
            </section>

            <p className="text-gray-500 text-xs pt-4 border-t border-white/10">
              制定日: 2024年12月1日
            </p>
          </div>

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
