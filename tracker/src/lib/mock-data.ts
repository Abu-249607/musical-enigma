import { Order, OrderStatus, Priority } from "@/types/order";

// Generate mock orders for development and testing
// This allows the app to work without Airtable credentials

const statuses: OrderStatus[] = [
  "new",
  "in_progress",
  "pending_review",
  "awaiting_customer",
  "processing",
  "shipped",
];

const priorities: Priority[] = ["low", "medium", "high", "urgent"];

const customers = [
  "Acme Corp",
  "Globex Industries",
  "Initech",
  "Umbrella Corp",
  "Wayne Enterprises",
  "Stark Industries",
  "LexCorp",
  "Cyberdyne Systems",
  "Oscorp",
  "Weyland-Yutani",
];

const channels = ["Web", "Phone", "Email", "Partner", "Referral"];

const assignees = [
  "Alice Johnson",
  "Bob Smith",
  "Carol Williams",
  "David Brown",
  "Eva Martinez",
];

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomMinutesAgo(minMinutes: number, maxMinutes: number): string {
  const minutes = Math.floor(Math.random() * (maxMinutes - minMinutes) + minMinutes);
  const date = new Date(Date.now() - minutes * 60 * 1000);
  return date.toISOString();
}

export function generateMockOrders(count: number = 50): Order[] {
  const orders: Order[] = [];

  for (let i = 1; i <= count; i++) {
    const status = randomItem(statuses);
    const createdMinutesAgo = Math.floor(Math.random() * 2880) + 60; // 1 hour to 48 hours ago
    const statusMinutesAgo = Math.floor(Math.random() * Math.min(createdMinutesAgo, 120)); // up to 2 hours or creation time

    orders.push({
      id: `ORD-${String(i).padStart(5, "0")}`,
      title: `Order #${1000 + i}`,
      status,
      statusEnteredAt: randomMinutesAgo(statusMinutesAgo, statusMinutesAgo + 1),
      customer: randomItem(customers),
      channel: randomItem(channels),
      priority: randomItem(priorities),
      assignee: randomItem(assignees),
      createdAt: randomMinutesAgo(createdMinutesAgo, createdMinutesAgo + 1),
      updatedAt: randomMinutesAgo(statusMinutesAgo, statusMinutesAgo + 1),
      notes: Math.random() > 0.7 ? `Sample note for order ${i}` : undefined,
    });
  }

  return orders;
}

// Pre-generated mock data for consistent development experience
export const MOCK_ORDERS = generateMockOrders(100);

// Mock data with specific scenarios for testing thresholds
export function generateTestScenarios(): Order[] {
  const now = Date.now();

  return [
    {
      id: "TEST-001",
      title: "Just Created",
      status: "new",
      statusEnteredAt: new Date(now - 2 * 60 * 1000).toISOString(), // 2 minutes ago
      customer: "Test Customer 1",
      priority: "high",
      assignee: "Test Assignee",
      createdAt: new Date(now - 2 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 2 * 60 * 1000).toISOString(),
    },
    {
      id: "TEST-002",
      title: "Approaching Yellow",
      status: "in_progress",
      statusEnteredAt: new Date(now - 14 * 60 * 1000).toISOString(), // 14 minutes ago
      customer: "Test Customer 2",
      priority: "medium",
      assignee: "Test Assignee",
      createdAt: new Date(now - 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 14 * 60 * 1000).toISOString(),
    },
    {
      id: "TEST-003",
      title: "Just Turned Yellow",
      status: "pending_review",
      statusEnteredAt: new Date(now - 16 * 60 * 1000).toISOString(), // 16 minutes ago
      customer: "Test Customer 3",
      priority: "high",
      assignee: "Test Assignee",
      createdAt: new Date(now - 2 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 16 * 60 * 1000).toISOString(),
    },
    {
      id: "TEST-004",
      title: "Deep Yellow",
      status: "awaiting_customer",
      statusEnteredAt: new Date(now - 35 * 60 * 1000).toISOString(), // 35 minutes ago
      customer: "Test Customer 4",
      priority: "urgent",
      assignee: "Test Assignee",
      createdAt: new Date(now - 4 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 35 * 60 * 1000).toISOString(),
    },
    {
      id: "TEST-005",
      title: "Just Turned Red",
      status: "processing",
      statusEnteredAt: new Date(now - 46 * 60 * 1000).toISOString(), // 46 minutes ago
      customer: "Test Customer 5",
      priority: "urgent",
      assignee: "Test Assignee",
      createdAt: new Date(now - 8 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 46 * 60 * 1000).toISOString(),
    },
    {
      id: "TEST-006",
      title: "Critical - Long Time",
      status: "in_progress",
      statusEnteredAt: new Date(now - 120 * 60 * 1000).toISOString(), // 2 hours ago
      customer: "Test Customer 6",
      priority: "urgent",
      assignee: "Test Assignee",
      createdAt: new Date(now - 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(now - 120 * 60 * 1000).toISOString(),
    },
  ];
}
