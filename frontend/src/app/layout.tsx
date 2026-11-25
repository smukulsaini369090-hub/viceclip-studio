import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VICECLIP STUDIO — GTA 6 Viral Video Clipping Studio",
  description: "Local-first AI viral video clipping studio engineered for GTA 6 YouTube Shorts on Windows 11 / RTX 3050",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-studio-950 text-studio-100 min-h-screen antialiased selection:bg-tally-amber selection:text-studio-950">
        {children}
      </body>
    </html>
  );
}
