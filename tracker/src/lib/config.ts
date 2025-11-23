// Configuration for the order tracker
// These values can be overridden via environment variables

export const config = {
  // Airtable configuration
  airtable: {
    apiKey: process.env.AIRTABLE_API_KEY || "",
    baseId: process.env.AIRTABLE_BASE_ID || "apptAQ1ug44elbkHX",
    tableName: process.env.AIRTABLE_TABLE_NAME || "Orders",
  },

  // Time thresholds in minutes (configurable without redeploy)
  thresholds: {
    // Time in status before showing yellow warning
    yellowMinutes: parseInt(process.env.THRESHOLD_YELLOW_MINUTES || "15", 10),
    // Time in status before showing red alert (cumulative from start)
    redMinutes: parseInt(process.env.THRESHOLD_RED_MINUTES || "45", 10),
  },

  // Polling configuration
  polling: {
    // How often to fetch updates from the server (in seconds)
    intervalSeconds: parseInt(process.env.POLLING_INTERVAL_SECONDS || "30", 10),
    // How often to update the UI timer (in seconds)
    timerTickSeconds: 1,
  },

  // UI configuration
  ui: {
    // Number of items visible in the viewport at once
    visibleItems: 10,
    // Item height for virtualization (in pixels)
    itemHeight: 120,
    // Page size for loading more items
    pageSize: 50,
  },
} as const;

// Validation helper
export function validateConfig(): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (config.thresholds.yellowMinutes <= 0) {
    errors.push("Yellow threshold must be greater than 0");
  }

  if (config.thresholds.redMinutes <= config.thresholds.yellowMinutes) {
    errors.push("Red threshold must be greater than yellow threshold");
  }

  if (config.polling.intervalSeconds < 10) {
    errors.push("Polling interval should be at least 10 seconds to avoid rate limits");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
