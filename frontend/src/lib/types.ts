/**
 * TypeScript types mirroring the backend's response shapes exactly, per
 * API Specification v1.0. Field names are camelCase throughout, matching
 * the backend's CamelModel JSON boundary (Section 6).
 */

export type Role = "administrator" | "manager" | "operations_staff";

export interface CurrentUser {
  id: string;
  username: string;
  role: Role;
}

export interface Pagination {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export interface User {
  id: string;
  username: string;
  role: Role;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Location {
  id: string;
  name: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface MealType {
  id: string;
  name: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ImportRecordError {
  rowReference: number;
  failureReason: string;
}

export interface ImportJobSummary {
  importId: string;
  uploadedByUserId: string;
  uploadedAt: string;
  status: "processing" | "completed" | "failed";
  totalRecords: number;
  validRecords: number;
  invalidRecords: number;
}

export interface ImportJobDetail extends ImportJobSummary {
  errors: ImportRecordError[];
}

export interface PlannedQuantity {
  id: string;
  planDate: string;
  locationId: string;
  mealTypeId: string;
  quantity: number;
  enteredByUserId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Forecast {
  id: string;
  forecastDate: string;
  locationId: string;
  mealTypeId: string;
  forecastedDemand: number;
  generatedAt: string;
}

export interface ComparisonRow {
  date: string;
  locationId: string;
  mealTypeId: string;
  forecastedDemand: number | null;
  plannedQuantity: number | null;
  potentialSurplus: number | null;
  potentialShortage: number | null;
  variancePercentage: number | null;
}

export type ClassificationStatus = "surplus" | "shortage" | "balanced" | "unavailable";

export interface ClassificationRow {
  date: string;
  locationId: string;
  mealTypeId: string;
  status: ClassificationStatus;
  thresholdApplied: number | null;
}

export interface Recommendation {
  id: string;
  periodDate: string;
  locationId: string;
  mealTypeId: string;
  estimatedSurplusQuantity: number;
  recommendationText: string;
  secondaryLocationId: string | null;
  isAdvisory: boolean;
  generatedAt: string;
}

export interface DashboardRow {
  date: string;
  locationId: string;
  mealTypeId: string;
  forecastedDemand: number | null;
  plannedQuantity: number | null;
  potentialSurplus: number | null;
  potentialShortage: number | null;
  variancePercentage: number | null;
  status: ClassificationStatus;
  recommendation: {
    id: string;
    estimatedSurplusQuantity: number;
    recommendationText: string;
    isAdvisory: boolean;
  } | null;
}

export interface ReportRow {
  date: string;
  locationId: string;
  mealTypeId: string;
  forecastedDemand: number | null;
  plannedQuantity: number | null;
  potentialSurplus: number | null;
  potentialShortage: number | null;
  variancePercentage: number | null;
  status: ClassificationStatus;
}

export interface Paginated<T> {
  data: T[];
  pagination: Pagination;
}
