"use client";

import { useState, useEffect } from "react";

interface ConfigData {
  thresholds: {
    yellowMinutes: number;
    redMinutes: number;
  };
  polling: {
    intervalSeconds: number;
    timerTickSeconds: number;
  };
  ui: {
    visibleItems: number;
    itemHeight: number;
    pageSize: number;
  };
  validation: {
    valid: boolean;
    errors: string[];
  };
}

export function useConfig() {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchConfig() {
      try {
        const response = await fetch("/api/config");
        const data = await response.json();
        setConfig(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load config");
      } finally {
        setLoading(false);
      }
    }

    fetchConfig();
  }, []);

  return { config, loading, error };
}
