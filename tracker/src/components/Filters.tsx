"use client";

import { useState } from "react";
import {
  Order,
  FilterOptions,
  SortOptions,
  SortField,
  SortDirection,
  OrderStatus,
  Priority,
  STATUS_DISPLAY,
  PRIORITY_DISPLAY,
  TERMINAL_STATUSES,
} from "@/types/order";

interface FiltersProps {
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
  sort: SortOptions;
  onSortChange: (sort: SortOptions) => void;
  orders: Order[]; // For extracting unique assignees
  totalCount: number;
  filteredCount: number;
}

export function Filters({
  filters,
  onFiltersChange,
  sort,
  onSortChange,
  orders,
  totalCount,
  filteredCount,
}: FiltersProps) {
  const [expanded, setExpanded] = useState(false);

  // Get unique assignees from orders
  const uniqueAssignees = Array.from(
    new Set(orders.map((o) => o.assignee).filter((a): a is string => !!a))
  ).sort();

  // Get active (non-terminal) statuses
  const activeStatuses = (Object.keys(STATUS_DISPLAY) as OrderStatus[]).filter(
    (status) => !TERMINAL_STATUSES.includes(status)
  );

  const handleStatusChange = (status: OrderStatus, checked: boolean) => {
    const currentStatuses = filters.status || [];
    const newStatuses = checked
      ? [...currentStatuses, status]
      : currentStatuses.filter((s) => s !== status);
    onFiltersChange({
      ...filters,
      status: newStatuses.length > 0 ? newStatuses : undefined,
    });
  };

  const handlePriorityChange = (priority: Priority, checked: boolean) => {
    const currentPriorities = filters.priority || [];
    const newPriorities = checked
      ? [...currentPriorities, priority]
      : currentPriorities.filter((p) => p !== priority);
    onFiltersChange({
      ...filters,
      priority: newPriorities.length > 0 ? newPriorities : undefined,
    });
  };

  const handleAssigneeChange = (assignee: string, checked: boolean) => {
    const currentAssignees = filters.assignee || [];
    const newAssignees = checked
      ? [...currentAssignees, assignee]
      : currentAssignees.filter((a) => a !== assignee);
    onFiltersChange({
      ...filters,
      assignee: newAssignees.length > 0 ? newAssignees : undefined,
    });
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  const hasActiveFilters =
    (filters.status && filters.status.length > 0) ||
    (filters.priority && filters.priority.length > 0) ||
    (filters.assignee && filters.assignee.length > 0) ||
    filters.minTimeInStatus !== undefined ||
    filters.maxTimeInStatus !== undefined;

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
      {/* Header with sort and expand toggle */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-4">
          <h2 className="font-semibold text-gray-900">
            Orders{" "}
            <span className="text-gray-500 font-normal">
              ({filteredCount} of {totalCount})
            </span>
          </h2>

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear filters
            </button>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* Sort dropdown */}
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Sort by:</label>
            <select
              value={sort.field}
              onChange={(e) =>
                onSortChange({ ...sort, field: e.target.value as SortField })
              }
              className="text-sm border rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="timeInStatus">Time in Status</option>
              <option value="priority">Priority</option>
              <option value="status">Status</option>
              <option value="createdAt">Created</option>
              <option value="title">Title</option>
            </select>
            <button
              onClick={() =>
                onSortChange({
                  ...sort,
                  direction: sort.direction === "asc" ? "desc" : "asc",
                })
              }
              className="p-1 hover:bg-gray-100 rounded"
              title={sort.direction === "asc" ? "Ascending" : "Descending"}
            >
              {sort.direction === "asc" ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              )}
            </button>
          </div>

          {/* Expand/collapse filters */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
          >
            <svg
              className={`w-4 h-4 transition-transform ${expanded ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            Filters
            {hasActiveFilters && (
              <span className="ml-1 px-1.5 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                Active
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Expanded filter options */}
      {expanded && (
        <div className="border-t pt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Status filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Status</h3>
            <div className="space-y-1">
              {activeStatuses.map((status) => (
                <label key={status} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={filters.status?.includes(status) || false}
                    onChange={(e) => handleStatusChange(status, e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  {STATUS_DISPLAY[status].label}
                </label>
              ))}
            </div>
          </div>

          {/* Priority filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Priority</h3>
            <div className="space-y-1">
              {(Object.keys(PRIORITY_DISPLAY) as Priority[]).map((priority) => (
                <label key={priority} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={filters.priority?.includes(priority) || false}
                    onChange={(e) => handlePriorityChange(priority, e.target.checked)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span className={PRIORITY_DISPLAY[priority].color}>
                    {PRIORITY_DISPLAY[priority].label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Assignee filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Assignee</h3>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {uniqueAssignees.length > 0 ? (
                uniqueAssignees.map((assignee) => (
                  <label key={assignee} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={filters.assignee?.includes(assignee) || false}
                      onChange={(e) => handleAssigneeChange(assignee, e.target.checked)}
                      className="rounded text-blue-600 focus:ring-blue-500"
                    />
                    {assignee}
                  </label>
                ))
              ) : (
                <p className="text-sm text-gray-400">No assignees found</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
