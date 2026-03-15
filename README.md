# Jira Ticket Evaluator

An **AI-powered semantic verification tool** that automatically checks whether a GitHub Pull Request actually satisfies the requirements in a Jira ticket. Built with a 10-stage agentic AI pipeline using AWS Bedrock, FastAPI, and Next.js.

---

## Live Deployments

| Service | URL |
|---|---|
| **Frontend (Vercel)** | [https://jira-ticket-evaluator.vercel.app](https://jira-ticket-evaluator.vercel.app) |
| **Backend API (CloudFront)** | [https://d2bhn20vt8mwic.cloudfront.net](https://d2bhn20vt8mwic.cloudfront.net) |
| **API Health Check** | [https://d2bhn20vt8mwic.cloudfront.net/](https://d2bhn20vt8mwic.cloudfront.net/) |

---
## Demo

Given a **Jira Ticket ID** (e.g., `PROJ-123`) and a **GitHub PR URL**, the tool:
1. Fetches the Jira ticket requirements
2. Fetches the PR code diff
3. Runs a full AI evaluation pipeline
4. Returns a **PASS / PARTIAL / FAIL** verdict per requirement with AI confidence scores and code evidence

---

## Architecture

```
Browser → Vercel (Next.js) → CloudFront (HTTPS) → EC2 (FastAPI + Docker)
                                                          ↓
                                                   AI Pipeline (10 Stages)
                                                          ↓
                                                    AWS DynamoDB
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 16** (TypeScript) | Web app & API proxy to backend |
| **Framer Motion** | Animations |
| **Lucide Icons** | UI icons |
| **Tailwind CSS** | Styling |
| **Vercel** | Deployment |

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI + Uvicorn** | REST API framework |
| **AWS Bedrock (Amazon Nova Pro/Lite)** | LLM for AI reasoning stages |
| **Amazon Titan Embeddings v2** | Semantic code search |
| **AWS DynamoDB** | Evaluation result storage |
| **MCP (Model Context Protocol)** | GitHub integration |
| **Jira REST API v3** | Jira ticket fetching |
| **Docker** | Containerized backend |
| **AWS EC2** | Backend hosting |
| **AWS CloudFront** | HTTPS CDN layer |

---

## The 10-Stage AI Pipeline

| Stage | Module | Description |
|---|---|---|
| **1** | `main.py` | Request received & validated |
| **2** | `jira_mcp_client.py` | Fetches Jira ticket via REST API v3 |
| **2.5** | `planner_agent.py` | **Planner Agent** — uses Amazon Nova Pro to dynamically decide the execution plan based on ticket type |
| **3** | `ticket_parser.py` | Parses Jira ticket into structured requirements with classification |
| **4** | `github_mcp_client.py` | Fetches GitHub PR metadata + raw code diff via GitHub MCP server |
| **5** | `pr_analyzer.py` | Analyzes PR structure, changed files and maps them to requirements |
| **5.5** | `context_retriever.py` | Fetches additional codebase context from GitHub for deeper analysis |
| **6** | `semantic_search.py` | Semantic + keyword search using Titan Embeddings to find relevant code chunks per requirement |
| **7** | `evidence_finder.py` | AI maps each requirement to actual code evidence with validation |
| **8** | `test_generator.py` | Generates and runs synthetic test cases (skipped for refactor tickets) |
| **9** | `verdict_agent.py` | Produces final PASS / PARTIAL / FAIL verdict per requirement |
| **10** | `dynamodb_client.py` | Persists the full result to AWS DynamoDB |

> **Note**: Stages 2 and 4 run **concurrently** using `asyncio.gather()` for speed.

---
## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 20+
- AWS Account with Bedrock access (Nova Pro, Nova Lite, Titan Embeddings)
- Jira Cloud account with API token
- GitHub Personal Access Token

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the server
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy and fill in environment variables
cp .env.example .env
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Run the development server
npm run dev
```

Frontend runs at `http://localhost:3000`

---

## 🔧 Environment Variables

### Backend (`.env`)

```env
# AWS (for Bedrock & DynamoDB)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Jira
JIRA_API_TOKEN=your_jira_personal_access_token
JIRA_EMAIL=your_jira_account_email
JIRA_DOMAIN=your_company.atlassian.net

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat

# Server
PORT=8000
HOST=0.0.0.0
```

### Frontend (`.env`)

```env
# Must include https:// protocol prefix!
NEXT_PUBLIC_API_URL=https://d2bhn20vt8mwic.cloudfront.net
```

> **Important**: Always include `https://` in `NEXT_PUBLIC_API_URL` — missing the protocol prefix will cause a 503 error in production.

---

## Docker Deployment (Backend)

```bash
cd backend

# Build the image
docker build -t jira-evaluator-backend .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  jira-evaluator-backend
```

The Dockerfile:
- Uses `python:3.11-slim` base
- Installs Node.js 20 (required for GitHub MCP via `npx`)
- Exposes port `8000`
- Runs `uvicorn main:app --host 0.0.0.0 --port 8000`

---

## Project Structure

```
Jira_Ticket_Evaluator/
├── frontend/                        # Next.js web app
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx             # Main UI
│   │       └── api/evaluate/
│   │           └── route.ts         # Backend proxy API route
│   ├── .env.example
│   └── package.json
│
└── backend/                         # FastAPI Python backend
    ├── main.py                      # FastAPI app + pipeline orchestrator
    ├── bedrock_client.py            # AWS Bedrock (Nova + Titan) client
    ├── jira_mcp_client.py           # Jira REST API integration (Stage 2)
    ├── github_mcp_client.py         # GitHub MCP server integration (Stage 4)
    ├── planner_agent.py             # Dynamic execution planner (Stage 2.5)
    ├── ticket_parser.py             # Requirement extraction (Stage 3)
    ├── pr_analyzer.py               # PR structure analysis (Stage 5)
    ├── context_retriever.py         # Codebase context fetcher (Stage 5.5)
    ├── semantic_search.py           # Embedding-based code search (Stage 6)
    ├── evidence_finder.py           # AI evidence mapper (Stage 7)
    ├── test_generator.py            # Synthetic test generator (Stage 8)
    ├── verdict_agent.py             # Final verdict generator (Stage 9)
    ├── dynamodb_client.py           # DynamoDB persistence (Stage 10)
    ├── Dockerfile
    ├── requirements.txt
    └── .env.example
```

---

## API Reference

### `GET /`
Health check.
```json
{"status": "Backend is running"}
```

### `POST /api/evaluate`
Runs the full AI evaluation pipeline.

**Request Body:**
```json
{
  "jira_id": "DEV-4",
  "github_pr_url": "https://github.com/owner/repo/pull/45"
}
```

**Response:**
```json
{
  "overall_verdict": "PASS",
  "summary": "2 of 2 requirements implemented.",
  "planner_decisions": "This is a feature ticket...",
  "requirements": [
    {
      "id": 1,
      "statement": "Reset email must be sent to the user",
      "verdict": "PASS",
      "evidence": "auth.js line 5",
      "confidence": 0.90,
      "test_result": "PASS"
    }
  ],
  "evaluation_id": "abc123"
}
```

---

## AI Models Used

| Model | Usage |
|---|---|
| `us.amazon.nova-pro-v1:0` | Planner Agent, Evidence Finder, Verdict Agent |
| `us.amazon.nova-lite-v1:0` | Ticket Parser, PR Analyzer, Test Generator |
| `amazon.titan-embed-text-v2:0` | Semantic code chunk embeddings |

---

## Built With

- [AWS Bedrock](https://aws.amazon.com/bedrock/) — Amazon Nova AI models
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — GitHub tool integration
- [FastAPI](https://fastapi.tiangolo.com/) — Python backend
- [Next.js](https://nextjs.org/) — React frontend
- [Vercel](https://vercel.com/) — Frontend hosting
- [AWS EC2 + CloudFront](https://aws.amazon.com/) — Backend hosting & HTTPS
