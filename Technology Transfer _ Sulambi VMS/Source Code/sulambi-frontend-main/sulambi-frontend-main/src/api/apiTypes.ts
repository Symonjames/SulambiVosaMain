/** Payload shapes returned by backend for cached fetches (after axios unwrap). */

export interface EventsListPayload {
  events?: unknown[];
  external?: unknown[];
  internal?: unknown[];
}

export interface SatisfactionAnalyticsPayload {
  success?: boolean;
  data?: {
    satisfactionData?: unknown[];
    topIssues?: unknown[];
    volunteerCount?: number;
    beneficiaryCount?: number;
    totalCount?: number;
  };
}

export interface DashboardSummaryPayload {
  data?: Record<string, unknown>;
}

/** Dashboard analytics body (may nest `data` again depending on backend). */
export interface DashboardAnalyticsPayload {
  data?: {
    data?: Record<string, unknown>;
    sexGroup?: Record<string, unknown>;
    ageGroup?: Record<string, unknown>;
  } & Record<string, unknown>;
}

export interface ReportsListPayload {
  external?: unknown[];
  internal?: unknown[];
}
