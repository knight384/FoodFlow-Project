"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "@/lib/config";
import { AppShell } from "@/components/AppShell";
import { Activity, Database, Server, Globe } from "lucide-react";

type CheckStatus = "checking" | "ok" | "error";

interface CheckState {
  status: CheckStatus;
  detail?: string;
}

export default function SystemStatusPage() {
  const [apiCheck, setApiCheck] = useState<CheckState>({ status: "checking" });
  const [dbCheck, setDbCheck] = useState<CheckState>({ status: "checking" });

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(() => setApiCheck({ status: "ok" }))
      .catch((err) =>
        setApiCheck({ status: "error", detail: String(err) }),
      );

    fetch(`${API_BASE_URL}/health/db`)
      .then((res) => res.json())
      .then((body) => {
        if (body.status === "ok") {
          setDbCheck({ status: "ok" });
        } else {
          setDbCheck({ status: "error", detail: body.detail ?? "unreachable" });
        }
      })
      .catch((err) => setDbCheck({ status: "error", detail: String(err) }));
  }, []);

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">System Status</h1>
        <p className="text-sm text-textSecondary mt-1">
          Monitor infrastructure health and connectivity.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 max-w-4xl">
        <StatusCard 
          title="Frontend Interface" 
          description="Web application delivery"
          status="ok" 
          detail="Operating normally"
          icon={<Globe className="text-textSecondary" size={20} />}
        />
        <StatusCard 
          title="Backend API" 
          description="Core application logic and endpoints"
          status={apiCheck.status} 
          detail={apiCheck.status === "ok" ? "Operating normally" : apiCheck.detail}
          icon={<Server className="text-textSecondary" size={20} />}
        />
        <StatusCard 
          title="Database" 
          description="Persistent storage connectivity"
          status={dbCheck.status} 
          detail={dbCheck.status === "ok" ? "Operating normally" : dbCheck.detail}
          icon={<Database className="text-textSecondary" size={20} />}
        />
      </div>

      <div className="mt-8 card p-6 max-w-4xl bg-surfaceHighlight border-dashed">
        <div className="flex items-center gap-2 text-textPrimary font-medium mb-2">
          <Activity size={18} className="text-accent" />
          Diagnostic Information
        </div>
        <p className="text-xs text-textSecondary leading-relaxed max-w-2xl">
          These checks verify that the foundation components (Frontend, Backend API, Database) are wired together correctly. The checks call the infrastructure health endpoints (`GET /health` and `GET /health/db`). If any component shows an error, check the respective service logs for detailed stack traces.
        </p>
      </div>
    </AppShell>
  );
}

function StatusCard({
  title,
  description,
  status,
  detail,
  icon
}: {
  title: string;
  description: string;
  status: CheckStatus;
  detail?: string;
  icon: React.ReactNode;
}) {
  const getStatusDisplay = () => {
    if (status === "checking") {
      return {
        color: "bg-statusUnavailable/10 border-statusUnavailable/20 text-statusUnavailable",
        dot: "bg-statusUnavailable animate-pulse",
        text: "Checking..."
      };
    }
    if (status === "ok") {
      return {
        color: "bg-statusSurplus/10 border-statusSurplus/20 text-statusSurplus",
        dot: "bg-statusSurplus",
        text: "Healthy"
      };
    }
    return {
      color: "bg-statusShortage/10 border-statusShortage/20 text-statusShortage",
      dot: "bg-statusShortage animate-pulse",
      text: "Error"
    };
  };

  const display = getStatusDisplay();

  return (
    <div className="card p-5 flex flex-col h-full relative overflow-hidden group hover:border-borderHover transition-colors duration-200">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-surfaceHighlight rounded-md border border-border group-hover:border-borderHover transition-colors">
          {icon}
        </div>
        <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-xs font-medium ${display.color}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${display.dot}`}></span>
          {display.text}
        </div>
      </div>
      
      <div className="mt-auto">
        <h3 className="text-sm font-medium text-textPrimary">{title}</h3>
        <p className="text-xs text-textSecondary mt-1">{description}</p>
        
        {detail && status === "error" && (
          <div className="mt-3 p-2 bg-statusShortage/5 border border-statusShortage/10 rounded text-xs text-statusShortage font-mono truncate" title={detail}>
            {detail}
          </div>
        )}
      </div>
    </div>
  );
}
