"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";
import type { Role } from "@/lib/types";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  TrendingUp,
  ClipboardList,
  Lightbulb,
  FileBarChart,
  Database,
  MapPin,
  Utensils,
  Users,
  Activity,
  LogOut,
  Menu,
  X,
  ChevronDown,
} from "lucide-react";
import { LoadingState } from "@/components/LoadingState";

type NavItem = {
  href: string;
  label: string;
  roles: Role[];
  icon: React.ElementType;
};

type NavGroup = {
  title: string;
  items: NavItem[];
};

const NAV_GROUPS: NavGroup[] = [
  {
    title: "Overview",
    items: [
      { href: "/dashboard", label: "Dashboard", roles: ["administrator", "manager", "operations_staff"], icon: LayoutDashboard },
    ],
  },
  {
    title: "Planning",
    items: [
      { href: "/forecasts", label: "Forecasts", roles: ["administrator", "manager"], icon: TrendingUp },
      { href: "/planned-quantities", label: "Planned Quantities", roles: ["administrator", "manager", "operations_staff"], icon: ClipboardList },
    ],
  },
  {
    title: "Insights",
    items: [
      { href: "/recommendations", label: "Recommendations", roles: ["administrator", "manager"], icon: Lightbulb },
      { href: "/reports", label: "Reports", roles: ["administrator", "manager"], icon: FileBarChart },
    ],
  },
  {
    title: "Data Management",
    items: [
      { href: "/historical-data", label: "Historical Data", roles: ["administrator"], icon: Database },
      { href: "/locations", label: "Locations", roles: ["administrator"], icon: MapPin },
      { href: "/meal-types", label: "Meal Types", roles: ["administrator"], icon: Utensils },
    ],
  },
  {
    title: "Administration",
    items: [
      { href: "/users", label: "Users", roles: ["administrator"], icon: Users },
      { href: "/system-status", label: "System Status", roles: ["administrator"], icon: Activity },
    ],
  },
];

export function roleLabel(role: Role): string {
  switch (role) {
    case "administrator":
      return "Administrator";
    case "manager":
      return "Manager";
    case "operations_staff":
      return "Operations Staff";
    default:
      return role;
  }
}

export function AppShell({ children }: { children: ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading) {
    return <LoadingState className="min-h-screen" text="Loading FoodFlow..." />;
  }

  if (!user) {
    return null;
  }

  // Filter nav groups by user role
  const visibleGroups = NAV_GROUPS.map(group => ({
    ...group,
    items: group.items.filter(item => item.roles.includes(user.role))
  })).filter(group => group.items.length > 0);

  const SidebarContent = () => (
    <>
      <div className="flex h-16 items-center px-6 border-b border-border bg-surface">
        <Link href="/dashboard" className="text-lg font-bold tracking-tight text-textPrimary flex items-center gap-3 transition-opacity hover:opacity-80">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent text-white shadow-sm">
            <LayoutDashboard size={18} />
          </div>
          FoodFlow
        </Link>
      </div>
      
      <div className="flex-1 overflow-y-auto py-6 custom-scrollbar">
        <nav className="space-y-8 px-4">
          {visibleGroups.map((group, idx) => (
            <div key={idx}>
              <h3 className="mb-3 px-2 text-xs font-semibold uppercase tracking-wider text-textSecondary/70">
                {group.title}
              </h3>
              <ul className="space-y-1">
                {group.items.map((item) => {
                  const isActive = pathname?.startsWith(item.href);
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        onClick={() => setMobileNavOpen(false)}
                        className={cn(
                          "group relative flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200",
                          isActive
                            ? "bg-accent/15 text-accent"
                            : "text-textSecondary hover:bg-surfaceHighlight hover:text-textPrimary"
                        )}
                      >
                        {isActive && (
                          <div className="absolute left-0 top-1/2 -mt-3 h-6 w-1 rounded-r-md bg-accent" />
                        )}
                        <item.icon
                          className={cn("h-4 w-4 flex-shrink-0 transition-colors", isActive ? "text-accent" : "text-textSecondary group-hover:text-textPrimary")}
                        />
                        {item.label}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>
      </div>

      <div className="border-t border-border bg-surface p-4">
        <div className="mb-4 flex items-center gap-3 px-2 rounded-lg py-2 transition-colors hover:bg-surfaceHighlight cursor-pointer">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/20 text-accent font-semibold shadow-sm border border-accent/20">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div className="flex flex-col flex-1 overflow-hidden">
            <span className="text-sm font-semibold text-textPrimary truncate leading-tight">{user.username}</span>
            <span className="text-xs text-textSecondary mt-0.5 truncate">{roleLabel(user.role)}</span>
          </div>
          <ChevronDown size={14} className="text-textSecondary" />
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-textSecondary transition-all duration-200 hover:bg-surfaceHighlight hover:text-textPrimary focus:outline-none focus:ring-2 focus:ring-accent/50 active:scale-[0.98]"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </div>
    </>
  );

  return (
    <div className="flex min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 flex-col border-r border-border bg-surface md:flex relative z-10 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
        <SidebarContent />
      </aside>

      {/* Mobile Drawer */}
      {mobileNavOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div 
            className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity" 
            onClick={() => setMobileNavOpen(false)} 
          />
          <aside className="relative flex w-72 max-w-[85%] flex-col bg-surface shadow-2xl border-r border-border h-full transition-transform transform">
            <div className="absolute right-0 top-0 -mr-12 pt-4">
              <button
                type="button"
                className="ml-1 flex h-10 w-10 items-center justify-center rounded-full bg-surface/50 backdrop-blur-md focus:outline-none focus:ring-2 focus:ring-inset focus:ring-accent text-textPrimary hover:bg-surface transition-colors"
                onClick={() => setMobileNavOpen(false)}
              >
                <X className="h-5 w-5" aria-hidden="true" />
                <span className="sr-only">Close sidebar</span>
              </button>
            </div>
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        {/* Mobile Top Header (Glassmorphism) */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-surface/80 backdrop-blur-md px-4 md:hidden">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent text-white shadow-sm">
              <LayoutDashboard size={16} />
            </div>
            <span className="text-lg font-bold tracking-tight text-textPrimary">FoodFlow</span>
          </div>
          <button
            type="button"
            className="-mx-2 inline-flex items-center justify-center rounded-md p-2.5 text-textSecondary hover:bg-surfaceHighlight hover:text-textPrimary focus:outline-none focus:ring-2 focus:ring-accent transition-colors active:scale-95"
            onClick={() => setMobileNavOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>
        </header>

        <main className="flex-1 overflow-y-auto bg-background p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl w-full animate-in fade-in duration-500">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
