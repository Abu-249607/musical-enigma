import { NextResponse } from "next/server";
import { config, validateConfig } from "@/lib/config";

// GET /api/config - Get public configuration (thresholds, polling intervals)
// Note: This does NOT expose sensitive data like API keys
export async function GET() {
  const validation = validateConfig();

  return NextResponse.json({
    thresholds: config.thresholds,
    polling: config.polling,
    ui: config.ui,
    validation,
    timestamp: new Date().toISOString(),
  });
}
