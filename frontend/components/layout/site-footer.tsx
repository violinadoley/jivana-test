import Link from "next/link";

import { JivanaLogo } from "@/components/brand/jivana-logo";

const columns = [
  {
    title: "Product",
    links: [
      { href: "/#product", label: "Overview" },
      { href: "/#features", label: "Solutions" },
      { href: "/dashboard", label: "Workspace" },
    ],
  },
  {
    title: "Company",
    links: [
      { href: "/#approach", label: "About" },
      { href: "/#capabilities", label: "Capabilities" },
    ],
  },
  {
    title: "Legal",
    links: [{ href: "/#", label: "Demo disclaimer" }],
  },
] as const;

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-border/60 bg-background">
      <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-[1.2fr_repeat(3,1fr)]">
          <div>
            <JivanaLogo size="md" showTagline />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Synthetic demo data only. Not for clinical decision-making without independent
              validation.
            </p>
          </div>
          {columns.map((col) => (
            <div key={col.title}>
              <p className="text-sm font-semibold text-foreground">{col.title}</p>
              <ul className="mt-4 space-y-2">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-12 flex flex-col gap-4 border-t border-border/60 pt-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">© {new Date().getFullYear()} Jivana</p>
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>LinkedIn</span>
            <span>X</span>
            <span>YouTube</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
