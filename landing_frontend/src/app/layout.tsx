import type { Metadata } from "next";
import { Work_Sans } from "next/font/google";
import "./globals.css";

const worksans = Work_Sans({ weight: "400", subsets: ["latin"]});


export const metadata: Metadata = {
  title: "Resume Match Pro",
  description: "AI powered resume matching for job seekers and employers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-worksans text-sm sm:text-lg md:text-xl bg-bg text-text">{children}</body>
    </html>
  );
}
