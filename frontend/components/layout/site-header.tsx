import Link from "next/link";

import { JivanaLogo } from "@/components/brand/jivana-logo";

const links = [
  { href: "/#product", label: "Product" },
  { href: "/#features", label: "Solutions" },
  { href: "/#capabilities", label: "Research" },
  { href: "/#approach", label: "About" },
] as const;

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/85 backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-6 px-4 sm:px-6">
        <Link href="/" className="shrink-0">
          <JivanaLogo size="sm" />
        </Link>
        <nav className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
          {links.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-foreground">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="/dashboard"
            className="hidden h-9 items-center px-4 text-sm font-medium text-foreground sm:inline-flex"
          >
            Sign in
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex h-9 items-center rounded-full bg-foreground px-5 text-sm font-medium text-background shadow-sm"
          >
            Open workspace
          </Link>
        </div>
      </div>
    </header>
  );
}
