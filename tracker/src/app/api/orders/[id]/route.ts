import { NextRequest, NextResponse } from "next/server";
import { fetchOrderById } from "@/lib/airtable";
import { MOCK_ORDERS } from "@/lib/mock-data";
import { config } from "@/lib/config";

// GET /api/orders/[id] - Fetch a single order by ID
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const searchParams = request.nextUrl.searchParams;
  const useMock = searchParams.get("mock") === "true";

  try {
    // Check if we should use mock data
    if (useMock || !config.airtable.apiKey) {
      const mockOrder = MOCK_ORDERS.find((o) => o.id === id);
      if (!mockOrder) {
        return NextResponse.json({ error: "Order not found" }, { status: 404 });
      }
      return NextResponse.json({
        order: mockOrder,
        source: "mock",
        timestamp: new Date().toISOString(),
      });
    }

    // Fetch real order from Airtable
    const order = await fetchOrderById(id);

    if (!order) {
      return NextResponse.json({ error: "Order not found" }, { status: 404 });
    }

    return NextResponse.json({
      order,
      source: "airtable",
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Error fetching order:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
