"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Bookmark, ClipboardList, Milestone } from "lucide-react";

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="nav-links">
      <Link href="/" className={`nav-link ${pathname === "/" ? "active" : ""}`}>
        <LayoutDashboard size={15} />
        Dashboard
      </Link>
      <Link href="/saved" className={`nav-link ${pathname === "/saved" ? "active" : ""}`}>
        <Bookmark size={15} />
        Saved
      </Link>
      <Link href="/applications" className={`nav-link ${pathname === "/applications" ? "active" : ""}`}>
        <ClipboardList size={15} />
        Applied
      </Link>
      <Link href="/roadmap" className={`nav-link ${pathname === "/roadmap" ? "active" : ""}`}>
        <Milestone size={15} />
        Roadmap
      </Link>
    </nav>
  );
}
