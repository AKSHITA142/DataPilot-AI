"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Upload,
  Activity,
  FlaskConical,
  BookOpen,
  Lightbulb,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
} from "lucide-react";

/* ── Nav items — only real routes ──────────────── */
const NAV_ITEMS = [
  { href: "/upload", icon: Upload, label: "New Run" },
  { href: "/timeline", icon: Activity, label: "Timeline", dynamic: true },
  { href: "/experiments", icon: FlaskConical, label: "Experiments", dynamic: true },
  { href: "/knowledge", icon: BookOpen, label: "Knowledge", dynamic: true },
  { href: "/recommendation", icon: Lightbulb, label: "Recommendation", dynamic: true },
];

/* ── Single nav link ─────────────────────────────── */
function NavLink({
  href,
  icon: Icon,
  label,
  collapsed,
  active,
  dynamic,
}: {
  href: string;
  icon: React.ElementType;
  label: string;
  collapsed: boolean;
  active: boolean;
  dynamic?: boolean;
}) {
  const sharedClassName = `
    group relative flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium
    transition-colors duration-150 select-none
    ${active
      ? "bg-surface-4 text-text"
      : "text-text-muted hover:text-text-secondary hover:bg-surface-3"
    }
    ${dynamic && !active ? "cursor-default opacity-60" : "cursor-pointer"}
  `;

  const innerContent = (
    <>
      {/* Active indicator stripe */}
      {active && (
        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-brand-500" />
      )}

      <Icon
        className={`w-4 h-4 shrink-0 transition-colors ${
          active ? "text-brand-400" : "text-text-muted group-hover:text-text-secondary"
        }`}
      />

      <AnimatePresence>
        {!collapsed && (
          <motion.span
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: "auto" }}
            exit={{ opacity: 0, width: 0 }}
            transition={{ duration: 0.18 }}
            className="overflow-hidden whitespace-nowrap"
          >
            {label}
          </motion.span>
        )}
      </AnimatePresence>

      {/* Tooltip when collapsed */}
      {collapsed && (
        <span className="
          pointer-events-none absolute left-full ml-3 px-2 py-1 rounded-md
          bg-surface-3 border border-border text-xs text-text-secondary whitespace-nowrap
          opacity-0 group-hover:opacity-100 transition-opacity duration-150 z-50
        ">
          {label}
        </span>
      )}
    </>
  );

  if (dynamic) {
    return (
      <div
        title={`${label} (open from an active run)`}
        className={sharedClassName}
      >
        {innerContent}
      </div>
    );
  }

  return (
    <Link href={href} className={sharedClassName}>
      {innerContent}
    </Link>
  );
}


/* ── Main Sidebar ───────────────────────────────── */
export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <motion.aside
      animate={{ width: collapsed ? 60 : 220 }}
      transition={{ duration: 0.22, ease: "easeInOut" }}
      className="
        hidden md:flex flex-col shrink-0
        bg-surface-1 border-r border-border-subtle
        h-screen sticky top-0 overflow-hidden z-20
      "
    >
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-3 py-4 border-b border-border-subtle h-14 shrink-0">
        <Link href="/" className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 rounded-md bg-brand-500 flex items-center justify-center shrink-0">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.18 }}
                className="font-semibold text-sm tracking-tight text-text whitespace-nowrap overflow-hidden"
              >
                DataPilot<span className="text-brand-400">-AI</span>
              </motion.span>
            )}
          </AnimatePresence>
        </Link>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-2 py-3 flex flex-col gap-0.5 overflow-y-auto overflow-x-hidden">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.href}
            {...item}
            collapsed={collapsed}
            active={isActive(item.href)}
          />
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="px-2 pb-4 pt-2 border-t border-border-subtle shrink-0">
        <button
          onClick={() => setCollapsed((c) => !c)}
          className="
            w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md
            text-text-muted hover:text-text-secondary hover:bg-surface-3
            transition-colors text-xs font-medium
          "
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </motion.aside>
  );
}

/* ── Mobile Drawer ──────────────────────────────── */
export function MobileDrawer({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const pathname = usePathname();

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={onClose}
          />

          {/* Drawer panel */}
          <motion.aside
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ duration: 0.22, ease: "easeInOut" }}
            className="
              fixed top-0 left-0 bottom-0 w-64
              bg-surface-1 border-r border-border z-50 md:hidden
              flex flex-col
            "
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 h-14 border-b border-border-subtle">
              <Link href="/" onClick={onClose} className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-md bg-brand-500 flex items-center justify-center">
                  <Brain className="w-4 h-4 text-white" />
                </div>
                <span className="font-semibold text-sm tracking-tight text-text">
                  DataPilot<span className="text-brand-400">-AI</span>
                </span>
              </Link>
              <button
                onClick={onClose}
                className="p-1.5 rounded-md text-text-muted hover:text-text hover:bg-surface-3 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Nav */}
            <nav className="flex-1 px-3 py-3 flex flex-col gap-0.5 overflow-y-auto">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.href}
                  {...item}
                  collapsed={false}
                  active={isActive(item.href)}
                />
              ))}
            </nav>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}

/* ── Mobile Bottom Nav ───────────────────────────── */
export function MobileBottomNav() {
  const pathname = usePathname();

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + "/");

  const BOTTOM_ITEMS = [
    { href: "/upload", icon: Upload, label: "New Run" },
    { href: "/timeline", icon: Activity, label: "Timeline", dynamic: true },
    { href: "/experiments", icon: FlaskConical, label: "Experiments", dynamic: true },
    { href: "/knowledge", icon: BookOpen, label: "Knowledge", dynamic: true },
  ];

  return (
    <nav className="
      md:hidden fixed bottom-0 left-0 right-0 z-30
      bg-surface-1 border-t border-border-subtle
      flex items-center justify-around px-2 pb-safe
    ">
      {BOTTOM_ITEMS.map((item) => {
        const active = isActive(item.href);
        const itemClassName = `
          flex flex-col items-center gap-0.5 px-3 py-2.5 min-w-[56px]
          text-xs font-medium transition-colors
          ${active ? "text-brand-400" : "text-text-muted"}
          ${item.dynamic && !active ? "opacity-50 cursor-default" : "cursor-pointer"}
        `;

        if (item.dynamic) {
          return (
            <div key={item.href} className={itemClassName}>
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </div>
          );
        }

        return (
          <Link key={item.href} href={item.href} className={itemClassName}>
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}


/* ── Hamburger trigger (used in Topbar) ─────────── */
export function HamburgerButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="
        md:hidden p-2 rounded-md text-text-muted hover:text-text
        hover:bg-surface-3 transition-colors
      "
      aria-label="Open navigation"
    >
      <Menu className="w-5 h-5" />
    </button>
  );
}
