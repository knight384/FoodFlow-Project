"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { describeApiError } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { LayoutDashboard, Eye, EyeOff, Activity, ShieldCheck, TrendingUp } from "lucide-react";
import { LoadingState } from "@/components/LoadingState";

export default function LoginPage() {
  const { login, user, isLoading } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/dashboard");
    }
  }, [isLoading, user, router]);

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState text="" />
      </main>
    );
  }

  if (user) {
    return null; // redirect effect above is in flight
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      router.replace("/dashboard");
    } catch (err) {
      setError(describeApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-background">
      {/* Left side: Branding/Value Prop (Hidden on mobile, visible on lg screens) */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-surface p-12 border-r border-border relative overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-20">
          <div className="absolute -top-24 -left-24 w-96 h-96 bg-accent rounded-full blur-[128px]"></div>
          <div className="absolute top-1/2 -right-24 w-64 h-64 bg-statusSurplus rounded-full blur-[128px] opacity-30"></div>
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-white shadow-sm">
              <LayoutDashboard size={22} />
            </div>
            <span className="text-2xl font-bold tracking-tight text-textPrimary">FoodFlow</span>
          </div>

          <div className="max-w-md mt-12">
            <h1 className="text-4xl font-semibold tracking-tight text-textPrimary leading-tight mb-6">
              Enterprise Demand Forecasting & Operations
            </h1>
            <p className="text-lg text-textSecondary leading-relaxed">
              Optimize your food supply chain with predictive analytics. Reduce waste, streamline operations, and ensure balanced distribution across all your facilities.
            </p>
          </div>
        </div>

        <div className="relative z-10 grid grid-cols-1 gap-6 max-w-md mt-12">
          <div className="flex items-start gap-4">
            <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-surfaceHighlight text-accent">
              <Activity size={16} />
            </div>
            <div>
              <h3 className="text-sm font-medium text-textPrimary">Real-time Telemetry</h3>
              <p className="text-sm text-textSecondary mt-1">Monitor surplus and shortage events as they happen.</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-surfaceHighlight text-statusSurplus">
              <TrendingUp size={16} />
            </div>
            <div>
              <h3 className="text-sm font-medium text-textPrimary">Predictive AI</h3>
              <p className="text-sm text-textSecondary mt-1">Forecast future demand based on historical operational data.</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-surfaceHighlight text-statusBalanced">
              <ShieldCheck size={16} />
            </div>
            <div>
              <h3 className="text-sm font-medium text-textPrimary">Enterprise Security</h3>
              <p className="text-sm text-textSecondary mt-1">Role-based access control governing facility-level operations.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Login Form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-6 sm:p-12">
        <div className="w-full max-w-md">
          <div className="flex lg:hidden items-center gap-3 mb-10">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-white shadow-sm">
              <LayoutDashboard size={22} />
            </div>
            <span className="text-2xl font-bold tracking-tight text-textPrimary">FoodFlow</span>
          </div>

          <div className="mb-10">
            <h2 className="text-3xl font-semibold tracking-tight text-textPrimary">Welcome back</h2>
            <p className="mt-2 text-sm text-textSecondary">
              Sign in to your account to access your operational dashboard.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <ErrorBanner message={error} />
            
            <div className="space-y-2">
              <label className="block text-sm font-medium text-textPrimary" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input-field py-3 text-base"
                placeholder="Enter your username"
              />
            </div>
            
            <div className="space-y-2">
              <label className="block text-sm font-medium text-textPrimary" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field py-3 text-base pr-12"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 flex items-center px-4 text-textSecondary hover:text-textPrimary focus:outline-none transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex={-1}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            
            <div className="pt-4">
              <button
                type="submit"
                disabled={submitting}
                className="btn-primary w-full py-3 text-base font-semibold shadow-md transition-all active:scale-[0.98]"
              >
                {submitting ? "Authenticating..." : "Sign in to Dashboard"}
              </button>
            </div>
          </form>
          
          <div className="mt-8 text-center">
            <p className="text-xs text-textSecondary">
              By signing in, you agree to the <a href="#" className="text-accent hover:underline">Terms of Service</a> and <a href="#" className="text-accent hover:underline">Privacy Policy</a>.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
