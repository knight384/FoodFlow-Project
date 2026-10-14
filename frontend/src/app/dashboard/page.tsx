"use client";

import { useEffect, useState, useMemo } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, describeApiError } from "@/lib/api";
import type { DashboardRow, Location, MealType } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { StatusBadge } from "@/components/StatusBadge";
import { ErrorBanner } from "@/components/ErrorBanner";
import { StatCard } from "@/components/StatCard";
import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { LoadingState } from "@/components/LoadingState";
import { TrendingUp, ClipboardList, ArrowUpRight, ArrowDownRight, Activity } from "lucide-react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";

const CHART_COLORS = {
  forecast: "#3b82f6", // accent
  planned: "#737373", // neutral gray
  surplus: "#10b981", // green
  shortage: "#ef4444", // red
  balanced: "#f59e0b", // amber
  unavailable: "#52525b" // dark gray
};

export default function DashboardPage() {
  const { token } = useAuth();
  const [rows, setRows] = useState<DashboardRow[]>([]);
  const [locations, setLocations] = useState<Record<string, string>>({});
  const [mealTypes, setMealTypes] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    setError(null);
    Promise.all([
      apiGet<{ data: DashboardRow[] }>("/dashboard", token),
      apiGet<{ data: Location[] }>("/locations", token, { pageSize: 100 }),
      apiGet<{ data: MealType[] }>("/meal-types", token, { pageSize: 100 }),
    ])
      .then(([dashboard, locs, meals]) => {
        setRows(dashboard.data);
        setLocations(Object.fromEntries(locs.data.map((l) => [l.id, l.name])));
        setMealTypes(Object.fromEntries(meals.data.map((m) => [m.id, m.name])));
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }, [token]);

  // Derived KPIs
  const { totalForecast, totalPlanned, surplusCount, shortageCount, statusData, trendData } = useMemo(() => {
    let tf = 0;
    let tp = 0;
    let surp = 0;
    let short = 0;
    let bal = 0;
    let unavail = 0;

    const dateMap: Record<string, { date: string; forecast: number; planned: number }> = {};

    rows.forEach(row => {
      tf += row.forecastedDemand || 0;
      tp += row.plannedQuantity || 0;
      if (row.status === "surplus") surp++;
      else if (row.status === "shortage") short++;
      else if (row.status === "balanced") bal++;
      else if (row.status === "unavailable") unavail++;

      if (!dateMap[row.date]) {
        dateMap[row.date] = { date: row.date, forecast: 0, planned: 0 };
      }
      dateMap[row.date].forecast += row.forecastedDemand || 0;
      dateMap[row.date].planned += row.plannedQuantity || 0;
    });

    return {
      totalForecast: tf,
      totalPlanned: tp,
      surplusCount: surp,
      shortageCount: short,
      statusData: [
        { name: "Surplus", value: surp, color: CHART_COLORS.surplus },
        { name: "Shortage", value: short, color: CHART_COLORS.shortage },
        { name: "Balanced", value: bal, color: CHART_COLORS.balanced },
        { name: "Unavailable", value: unavail, color: CHART_COLORS.unavailable },
      ].filter(d => d.value > 0),
      trendData: Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date))
    };
  }, [rows]);

  const columns = [
    { header: "Date", accessor: (r: DashboardRow) => r.date },
    { header: "Location", accessor: (r: DashboardRow) => locations[r.locationId] ?? r.locationId },
    { header: "Meal Type", accessor: (r: DashboardRow) => mealTypes[r.mealTypeId] ?? r.mealTypeId },
    { header: "Forecast", accessor: (r: DashboardRow) => <div className="text-right">{r.forecastedDemand ?? "—"}</div> },
    { header: "Planned", accessor: (r: DashboardRow) => <div className="text-right">{r.plannedQuantity ?? "—"}</div> },
    { header: "Status", accessor: (r: DashboardRow) => <StatusBadge status={r.status} /> },
  ];

  return (
    <AppShell>
      <div className="mb-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textPrimary">Dashboard</h1>
          <p className="text-sm font-medium text-textSecondary mt-2">
            Operational summary of forecast demand and food planning.
          </p>
        </div>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <LoadingState text="Loading dashboard data..." className="py-12" />
      ) : rows.length === 0 ? (
        <EmptyState
          title="No upcoming planning data"
          description="There are currently no forecast or planned-quantity records for the upcoming period."
          icon={<Activity size={32} />}
          className="py-16"
        />
      ) : (
        <div className="space-y-6">
          {/* KPIs */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Forecasted Demand"
              value={totalForecast.toLocaleString()}
              icon={<TrendingUp size={16} />}
              description="Total projected meals"
            />
            <StatCard
              label="Planned Quantity"
              value={totalPlanned.toLocaleString()}
              icon={<ClipboardList size={16} />}
              description="Total meals prepared"
            />
            <StatCard
              label="Surplus Incidents"
              value={surplusCount}
              icon={<ArrowUpRight size={16} className="text-statusSurplus" />}
              description="Requires redistribution"
            />
            <StatCard
              label="Shortage Incidents"
              value={shortageCount}
              icon={<ArrowDownRight size={16} className="text-statusShortage" />}
              description="Risk of stockout"
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <ChartCard title="Forecast vs Planned" description="Aggregated by date">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" vertical={false} />
                  <XAxis dataKey="date" stroke="#a3a3a3" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#a3a3a3" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#171717", borderColor: "#2d2d2d", color: "#f5f5f5" }}
                    itemStyle={{ color: "#f5f5f5" }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="forecast" name="Forecasted" fill={CHART_COLORS.forecast} radius={[2, 2, 0, 0]} />
                  <Bar dataKey="planned" name="Planned" fill={CHART_COLORS.planned} radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Status Classification" description="Breakdown of planning status">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    stroke="none"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "rgba(23, 23, 23, 0.9)", backdropFilter: "blur(8px)", borderColor: "#2d2d2d", color: "#f5f5f5", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)" }}
                    itemStyle={{ color: "#f5f5f5", fontSize: "13px", fontWeight: 500 }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '13px', fontWeight: 500, paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Demand Trend" description="Total forecast across all locations" className="lg:col-span-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" vertical={false} />
                  <XAxis dataKey="date" stroke="#a3a3a3" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#a3a3a3" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "rgba(23, 23, 23, 0.9)", backdropFilter: "blur(8px)", borderColor: "#2d2d2d", color: "#f5f5f5", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)" }}
                    itemStyle={{ color: "#f5f5f5", fontSize: "13px", fontWeight: 500 }}
                    labelStyle={{ color: "#a3a3a3", fontSize: "12px", marginBottom: "4px" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="forecast"
                    name="Forecasted Demand"
                    stroke={CHART_COLORS.forecast}
                    strokeWidth={2}
                    dot={{ r: 4, fill: CHART_COLORS.forecast, strokeWidth: 0 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Table Preview */}
          <div>
            <h2 className="mb-4 text-lg font-medium text-textPrimary">Recent Activity</h2>
            <DataTable
              columns={columns}
              data={rows.slice(0, 10)}
              keyExtractor={(r, i) => `${r.date}-${r.locationId}-${r.mealTypeId}-${i}`}
            />
          </div>
        </div>
      )}
    </AppShell>
  );
}
