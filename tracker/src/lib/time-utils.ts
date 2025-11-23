import { ColorBadge } from "@/types/order";
import { config } from "./config";

/**
 * Calculate time elapsed since a given date in milliseconds
 * Handles clock skew and invalid dates gracefully
 */
export function getTimeInStatusMs(statusEnteredAt: string | undefined | null): number {
  if (!statusEnteredAt) {
    return 0;
  }

  try {
    const enteredAt = new Date(statusEnteredAt).getTime();
    const now = Date.now();

    // Guard against future dates (clock skew)
    if (enteredAt > now) {
      return 0;
    }

    // Guard against invalid dates
    if (isNaN(enteredAt)) {
      return 0;
    }

    return now - enteredAt;
  } catch {
    return 0;
  }
}

/**
 * Determine the color badge based on time in status
 */
export function getColorBadge(timeInStatusMs: number): ColorBadge {
  const timeInMinutes = timeInStatusMs / (1000 * 60);

  if (timeInMinutes >= config.thresholds.redMinutes) {
    return "red";
  }

  if (timeInMinutes >= config.thresholds.yellowMinutes) {
    return "yellow";
  }

  return "neutral";
}

/**
 * Format milliseconds as a human-readable duration
 * e.g., "2h 15m", "45m", "5m 30s"
 */
export function formatDuration(ms: number): string {
  if (ms <= 0) {
    return "0m";
  }

  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }

  return `${seconds}s`;
}

/**
 * Format milliseconds as a compact duration (for tight spaces)
 * e.g., "2:15:00", "0:45:30"
 */
export function formatDurationCompact(ms: number): string {
  if (ms <= 0) {
    return "0:00";
  }

  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }

  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

/**
 * Get time remaining until next threshold
 */
export function getTimeUntilNextThreshold(timeInStatusMs: number): {
  threshold: "yellow" | "red" | null;
  remainingMs: number;
} | null {
  const timeInMinutes = timeInStatusMs / (1000 * 60);

  if (timeInMinutes >= config.thresholds.redMinutes) {
    // Already at red, no next threshold
    return null;
  }

  if (timeInMinutes >= config.thresholds.yellowMinutes) {
    // At yellow, next is red
    const remainingMs = (config.thresholds.redMinutes - timeInMinutes) * 60 * 1000;
    return { threshold: "red", remainingMs };
  }

  // At neutral, next is yellow
  const remainingMs = (config.thresholds.yellowMinutes - timeInMinutes) * 60 * 1000;
  return { threshold: "yellow", remainingMs };
}

/**
 * Format a date for display
 */
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return "Unknown";
    }
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "Unknown";
  }
}

/**
 * Get relative time description
 * e.g., "5 minutes ago", "2 hours ago", "yesterday"
 */
export function getRelativeTime(dateString: string): string {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return "Unknown";
    }

    const now = Date.now();
    const diffMs = now - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) {
      return "just now";
    }
    if (diffMinutes < 60) {
      return `${diffMinutes}m ago`;
    }
    if (diffHours < 24) {
      return `${diffHours}h ago`;
    }
    if (diffDays === 1) {
      return "yesterday";
    }
    if (diffDays < 7) {
      return `${diffDays}d ago`;
    }

    return formatDate(dateString);
  } catch {
    return "Unknown";
  }
}
