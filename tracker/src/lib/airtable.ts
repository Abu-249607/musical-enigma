import { Order, AirtableRecord, OrderStatus, Priority, TERMINAL_STATUSES } from "@/types/order";
import { config } from "./config";

// Airtable API client for server-side use only
// Never expose API keys to the client

const AIRTABLE_API_URL = "https://api.airtable.com/v0";

interface AirtableResponse {
  records: AirtableRecord[];
  offset?: string;
}

interface FetchOptions {
  filterByFormula?: string;
  maxRecords?: number;
  pageSize?: number;
  offset?: string;
  sort?: Array<{ field: string; direction: "asc" | "desc" }>;
}

/**
 * Fetch records from Airtable with pagination support
 */
async function fetchAirtableRecords(options: FetchOptions = {}): Promise<AirtableResponse> {
  if (!config.airtable.apiKey) {
    throw new Error("Airtable API key not configured");
  }

  const url = new URL(
    `${AIRTABLE_API_URL}/${config.airtable.baseId}/${encodeURIComponent(config.airtable.tableName)}`
  );

  // Build query parameters
  if (options.filterByFormula) {
    url.searchParams.set("filterByFormula", options.filterByFormula);
  }
  if (options.maxRecords) {
    url.searchParams.set("maxRecords", String(options.maxRecords));
  }
  if (options.pageSize) {
    url.searchParams.set("pageSize", String(options.pageSize));
  }
  if (options.offset) {
    url.searchParams.set("offset", options.offset);
  }
  if (options.sort) {
    options.sort.forEach((sortItem, index) => {
      url.searchParams.set(`sort[${index}][field]`, sortItem.field);
      url.searchParams.set(`sort[${index}][direction]`, sortItem.direction);
    });
  }

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${config.airtable.apiKey}`,
      "Content-Type": "application/json",
    },
    // Cache for a short time to reduce API calls
    next: { revalidate: 10 },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Airtable API error: ${response.status} - ${error}`);
  }

  return response.json();
}

/**
 * Map Airtable status string to our OrderStatus type
 */
function mapStatus(status: string | undefined): OrderStatus {
  if (!status) return "new";

  const normalized = status.toLowerCase().replace(/\s+/g, "_");

  const statusMap: Record<string, OrderStatus> = {
    new: "new",
    in_progress: "in_progress",
    "in progress": "in_progress",
    pending_review: "pending_review",
    "pending review": "pending_review",
    awaiting_customer: "awaiting_customer",
    "awaiting customer": "awaiting_customer",
    processing: "processing",
    shipped: "shipped",
    closed_won: "closed_won",
    "closed won": "closed_won",
    closed_lost: "closed_lost",
    "closed lost": "closed_lost",
  };

  return statusMap[normalized] || "new";
}

/**
 * Map Airtable priority string to our Priority type
 */
function mapPriority(priority: string | undefined): Priority {
  if (!priority) return "medium";

  const normalized = priority.toLowerCase();

  const priorityMap: Record<string, Priority> = {
    low: "low",
    medium: "medium",
    high: "high",
    urgent: "urgent",
    critical: "urgent",
  };

  return priorityMap[normalized] || "medium";
}

/**
 * Transform an Airtable record to our Order type
 */
function transformRecord(record: AirtableRecord): Order {
  const fields = record.fields;

  return {
    id: record.id,
    title: fields.Title || `Order ${record.id}`,
    status: mapStatus(fields.Status),
    statusEnteredAt: fields["Status Entered At"] || record.createdTime,
    customer: fields.Customer || "Unknown",
    channel: fields.Channel,
    priority: mapPriority(fields.Priority),
    assignee: fields.Assignee,
    createdAt: record.createdTime,
    updatedAt: record.createdTime, // Airtable doesn't have a native updated field
    notes: fields.Notes,
  };
}

/**
 * Fetch all active orders (excluding terminal statuses)
 */
export async function fetchActiveOrders(): Promise<Order[]> {
  // Build filter formula to exclude terminal statuses
  const terminalStatusFilters = TERMINAL_STATUSES.map(
    (status) => `{Status} != '${status.replace(/_/g, " ")}'`
  ).join(", ");

  const filterFormula = `AND(${terminalStatusFilters})`;

  const allOrders: Order[] = [];
  let offset: string | undefined;

  // Paginate through all records
  do {
    const response = await fetchAirtableRecords({
      filterByFormula: filterFormula,
      pageSize: 100,
      offset,
    });

    const orders = response.records.map(transformRecord);
    allOrders.push(...orders);
    offset = response.offset;
  } while (offset);

  return allOrders;
}

/**
 * Fetch a single order by ID
 */
export async function fetchOrderById(orderId: string): Promise<Order | null> {
  if (!config.airtable.apiKey) {
    throw new Error("Airtable API key not configured");
  }

  const url = `${AIRTABLE_API_URL}/${config.airtable.baseId}/${encodeURIComponent(
    config.airtable.tableName
  )}/${orderId}`;

  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${config.airtable.apiKey}`,
      "Content-Type": "application/json",
    },
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Airtable API error: ${response.status} - ${error}`);
  }

  const record: AirtableRecord = await response.json();
  return transformRecord(record);
}

/**
 * Check if Airtable is configured and accessible
 */
export async function checkAirtableConnection(): Promise<{
  connected: boolean;
  error?: string;
}> {
  if (!config.airtable.apiKey) {
    return { connected: false, error: "API key not configured" };
  }

  try {
    await fetchAirtableRecords({ maxRecords: 1 });
    return { connected: true };
  } catch (error) {
    return {
      connected: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}
