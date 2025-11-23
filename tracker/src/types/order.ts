// Order status types
export type OrderStatus =
  | "new"
  | "in_progress"
  | "pending_review"
  | "awaiting_customer"
  | "processing"
  | "shipped"
  | "closed_won"
  | "closed_lost";

// Terminal statuses that should be hidden from active view
export const TERMINAL_STATUSES: OrderStatus[] = ["closed_won", "closed_lost"];

// Status display configuration
export const STATUS_DISPLAY: Record<OrderStatus, { label: string; order: number }> = {
  new: { label: "New", order: 1 },
  in_progress: { label: "In Progress", order: 2 },
  pending_review: { label: "Pending Review", order: 3 },
  awaiting_customer: { label: "Awaiting Customer", order: 4 },
  processing: { label: "Processing", order: 5 },
  shipped: { label: "Shipped", order: 6 },
  closed_won: { label: "Closed Won", order: 7 },
  closed_lost: { label: "Closed Lost", order: 8 },
};

// Priority levels
export type Priority = "low" | "medium" | "high" | "urgent";

export const PRIORITY_DISPLAY: Record<Priority, { label: string; order: number; color: string }> = {
  low: { label: "Low", order: 1, color: "text-gray-500" },
  medium: { label: "Medium", order: 2, color: "text-blue-500" },
  high: { label: "High", order: 3, color: "text-orange-500" },
  urgent: { label: "Urgent", order: 4, color: "text-red-600" },
};

// Color badge types for time thresholds
export type ColorBadge = "neutral" | "yellow" | "red";

// Main Order interface
export interface Order {
  id: string;
  title: string;
  status: OrderStatus;
  statusEnteredAt: string; // ISO date string
  customer: string;
  channel?: string;
  priority: Priority;
  assignee?: string;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  notes?: string;
  // Computed fields (calculated client-side)
  timeInStatusMs?: number;
  colorBadge?: ColorBadge;
}

// Airtable record structure (raw from API)
export interface AirtableRecord {
  id: string;
  createdTime: string;
  fields: {
    Title?: string;
    Status?: string;
    "Status Entered At"?: string;
    Customer?: string;
    Channel?: string;
    Priority?: string;
    Assignee?: string;
    Notes?: string;
  };
}

// Filter options
export interface FilterOptions {
  status?: OrderStatus[];
  assignee?: string[];
  priority?: Priority[];
  minTimeInStatus?: number; // in minutes
  maxTimeInStatus?: number; // in minutes
}

// Sort options
export type SortField = "timeInStatus" | "status" | "priority" | "createdAt" | "title";
export type SortDirection = "asc" | "desc";

export interface SortOptions {
  field: SortField;
  direction: SortDirection;
}
