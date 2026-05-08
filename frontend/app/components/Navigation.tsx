"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="nav-links">
      <Link href="/" className={`nav-link ${pathname === "/" ? "active" : ""}`}>
        Dashboard
      </Link>
      <Link href="/saved" className={`nav-link ${pathname === "/saved" ? "active" : ""}`}>
        Saved
      </Link>
      <Link href="/applications" className={`nav-link ${pathname === "/applications" ? "active" : ""}`}>
        Applications
      </Link>
    </nav>
  );
}
