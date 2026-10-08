"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Reviews" },
  { href: "/dashboard", label: "Analytics" },
  { href: "/developers", label: "Developers" },
];

export default function Nav() {
  const pathname = usePathname();
  const isActive = (href: string) =>
    href === "/" ? pathname === "/" || pathname.startsWith("/reviews") : pathname.startsWith(href);

  return (
    <header className="border-b border-border bg-surface">
      <nav className="mx-auto flex max-w-6xl items-center gap-8 px-8">
        <Link href="/" className="py-3 text-lg font-semibold tracking-tight">
          PRISM
        </Link>
        <ul className="flex gap-6 text-sm">
          {links.map((l) => (
            <li key={l.href}>
              <Link
                href={l.href}
                aria-current={isActive(l.href) ? "page" : undefined}
                className={`block border-b-2 py-3.5 transition-colors ${
                  isActive(l.href)
                    ? "border-accent text-foreground"
                    : "border-transparent text-muted hover:text-foreground"
                }`}
              >
                {l.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}