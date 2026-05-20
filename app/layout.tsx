import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '뽑기맵',
  description: '전국 뽑기방 커뮤니티'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
