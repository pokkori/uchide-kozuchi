export interface StreakData {
  count: number;
  lastDate: string;
  shield: boolean;
}

export function updateStreak(key: string): StreakData {
  const today = new Date().toISOString().split("T")[0];
  const raw =
    typeof window !== "undefined"
      ? localStorage.getItem(`streak_${key}`)
      : null;
  const data: StreakData = raw
    ? JSON.parse(raw)
    : { count: 0, lastDate: "", shield: false };

  // Already updated today
  if (data.lastDate === today) return data;

  const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0];

  if (data.lastDate === yesterday) {
    // Consecutive day
    data.count += 1;
  } else if (data.shield && data.lastDate) {
    // Shield absorbs a missed day
    data.count += 1;
    data.shield = false;
  } else {
    // Reset streak
    data.count = 1;
  }

  // Award shield every 7 days
  if (data.count % 7 === 0) {
    data.shield = true;
  }

  data.lastDate = today;
  localStorage.setItem(`streak_${key}`, JSON.stringify(data));
  return data;
}

export function loadStreak(key: string): StreakData {
  const raw =
    typeof window !== "undefined"
      ? localStorage.getItem(`streak_${key}`)
      : null;
  return raw ? JSON.parse(raw) : { count: 0, lastDate: "", shield: false };
}

export function getStreakMilestoneMessage(streak: number): string | null {
  if (streak === 3) return "3日連続！習慣化が始まっています";
  if (streak === 7) return "1週間達成！シールドを獲得しました";
  if (streak === 14) return "2週間継続！素晴らしい習慣です";
  if (streak === 30) return "30日達成！あなたは意志の強い人です";
  return null;
}
