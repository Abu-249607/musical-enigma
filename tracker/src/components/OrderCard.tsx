"use client";

import { Order, STATUS_DISPLAY, PRIORITY_DISPLAY } from "@/types/order";
import { formatDuration, getRelativeTime } from "@/lib/time-utils";

interface OrderCardProps {
  order: Order;
  onClick?: () => void;
  isSelected?: boolean;
}

export function OrderCard({ order, onClick, isSelected }: OrderCardProps) {
  const statusInfo = STATUS_DISPLAY[order.status];
  const priorityInfo = PRIORITY_DISPLAY[order.priority];

  // Color badge styling
  const getBadgeClasses = () => {
    switch (order.colorBadge) {
      case "red":
        return "bg-red-500 text-white animate-pulse";
      case "yellow":
        return "bg-amber-400 text-gray-900";
      default:
        return "bg-gray-200 text-gray-700";
    }
  };

  // Border color based on urgency
  const getBorderClasses = () => {
    switch (order.colorBadge) {
      case "red":
        return "border-l-4 border-l-red-500";
      case "yellow":
        return "border-l-4 border-l-amber-400";
      default:
        return "border-l-4 border-l-gray-200";
    }
  };

  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-lg shadow-sm p-4 cursor-pointer
        transition-all duration-200 hover:shadow-md
        ${getBorderClasses()}
        ${isSelected ? "ring-2 ring-blue-500" : ""}
      `}
    >
      {/* Header row */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{order.title}</h3>
          <p className="text-sm text-gray-500 truncate">{order.id}</p>
        </div>

        {/* Time in status badge */}
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getBadgeClasses()}`}>
          {formatDuration(order.timeInStatusMs || 0)}
        </div>
      </div>

      {/* Status and Priority row */}
      <div className="flex items-center gap-2 mb-3">
        <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
          {statusInfo.label}
        </span>
        <span className={`text-xs font-medium ${priorityInfo.color}`}>
          {priorityInfo.label}
        </span>
      </div>

      {/* Info row */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <div className="flex items-center gap-4">
          {/* Customer */}
          <div className="flex items-center gap-1">
            <svg
              className="w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
            <span className="truncate max-w-[120px]">{order.customer}</span>
          </div>

          {/* Assignee */}
          {order.assignee && (
            <div className="flex items-center gap-1">
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="truncate max-w-[100px]">{order.assignee}</span>
            </div>
          )}
        </div>

        {/* Created time */}
        <span className="text-xs text-gray-400">{getRelativeTime(order.createdAt)}</span>
      </div>

      {/* Channel badge */}
      {order.channel && (
        <div className="mt-2">
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
            {order.channel}
          </span>
        </div>
      )}
    </div>
  );
}
