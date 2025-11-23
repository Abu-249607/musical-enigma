import { NextRequest, NextResponse } from "next/server";
import { fetchActiveOrders, checkAirtableConnection } from "@/lib/airtable";
import { MOCK_ORDERS } from "@/lib/mock-data";
import { config } from "@/lib/config";

// GET /api/orders - Fetch all active orders
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const useMock = searchParams.get("mock") === "true";

  try {
    // Check if we should use mock data
    if (useMock || !config.airtable.apiKey) {
      return NextResponse.json({
        orders: MOCK_ORDERS,
        source: "mock",
        timestamp: new Date().toISOString(),
      });
    }

    // Check Airtable connection
    const connectionStatus = await checkAirtableConnection();
    if (!connectionStatus.connected) {
      console.warn("Airtable not connected, using mock data:", connectionStatus.error);
      return NextResponse.json({
        orders: MOCK_ORDERS,
        source: "mock",
        warning: connectionStatus.error,
        timestamp: new Date().toISOString(),
      });
    }

    // Fetch real orders from Airtable
    const orders = await fetchActiveOrders();

    return NextResponse.json({
      orders,
      source: "airtable",
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Error fetching orders:", error);

    // Fallback to mock data on error
    return NextResponse.json(
      {
        orders: MOCK_ORDERS,
        source: "mock",
        error: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
      },
      { status: 200 } // Still return 200 with mock data
    );
  }
}
