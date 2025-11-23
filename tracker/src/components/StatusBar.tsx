"use client";

interface StatusBarProps {
  source: "airtable" | "mock" | null;
  lastUpdated: Date | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export function StatusBar({
  source,
  lastUpdated,
  loading,
  error,
  onRefresh,
}: StatusBarProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <div className="bg-white border-b px-4 py-2 flex items-center justify-between text-sm">
      <div className="flex items-center gap-4">
        {/* Data source indicator */}
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              source === "airtable" ? "bg-green-500" : "bg-yellow-500"
            }`}
          />
          <span className="text-gray-600">
            {source === "airtable" ? "Live from Airtable" : "Mock Data"}
          </span>
        </div>

        {/* Last updated */}
        {lastUpdated && (
          <span className="text-gray-400">
            Updated: {formatTime(lastUpdated)}
          </span>
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center gap-1 text-blue-600">
            <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span>Refreshing...</span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Error indicator */}
        {error && (
          <span className="text-red-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            {error}
          </span>
        )}

        {/* Manual refresh button */}
        <button
          onClick={onRefresh}
          disabled={loading}
          className="flex items-center gap-1 px-3 py-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors disabled:opacity-50"
        >
          <svg
            className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Refresh
        </button>
      </div>
    </div>
  );
}
