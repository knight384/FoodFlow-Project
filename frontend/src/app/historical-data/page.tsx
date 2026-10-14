"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, apiUploadFile, describeApiError } from "@/lib/api";
import type { ImportJobDetail, ImportJobSummary, Paginated } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { Database, Upload, FileText, CheckCircle2, AlertCircle } from "lucide-react";

const PAGE_SIZE = 20;

type UploadState = "idle" | "uploading" | "success" | "error";

export default function HistoricalDataPage() {
  const { token } = useAuth();
  const [jobs, setJobs] = useState<ImportJobSummary[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<ImportJobSummary>["pagination"] | null>(null);
  const [selectedJob, setSelectedJob] = useState<ImportJobDetail | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [fileChosen, setFileChosen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function loadJobs() {
    if (!token) return;
    setLoading(true);
    apiGet<Paginated<ImportJobSummary>>("/historical-data/imports", token, { page, pageSize: PAGE_SIZE })
      .then((res) => {
        setJobs(res.data);
        setPagination(res.pagination);
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }

  useEffect(loadJobs, [token, page]);

  async function handleUpload() {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Please choose a CSV file first.");
      return;
    }
    setError(null);
    setUploadState("uploading");
    try {
      const result = await apiUploadFile<{ importId: string; status: string }>(
        "/historical-data/imports",
        token,
        file,
      );
      if (fileInputRef.current) fileInputRef.current.value = "";
      setFileChosen(false);
      setUploadState(result.status === "failed" ? "error" : "success");
      setPage(1);
      loadJobs();
      viewDetail(result.importId);
    } catch (err) {
      setUploadState("error");
      setError(describeApiError(err));
    }
  }

  async function viewDetail(importId: string) {
    setError(null);
    try {
      const detail = await apiGet<ImportJobDetail>(`/historical-data/imports/${importId}`, token);
      setSelectedJob(detail);
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  const columns = [
    { header: "Uploaded", accessor: (j: ImportJobSummary) => new Date(j.uploadedAt).toLocaleString() },
    { 
      header: "Status", 
      accessor: (j: ImportJobSummary) => (
        <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${
          j.status === "completed" ? "bg-statusSurplus/10 text-statusSurplus border-statusSurplus/20" : 
          j.status === "failed" ? "bg-statusShortage/10 text-statusShortage border-statusShortage/20" : 
          "bg-statusUnavailable/10 text-statusUnavailable border-statusUnavailable/20"
        }`}>
          {j.status.charAt(0).toUpperCase() + j.status.slice(1)}
        </span>
      )
    },
    { header: "Valid", accessor: (j: ImportJobSummary) => <div className="text-right text-textSecondary">{j.validRecords}</div> },
    { header: "Invalid", accessor: (j: ImportJobSummary) => <div className="text-right text-textSecondary">{j.invalidRecords}</div> },
    { 
      header: "", 
      accessor: (j: ImportJobSummary) => (
        <div className="flex justify-end">
          <button
            onClick={() => viewDetail(j.importId)}
            className="text-accent hover:text-accentHover text-xs font-medium"
          >
            View Details
          </button>
        </div>
      )
    },
  ];

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">Historical Data</h1>
        <p className="text-sm text-textSecondary mt-1">
          Import historical consumption data to train forecast models. CSV format must contain: <code className="bg-surfaceHighlight px-1.5 py-0.5 rounded text-xs">date,location,meal_type,actual_consumed_quantity</code>.
        </p>
      </div>

      <div className="card p-4 sm:p-6 mb-6">
        <h2 className="text-sm font-medium text-textPrimary mb-4 flex items-center gap-2">
          <Upload size={16} className="text-accent" />
          Upload Dataset
        </h2>
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="relative flex-1">
            <input
              id="csvFile"
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={() => setFileChosen(!!fileInputRef.current?.files?.[0])}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="flex items-center gap-3 input-field py-2 px-3 border-dashed">
              <FileText size={18} className="text-textSecondary" />
              <span className="text-sm text-textSecondary truncate">
                {fileInputRef.current?.files?.[0]?.name || "Choose CSV file..."}
              </span>
            </div>
          </div>
          <button
            onClick={handleUpload}
            disabled={uploadState === "uploading" || !fileChosen}
            className="btn-primary w-full sm:w-auto flex items-center gap-2"
          >
            <Upload size={16} />
            {uploadState === "uploading" ? "Uploading..." : "Upload File"}
          </button>
        </div>
        
        {uploadState === "success" && (
          <div className="mt-4 flex items-center gap-2 text-sm text-statusSurplus">
            <CheckCircle2 size={16} />
            Import completed successfully. See details below.
          </div>
        )}
        {uploadState === "error" && selectedJob && (
          <div className="mt-4 flex items-center gap-2 text-sm text-statusShortage">
            <AlertCircle size={16} />
            Import finished with validation issues. See details below.
          </div>
        )}
      </div>

      <ErrorBanner message={error} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <h2 className="mb-4 text-lg font-medium text-textPrimary">Import History</h2>
          {loading ? (
             <LoadingState text="Loading imports..." className="py-12 card" />
          ) : (
            <div className="space-y-4">
              <DataTable
                columns={columns}
                data={jobs}
                keyExtractor={(j) => j.importId}
                emptyState={
                  <EmptyState
                    title="No imports yet"
                    description="Upload a CSV file to begin importing historical data."
                    icon={<Database size={32} />}
                    className="py-12"
                  />
                }
              />
              {pagination && jobs.length > 0 && <Pagination meta={pagination} onPageChange={setPage} />}
            </div>
          )}
        </div>

        <div className="lg:col-span-1">
          <h2 className="mb-4 text-lg font-medium text-textPrimary">Import Detail</h2>
          <div className="card h-full min-h-[300px] p-4 flex flex-col">
            {!selectedJob ? (
              <EmptyState
                title="No import selected"
                description="Select an import from the history to view its validation details."
                className="flex-1 border-0 bg-transparent p-0"
              />
            ) : (
              <div className="flex flex-col h-full">
                <div className="mb-4 space-y-2">
                  <div className="text-xs text-textSecondary uppercase tracking-wider font-semibold">Summary</div>
                  <div className="flex justify-between items-center text-sm border-b border-border pb-2">
                    <span className="text-textSecondary">Total Records:</span>
                    <span className="font-medium text-textPrimary">{selectedJob.totalRecords}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm border-b border-border pb-2">
                    <span className="text-textSecondary">Valid Records:</span>
                    <span className="font-medium text-statusSurplus">{selectedJob.validRecords}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm border-b border-border pb-2">
                    <span className="text-textSecondary">Invalid Records:</span>
                    <span className="font-medium text-statusShortage">{selectedJob.invalidRecords}</span>
                  </div>
                </div>

                {selectedJob.errors.length > 0 && (
                  <div className="flex-1 flex flex-col overflow-hidden">
                    <div className="text-xs text-textSecondary uppercase tracking-wider font-semibold mb-2">Errors</div>
                    <ul className="flex-1 overflow-y-auto space-y-2 pr-2 text-sm text-statusShortage bg-statusShortage/5 rounded border border-statusShortage/10 p-3">
                      {selectedJob.errors.map((e, idx) => (
                        <li key={idx} className="flex gap-2">
                          <span className="font-medium whitespace-nowrap">Row {e.rowReference}:</span>
                          <span>{e.failureReason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {selectedJob.errors.length === 0 && selectedJob.totalRecords > 0 && (
                  <div className="flex-1 flex items-center justify-center text-sm text-statusSurplus bg-statusSurplus/5 rounded border border-statusSurplus/10 p-4 text-center">
                    <CheckCircle2 size={24} className="mb-2" />
                    All records were imported successfully.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
