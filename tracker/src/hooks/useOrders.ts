"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Order, FilterOptions, SortOptions, TERMINAL_STATUSES } from "@/types/order";
import { getTimeInStatusMs, getColorBadge } from "@/lib/time-utils";
import { config } from "@/lib/config";

interface OrdersResponse {
  orders: Order[];
  source: "airtable" | "mock";
  error?: string;
  warning?: string;
  timestamp: string;
}

interface UseOrdersResult {
  orders: Order[];
  filteredOrders: Order[];
  loading: boolean;
  error: string | null;
  source: "airtable" | "mock" | null;
  lastUpdated: Date | null;
  refetch: () => Promise<void>;
  filters: FilterOptions;
  setFilters: (filters: FilterOptions) => void;
  sort: SortOptions;
  setSort: (sort: SortOptions) => void;
}

// Compute derived fields for an order
function enrichOrder(order: Order): Order {
  const timeInStatusMs = getTimeInStatusMs(order.statusEnteredAt);
  const colorBadge = getColorBadge(timeInStatusMs);

  return {
    ...order,
    timeInStatusMs,
    colorBadge,
  };
}

// Apply filters to orders
function applyFilters(orders: Order[], filters: FilterOptions): Order[] {
  return orders.filter((order) => {
    // Exclude terminal statuses from active view
    if (TERMINAL_STATUSES.includes(order.status)) {
      return false;
    }

    // Filter by status
    if (filters.status && filters.status.length > 0) {
      if (!filters.status.includes(order.status)) {
        return false;
      }
    }

    // Filter by assignee
    if (filters.assignee && filters.assignee.length > 0) {
      if (!order.assignee || !filters.assignee.includes(order.assignee)) {
        return false;
      }
    }

    // Filter by priority
    if (filters.priority && filters.priority.length > 0) {
      if (!filters.priority.includes(order.priority)) {
        return false;
      }
    }

    // Filter by min time in status
    if (filters.minTimeInStatus !== undefined) {
      const timeInMinutes = (order.timeInStatusMs || 0) / (1000 * 60);
      if (timeInMinutes < filters.minTimeInStatus) {
        return false;
      }
    }

    // Filter by max time in status
    if (filters.maxTimeInStatus !== undefined) {
      const timeInMinutes = (order.timeInStatusMs || 0) / (1000 * 60);
      if (timeInMinutes > filters.maxTimeInStatus) {
        return false;
      }
    }

    return true;
  });
}

// Apply sorting to orders
function applySort(orders: Order[], sort: SortOptions): Order[] {
  const sorted = [...orders];

  sorted.sort((a, b) => {
    let comparison = 0;

    switch (sort.field) {
      case "timeInStatus":
        comparison = (a.timeInStatusMs || 0) - (b.timeInStatusMs || 0);
        break;
      case "status":
        comparison = a.status.localeCompare(b.status);
        break;
      case "priority": {
        const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
        comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
        break;
      }
      case "createdAt":
        comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
        break;
      case "title":
        comparison = a.title.localeCompare(b.title);
        break;
    }

    return sort.direction === "desc" ? -comparison : comparison;
  });

  return sorted;
}

export function useOrders(): UseOrdersResult {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<"airtable" | "mock" | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({});
  const [sort, setSort] = useState<SortOptions>({
    field: "timeInStatus",
    direction: "desc",
  });

  // Track timer updates
  const [, setTimerTick] = useState(0);

  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch("/api/orders");
      const data: OrdersResponse = await response.json();

      if (data.error) {
        setError(data.error);
      }

      // Enrich orders with computed fields
      const enrichedOrders = data.orders.map(enrichOrder);
      setOrders(enrichedOrders);
      setSource(data.source);
      setLastUpdated(new Date(data.timestamp));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch orders");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // Polling for updates
  useEffect(() => {
    const interval = setInterval(fetchOrders, config.polling.intervalSeconds * 1000);
    return () => clearInterval(interval);
  }, [fetchOrders]);

  // Timer tick for updating time displays
  useEffect(() => {
    const interval = setInterval(() => {
      setTimerTick((t) => t + 1);
      // Re-enrich orders to update time calculations
      setOrders((prev) => prev.map(enrichOrder));
    }, config.polling.timerTickSeconds * 1000);

    return () => clearInterval(interval);
  }, []);

  // Apply filters and sorting
  const filteredOrders = applySort(applyFilters(orders, filters), sort);

  return {
    orders,
    filteredOrders,
    loading,
    error,
    source,
    lastUpdated,
    refetch: fetchOrders,
    filters,
    setFilters,
    sort,
    setSort,
  };
}

// Hook for selecting a single order
export function useSelectedOrder() {
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(false);

  const selectOrder = useCallback(async (orderId: string | null) => {
    setSelectedOrderId(orderId);

    if (!orderId) {
      setSelectedOrder(null);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/orders/${orderId}`);
      const data = await response.json();

      if (data.order) {
        setSelectedOrder(enrichOrder(data.order));
      }
    } catch (err) {
      console.error("Failed to fetch order details:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const closeDetail = useCallback(() => {
    setSelectedOrderId(null);
    setSelectedOrder(null);
  }, []);

  return {
    selectedOrderId,
    selectedOrder,
    loading,
    selectOrder,
    closeDetail,
  };
}
