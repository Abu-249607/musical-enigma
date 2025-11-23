"use client";

import { Order, STATUS_DISPLAY, PRIORITY_DISPLAY } from "@/types/order";
import { formatDuration, formatDate, getRelativeTime } from "@/lib/time-utils";
import { config } from "@/lib/config";

interface DetailPanelProps {
  order: Order | null;
  loading?: boolean;
  onClose: () => void;
}

export function DetailPanel({ order, loading, onClose }: DetailPanelProps) {
  if (!order && !loading) {
    return null;
  }

  // Color badge styling
  const getBadgeClasses = () => {
    if (!order) return "bg-gray-200 text-gray-700";
    switch (order.colorBadge) {
      case "red":
        return "bg-red-500 text-white";
      case "yellow":
        return "bg-amber-400 text-gray-900";
      default:
        return "bg-gray-200 text-gray-700";
    }
  };

  const getStatusDescription = () => {
    if (!order) return "";
    const timeInMinutes = (order.timeInStatusMs || 0) / (1000 * 60);

    if (order.colorBadge === "red") {
      return `Critical: Over ${config.thresholds.redMinutes} minutes in current status`;
    }
    if (order.colorBadge === "yellow") {
      const remaining = config.thresholds.redMinutes - timeInMinutes;
      return `Warning: ${Math.round(remaining)} minutes until critical`;
    }
    const remaining = config.thresholds.yellowMinutes - timeInMinutes;
    return `${Math.round(remaining)} minutes until warning threshold`;
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-white shadow-xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Order Details</h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-200 rounded-full transition-colors"
          aria-label="Close panel"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : order ? (
          <div className="space-y-6">
            {/* Title and ID */}
            <div>
              <h3 className="text-xl font-bold text-gray-900">{order.title}</h3>
              <p className="text-sm text-gray-500">{order.id}</p>
            </div>

            {/* Time in Status Card */}
            <div className={`rounded-lg p-4 ${getBadgeClasses()}`}>
              <div className="text-sm opacity-80">Time in Current Status</div>
              <div className="text-3xl font-bold mt-1">
                {formatDuration(order.timeInStatusMs || 0)}
              </div>
              <div className="text-sm mt-2 opacity-80">{getStatusDescription()}</div>
            </div>

            {/* Status and Priority */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-500">Status</label>
                <div className="mt-1">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {STATUS_DISPLAY[order.status].label}
                  </span>
                </div>
              </div>
              <div>
                <label className="text-sm text-gray-500">Priority</label>
                <div className={`mt-1 font-medium ${PRIORITY_DISPLAY[order.priority].color}`}>
                  {PRIORITY_DISPLAY[order.priority].label}
                </div>
              </div>
            </div>

            {/* Customer and Channel */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-500">Customer</label>
                <div className="mt-1 font-medium text-gray-900">{order.customer}</div>
              </div>
              {order.channel && (
                <div>
                  <label className="text-sm text-gray-500">Channel</label>
                  <div className="mt-1 font-medium text-gray-900">{order.channel}</div>
                </div>
              )}
            </div>

            {/* Assignee */}
            {order.assignee && (
              <div>
                <label className="text-sm text-gray-500">Assignee</label>
                <div className="mt-1 font-medium text-gray-900">{order.assignee}</div>
              </div>
            )}

            {/* Timestamps */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Timeline</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Created</span>
                  <span className="text-sm text-gray-900">
                    {formatDate(order.createdAt)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Status Changed</span>
                  <span className="text-sm text-gray-900">
                    {formatDate(order.statusEnteredAt)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Last Updated</span>
                  <span className="text-sm text-gray-900">
                    {getRelativeTime(order.updatedAt)}
                  </span>
                </div>
              </div>
            </div>

            {/* Notes */}
            {order.notes && (
              <div className="border-t pt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Notes</h4>
                <p className="text-sm text-gray-600 whitespace-pre-wrap">{order.notes}</p>
              </div>
            )}

            {/* Thresholds Info */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Alert Thresholds</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-gray-200" />
                  <span className="text-gray-600">
                    Normal: &lt; {config.thresholds.yellowMinutes} minutes
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-amber-400" />
                  <span className="text-gray-600">
                    Warning: {config.thresholds.yellowMinutes}–{config.thresholds.redMinutes} minutes
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-gray-600">
                    Critical: &gt; {config.thresholds.redMinutes} minutes
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

// Backdrop for the detail panel
export function DetailBackdrop({ onClick }: { onClick: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/30 z-40"
      onClick={onClick}
      aria-hidden="true"
    />
  );
}
