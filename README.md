# Order Tracker Web App

A real-time order tracking dashboard that visualizes active orders and flags items needing attention based on time spent in their current status.

## Features

- **Real-time Order Tracking**: Live updates of order statuses from Airtable
- **Visual Alert System**: Color-coded badges (neutral → yellow → red) based on time thresholds
- **Virtualized List**: Handles 1,200+ records efficiently, rendering only visible items
- **Filtering & Sorting**: Filter by status, priority, assignee; sort by time in status
- **Detail Panel**: Click any order to see full metadata and history
- **Auto-refresh**: Configurable polling interval with manual refresh option

## Time Thresholds

- **Neutral (gray)**: Order in status < 15 minutes
- **Warning (yellow)**: Order in status ≥ 15 minutes
- **Critical (red)**: Order in status ≥ 45 minutes

Thresholds are configurable via environment variables without code changes.

## Tech Stack

- **Frontend**: Next.js 16 with React 19, TypeScript
- **Styling**: Tailwind CSS 4
- **Virtualization**: @tanstack/react-virtual for performance
- **Data Source**: Airtable API with server-side proxy

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Airtable account with API access

### Installation

```bash
cd tracker
npm install
```

### Configuration

Create a `.env.local` file in the `tracker` directory:

```env
# Airtable Configuration
AIRTABLE_API_KEY=your_personal_access_token_here
AIRTABLE_BASE_ID=apptAQ1ug44elbkHX
AIRTABLE_TABLE_NAME=Orders

# Threshold Configuration (in minutes)
THRESHOLD_YELLOW_MINUTES=15
THRESHOLD_RED_MINUTES=45

# Polling interval (in seconds)
POLLING_INTERVAL_SECONDS=30
```

### Running the App

```bash
# Development mode with hot reload
npm run dev

# Production build
npm run build
npm start
```

The app will be available at `http://localhost:3000`

## Airtable Schema

The app expects an Airtable table with these fields:

| Field Name | Type | Description |
|------------|------|-------------|
| Title | Single line text | Order title/reference |
| Status | Single select | Current status (new, in_progress, pending_review, etc.) |
| Status Entered At | Date/time | When the order entered current status |
| Customer | Single line text | Customer name |
| Channel | Single select | Order channel (Web, Phone, Email, etc.) |
| Priority | Single select | low, medium, high, urgent |
| Assignee | Single line text | Assigned team member |
| Notes | Long text | Additional notes |

### Terminal Statuses

Orders with these statuses are automatically hidden from the active view:
- `closed won`
- `closed lost`

## Mock Data Mode

The app automatically falls back to mock data when:
- Airtable API key is not configured
- Airtable connection fails
- `?mock=true` query parameter is added to API requests

This allows development and testing without Airtable access.

## Project Structure

```
tracker/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── api/          # API routes (server-side proxy)
│   │   ├── page.tsx      # Main dashboard
│   │   └── layout.tsx    # Root layout
│   ├── components/       # React components
│   │   ├── OrderCard.tsx
│   │   ├── OrderList.tsx
│   │   ├── Filters.tsx
│   │   ├── DetailPanel.tsx
│   │   └── StatusBar.tsx
│   ├── hooks/            # Custom React hooks
│   │   ├── useOrders.ts
│   │   └── useConfig.ts
│   ├── lib/              # Utility functions
│   │   ├── airtable.ts   # Airtable API client
│   │   ├── config.ts     # Configuration
│   │   ├── mock-data.ts  # Mock data generator
│   │   └── time-utils.ts # Time calculations
│   └── types/            # TypeScript types
│       └── order.ts
├── .env.example          # Environment variables template
└── package.json
```

## API Endpoints

- `GET /api/orders` - Fetch all active orders
- `GET /api/orders/[id]` - Fetch single order by ID
- `GET /api/config` - Get public configuration (thresholds, polling)

## Security

- API keys are stored server-side only
- All Airtable requests are proxied through Next.js API routes
- No sensitive data is exposed to the client

## License

MIT
