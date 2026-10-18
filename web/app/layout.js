import './globals.css';

export const metadata = {
  title: 'EasyNmap — Understand your network',
  description: 'Explore EasyNmap in an interactive terminal, analyze Nmap output, and turn scan results into clear, actionable reports.',
};

export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>;
}
