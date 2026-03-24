import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const alt = '打出の小槌AI - 願いを叶える5ステップ';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: 'linear-gradient(135deg, #1e0a3c 0%, #3b1278 50%, #1e0a3c 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'sans-serif',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
          <div style={{ width: 64, height: 64, background: '#fbbf24', borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="36" height="36" viewBox="0 0 24 24" fill="#1e0a3c">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
            </svg>
          </div>
          <span style={{ color: '#fbbf24', fontSize: 28, fontWeight: 700 }}>打出の小槌AI</span>
        </div>
        <div style={{ color: 'white', fontSize: 48, fontWeight: 900, textAlign: 'center', lineHeight: 1.3, maxWidth: 900 }}>
          願いを叶える
          <br />
          5ステップを即提案
        </div>
        <div style={{ color: '#c4b5fd', fontSize: 22, marginTop: 24, textAlign: 'center' }}>
          あなたの願い事を入力するだけ | AIが実現への道を示す
        </div>
      </div>
    ),
    { ...size }
  );
}
