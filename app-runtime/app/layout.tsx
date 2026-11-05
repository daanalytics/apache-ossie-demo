import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Apache Ossie + Snowflake Demo",
  description: "How Apache Ossie metric context maps to a Snowflake semantic view.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
