import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI-Powered Personalized Restaurant Menu',
  description: 'Enhancing dining experiences through explainable, constraint-aware recommendation without hiding the full menu.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased text-slate-900 bg-slate-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}
