import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Order Tracker",
  description: "Real-time order tracking dashboard with status monitoring and alerts",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
