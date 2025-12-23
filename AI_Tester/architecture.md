┌─────────────────────────────────────────────────────────┐
│  Step 1: Parse OpenAPI Spec (NO LLM - Free!)           │
│  Extract:  endpoints, params, schemas                    │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: Analyze Your Tests (NO LLM - Free!)           │
│  Extract: what's tested, patterns                       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: Identify Gaps (NO LLM - Free!)                │
│  Calculate: untested endpoints, priorities              │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: Generate Basic Tests (NO LLM - Free!)         │
│  Create: happy path, edge cases, validation tests       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  Step 5: LLM Enhancement (USE LLM - Smart!)            │
│  Ask LLM: "What creative edge cases am I missing?"      │
│  Send:  ONLY one endpoint at a time (100 tokens)         │
└─────────────────────────────────────────────────────────┘