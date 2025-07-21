import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { cn } from "@/lib/utils";
import { GridBackground } from "@/components/grid-background";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Reddit AI Detection Bot",
  description: "Real-time monitoring and analytics dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={cn("antialiased", inter.className)}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <GridBackground />
          <main className="relative z-10">{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
} 