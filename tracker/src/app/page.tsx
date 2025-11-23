"use client";

import { useOrders, useSelectedOrder } from "@/hooks/useOrders";
import { OrderList } from "@/components/OrderList";
import { Filters } from "@/components/Filters";
import { DetailPanel, DetailBackdrop } from "@/components/DetailPanel";
import { StatusBar } from "@/components/StatusBar";
import { config } from "@/lib/config";

export default function Home() {
  const {
    orders,
    filteredOrders,
    loading,
    error,
    source,
    lastUpdated,
    refetch,
    filters,
    setFilters,
    sort,
    setSort,
  } = useOrders();

  const { selectedOrderId, selectedOrder, loading: detailLoading, selectOrder, closeDetail } =
    useSelectedOrder();

  // Count orders by color badge for summary
  const badgeCounts = filteredOrders.reduce(
    (acc, order) => {
      const badge = order.colorBadge || "neutral";
      acc[badge] = (acc[badge] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Order Tracker</h1>
              <p className="text-sm text-gray-500">
                Real-time monitoring of active orders
              </p>
            </div>

            {/* Summary badges */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
                <div className="w-3 h-3 rounded-full bg-gray-300" />
                <span className="text-sm font-medium">{badgeCounts.neutral || 0}</span>
                <span className="text-xs text-gray-500">OK</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-2 bg-amber-50 rounded-lg">
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <span className="text-sm font-medium">{badgeCounts.yellow || 0}</span>
                <span className="text-xs text-gray-500">Warning</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-2 bg-red-50 rounded-lg">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-sm font-medium">{badgeCounts.red || 0}</span>
                <span className="text-xs text-gray-500">Critical</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Status bar */}
      <StatusBar
        source={source}
        lastUpdated={lastUpdated}
        loading={loading}
        error={error}
        onRefresh={refetch}
      />

      {/* Main content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        {/* Filters */}
        <Filters
          filters={filters}
          onFiltersChange={setFilters}
          sort={sort}
          onSortChange={setSort}
          orders={orders}
          totalCount={orders.length}
          filteredCount={filteredOrders.length}
        />

        {/* Order list */}
        <div
          className="bg-gray-50 rounded-lg"
          style={{ height: `${config.ui.visibleItems * config.ui.itemHeight}px` }}
        >
          <OrderList
            orders={filteredOrders}
            selectedOrderId={selectedOrderId}
            onSelectOrder={selectOrder}
            loading={loading}
          />
        </div>

        {/* Threshold info */}
        <div className="mt-4 text-center text-sm text-gray-500">
          <span>
            Thresholds: Warning at {config.thresholds.yellowMinutes}min, Critical at{" "}
            {config.thresholds.redMinutes}min
          </span>
          <span className="mx-2">•</span>
          <span>Auto-refresh every {config.polling.intervalSeconds}s</span>
        </div>
      </main>

      {/* Detail panel overlay */}
      {selectedOrderId && (
        <>
          <DetailBackdrop onClick={closeDetail} />
          <DetailPanel
            order={selectedOrder}
            loading={detailLoading}
            onClose={closeDetail}
          />
        </>
      )}
    </div>
  );
}
