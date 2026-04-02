"use client";

import { useState, useEffect, useRef } from "react";
import { haptics } from "@/utils/haptics";
import { updateStreak, loadStreak, getStreakMilestoneMessage, StreakData } from "@/lib/streak";

export default function Home() {
  const [wish, setWish] = useState("");
  const [steps, setSteps] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [streak, setStreak] = useState<StreakData>({ count: 0, lastDate: "", shield: false });
  const [milestoneMsg, setMilestoneMsg] = useState<string | null>(null);
  const [isHammerSwinging, setIsHammerSwinging] = useState(false);
  const [currentWish, setCurrentWish] = useState("");
  const stepsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const data = loadStreak("uchide-kozuchi");
    setStreak(data);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!wish.trim() || isLoading) return;

    setIsLoading(true);
    setSteps("");
    setIsComplete(false);
    setCurrentWish(wish.trim());
    haptics.tap();
    setIsHammerSwinging(true);
    setTimeout(() => setIsHammerSwinging(false), 1800);

    // Update streak
    const newStreak = updateStreak("uchide-kozuchi");
    setStreak(newStreak);
    const msg = getStreakMilestoneMessage(newStreak.count);
    if (msg) setMilestoneMsg(msg);

    try {
      const res = await fetch("/api/wish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wish: wish.trim() }),
      });

      if (!res.ok) throw new Error("API error");

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let accumulated = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        setSteps(accumulated);
        if (stepsRef.current) {
          stepsRef.current.scrollTop = stepsRef.current.scrollHeight;
        }
      }
      haptics.success();
      setIsComplete(true);
    } catch {
      haptics.error();
      setSteps("エラーが発生しました。しばらくしてから再度お試しください。");
      setIsComplete(true);
    } finally {
      setIsLoading(false);
    }
  };

  const getFirstStep = () => {
    const lines = steps.split("\n").filter((l) => l.trim());
    return lines[0] || "";
  };

  const handleShare = () => {
    const firstStep = getFirstStep();
    const text = `【打出の小槌AI】\n願い事: ${currentWish}\n\n${firstStep}\n\nhttps://uchide-kozuchi.vercel.app`;
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const formatSteps = (text: string) => {
    return text.split("\n").map((line, i) => {
      if (!line.trim()) return null;
      const isNumbered = /^[1-5][.．、）)]\s/.test(line);
      return (
        <p
          key={i}
          className={`leading-relaxed ${isNumbered ? "step-item font-medium" : ""}`}
        >
          {line}
        </p>
      );
    });
  };

  return (
    <main className="min-h-screen relative overflow-hidden" style={{ background: "radial-gradient(ellipse at 20% 50%, rgba(245,158,11,0.12) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(217,119,6,0.08) 0%, transparent 50%), radial-gradient(ellipse at 50% 80%, rgba(252,211,77,0.06) 0%, transparent 50%), #0F0F1A" }}>
      {/* Background gradient orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
        <div
          className="absolute top-0 left-1/4 w-96 h-96 rounded-full opacity-10 blur-3xl"
          style={{ backgroundColor: "#f59e0b" }}
        />
        <div
          className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full opacity-8 blur-3xl"
          style={{ backgroundColor: "#d97706" }}
        />
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full opacity-5 blur-3xl"
          style={{ backgroundColor: "#fcd34d" }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-2xl">
        {/* Header */}
        <header className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <div
              className={`text-6xl select-none ${isHammerSwinging ? "hammer-swing" : ""}`}
              role="img"
              aria-label="打出の小槌のアイコン"
              style={{ filter: "drop-shadow(0 0 20px rgba(245,158,11,0.6))" }}
            >
              <svg
                width="72"
                height="72"
                viewBox="0 0 72 72"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                aria-hidden="true"
              >
                <rect x="28" y="8" width="16" height="36" rx="4" fill="#f59e0b" />
                <rect x="12" y="6" width="48" height="18" rx="6" fill="#fcd34d" />
                <rect x="14" y="8" width="44" height="14" rx="5" fill="#f59e0b" />
                <rect x="31" y="44" width="10" height="22" rx="3" fill="#d97706" />
                <circle cx="20" cy="56" r="3" fill="#fcd34d" opacity="0.8" />
                <circle cx="52" cy="52" r="2" fill="#fcd34d" opacity="0.6" />
                <circle cx="58" cy="62" r="2.5" fill="#f59e0b" opacity="0.7" />
                <circle cx="14" cy="62" r="2" fill="#fcd34d" opacity="0.5" />
              </svg>
            </div>
          </div>

          <h1 className="text-4xl font-bold mb-3">
            <span style={{ background: "linear-gradient(135deg, #fcd34d 0%, #f59e0b 50%, #d97706 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", filter: "drop-shadow(0 0 20px rgba(245,158,11,0.3))" }}>打出の小槌AI</span>
          </h1>
          <p className="text-gray-300 text-lg">
            願い事を入力すると、AIが実現への5つのステップを提案します
          </p>

          {/* Streak badge */}
          {streak.count > 0 && (
            <div className="flex justify-center mt-4">
              <div
                className="streak-badge inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold text-amber-900"
                role="status"
                aria-label={`${streak.count}日連続利用中${streak.shield ? "・シールド有効" : ""}`}
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path d="M8 1L10 6H15L11 9.5L12.5 15L8 11.5L3.5 15L5 9.5L1 6H6L8 1Z" fill="currentColor" />
                </svg>
                <span>{streak.count}日連続</span>
                {streak.shield && (
                  <span className="text-xs bg-amber-900/30 px-1.5 py-0.5 rounded">シールド</span>
                )}
              </div>
            </div>
          )}
        </header>

        {/* Milestone message */}
        {milestoneMsg && (
          <div
            className="glass-card rounded-2xl p-4 mb-6 text-center border border-amber-500/30"
            role="alert"
            aria-live="polite"
          >
            <p className="text-amber-300 font-semibold">{milestoneMsg}</p>
          </div>
        )}

        {/* Input form */}
        <section className="glass-card rounded-2xl p-6 mb-6" aria-label="願い事入力フォーム">
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label
                htmlFor="wish-input"
                className="block text-amber-300 font-semibold mb-2 text-sm uppercase tracking-wider"
              >
                あなたの願い事
              </label>
              <textarea
                id="wish-input"
                value={wish}
                onChange={(e) => setWish(e.target.value)}
                placeholder="例: 英語を流暢に話せるようになりたい"
                className="w-full rounded-xl p-4 text-gray-100 placeholder-gray-500 resize-none focus:ring-2 focus:ring-amber-500 transition-all text-base leading-relaxed"
                style={{
                  backgroundColor: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(245,158,11,0.3)",
                  minHeight: "100px",
                }}
                rows={3}
                maxLength={200}
                aria-label="願い事を入力してください（200文字以内）"
                aria-required="true"
                disabled={isLoading}
              />
              <p className="text-right text-xs text-gray-500 mt-1" aria-live="polite">
                {wish.length}/200
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading || !wish.trim()}
              className="w-full py-4 rounded-2xl font-bold text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed hover:-translate-y-0.5 active:scale-[0.97] min-h-[52px]"
              style={{
                background: isLoading
                  ? "rgba(245,158,11,0.5)"
                  : "linear-gradient(135deg, #f59e0b, #d97706)",
                color: "#1a1208",
                boxShadow: isLoading ? "none" : "0 0 25px rgba(245,158,11,0.35), 0 4px 15px rgba(0,0,0,0.3)",
              }}
              aria-label={isLoading ? "願い事を叶えています..." : "願い事を叶える"}
              aria-busy={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-3">
                  <svg
                    className="animate-spin"
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    aria-hidden="true"
                  >
                    <circle
                      className="opacity-25"
                      cx="10"
                      cy="10"
                      r="8"
                      stroke="currentColor"
                      strokeWidth="3"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M10 2a8 8 0 0 1 8 8h-2a6 6 0 0 0-6-6V2z"
                    />
                  </svg>
                  願いを叶えています...
                </span>
              ) : (
                "叶えてもらう"
              )}
            </button>
          </form>
        </section>

        {/* Results */}
        {(steps || isLoading) && (
          <section
            className="glass-card rounded-2xl p-6 mb-6"
            aria-label="AIの提案ステップ"
            aria-live="polite"
          >
            <div className="flex items-center gap-2 mb-4">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path
                  d="M10 2L12.5 7.5H18L13.5 11L15.5 17L10 13.5L4.5 17L6.5 11L2 7.5H7.5L10 2Z"
                  fill="#f59e0b"
                />
              </svg>
              <h2 className="text-amber-300 font-semibold text-sm uppercase tracking-wider">
                実現ステップ
              </h2>
              {isLoading && !isComplete && (
                <span className="text-xs text-gray-400 animate-pulse" aria-live="polite">
                  生成中...
                </span>
              )}
            </div>

            {currentWish && (
              <p className="text-gray-400 text-sm mb-4 pb-4 border-b border-white/10">
                願い事: <span className="text-amber-200">{currentWish}</span>
              </p>
            )}

            <div
              ref={stepsRef}
              className="text-gray-200 space-y-2 max-h-80 overflow-y-auto pr-1"
              aria-label="AIが生成した実現ステップの内容"
            >
              {formatSteps(steps)}
              {isLoading && !isComplete && (
                <span
                  className="inline-block w-2 h-5 bg-amber-400 animate-pulse"
                  aria-hidden="true"
                />
              )}
            </div>

            {/* Share button */}
            {isComplete && steps && (
              <div className="mt-6 pt-4 border-t border-white/10">
                <button
                  onClick={handleShare}
                  className="w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 hover:opacity-90 active:scale-95"
                  style={{
                    backgroundColor: "#000",
                    color: "#fff",
                    border: "1px solid rgba(255,255,255,0.2)",
                  }}
                  aria-label="Xでシェアする"
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                  Xでシェア
                </button>
              </div>
            )}
          </section>
        )}

        {/* How it works */}
        {!steps && !isLoading && (
          <section
            className="glass-card rounded-2xl p-6 mb-6"
            aria-label="使い方の説明"
          >
            <h2 className="text-amber-300 font-semibold text-sm uppercase tracking-wider mb-4">
              使い方
            </h2>
            <ol className="space-y-3 text-gray-300 text-sm" aria-label="3ステップの使い方">
              {[
                { step: "1", text: "願い事を入力してください（例: 副業で月10万円稼ぎたい）" },
                { step: "2", text: "「叶えてもらう」ボタンを押す" },
                { step: "3", text: "AIが実現のための具体的な5つのステップを提案します" },
              ].map(({ step, text }) => (
                <li key={step} className="flex items-start gap-3">
                  <span
                    className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-amber-900"
                    style={{ backgroundColor: "#f59e0b" }}
                    aria-hidden="true"
                  >
                    {step}
                  </span>
                  <span>{text}</span>
                </li>
              ))}
            </ol>
          </section>
        )}

        {/* Premium CTA */}
        {!steps && !isLoading && (
          <section
            className="glass-cta p-6 mb-6 text-center"
            aria-label="プレミアムプランのご案内"
          >
            <h2 className="text-amber-300 font-bold text-base mb-2">
              AIが毎日3つのラッキーアドバイスを生成
            </h2>
            <p className="text-gray-400 text-sm mb-2">
              運気を上げる具体的な行動が分かります。毎日続けることで、願いが現実に変わっていく。
            </p>
            <p className="text-amber-400/80 text-xs mb-4 font-semibold">
              プレミアム版では毎日6つのアドバイス + 詳細運勢レポートをお届け
            </p>
            <button
              type="button"
              className="rounded-2xl font-black text-lg py-4 px-8 text-center inline-block transition-opacity hover:opacity-90 active:scale-95 min-h-[44px]"
              style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)', color: '#1a1208' }}
              aria-label="プレミアムプランに申し込む（月額480円）"
              onClick={() => {
                // 決済連携後にここをリンク先に変更してください
                alert("プレミアムプランは準備中です。近日公開予定！");
              }}
            >
              プレミアムを始める → ¥480/月
            </button>
            <p className="text-gray-500 text-xs mt-3">初月無料・いつでも解約可能</p>
          </section>
        )}

        {/* Footer */}
        <footer className="text-center text-xs text-gray-500 mt-8 space-y-2">
          <nav aria-label="フッターナビゲーション">
            <ul className="flex justify-center gap-4">
              <li>
                <a
                  href="/privacy"
                  className="hover:text-amber-400 transition-colors"
                  aria-label="プライバシーポリシーを見る"
                >
                  プライバシーポリシー
                </a>
              </li>
              <li>
                <a
                  href="/legal"
                  className="hover:text-amber-400 transition-colors"
                  aria-label="特定商取引法に基づく表記を見る"
                >
                  特定商取引法に基づく表記
                </a>
              </li>
            </ul>
          </nav>
          <p>&copy; 2024 ポッコリラボ. All rights reserved.</p>
        </footer>
      </div>
    </main>
  );
}
