\# 🚀 Setup Guide - Enterprise AI BI Platform



\## ⚡ Quick Start (3 Steps)



\### Step 1: Clone \& Install

```bash

git clone https://github.com/YOUR-USERNAME/Enterprise-AI-Business-Intelligence-Platform.git

cd Enterprise-AI-Business-Intelligence-Platform

```



\### Step 2: Configure Environment Variables



\*\*Create a `.env.docker` file\*\* (this file is NOT committed to Git):



```bash

cp .env.example .env.docker

```



\*\*Then edit `.env.docker` with your actual values:\*\*



```bash

\# ==========================================

\# REQUIRED: LLM Provider Configuration

\# ==========================================



\# Option A: OpenAI (Official)

OPENAI\_API\_KEY=sk-your-openai-api-key-here

\# OPENAI\_BASE\_URL=  # Leave empty for official OpenAI

\# OPENAI\_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4o-mini



\# Option B: OpenAI-Compatible Router (byNara, DeepInfra, Together, etc.)

\# OPENAI\_API\_KEY=sk-your-router-key-here

\# OPENAI\_BASE\_URL=https://router.bynara.id/v1

\# OPENAI\_MODEL=qwen-3.8-max-free



\# Other Router Examples:

\# OPENAI\_BASE\_URL=https://api.deepinfra.com/v1

\# OPENAI\_MODEL=microsoft/Phi-3-mini-128k-instruct

\# OPENAI\_BASE\_URL=https://api.together.xyz/v1

\# OPENAI\_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1



\# ==========================================

\# Database Configuration (Neon Cloud - Recommended)

\# ==========================================

\# Get your free database at: https://neon.tech (0.5GB free)

POSTGRES\_HOST=ep-xxx.region.neon.tech

POSTGRES\_PORT=5432

POSTGRES\_DB=neondb

POSTGRES\_USER=neondb\_owner

POSTGRES\_PASSWORD=your-password



\# Async URL (required for SQLAlchemy async)

DATABASE\_URL=postgresql+asyncpg://neondb\_owner:your-password@ep-xxx.region.neon.tech/neondb?sslmode=require



\# ==========================================

\# Security

\# ==========================================

SECRET\_KEY=your-random-secret-key-here-min-32-chars

```



\### Step 3: Run with Docker

```bash

docker compose up -d --build

```



That's it! 🎉 Visit http://localhost:8000/docs for Swagger UI.



\---



\## 🔑 Where to Get API Keys?



\### Database (Required - Free Tier Available)



| Provider | Free Tier | URL | Setup |

|----------|-----------|-----|-------|

| \*\*Neon\*\* ✅ | 0.5 GB | https://neon.tech | \[Sign Up Free](https://console.neon.tech/create) |

| \*\*Supabase\*\* | 500 MB | https://supabase.com | \[Start Free](https://supabase.com) |

| \*\*Render\*\* | ❌ Expired | - | Upgrade required |



> \*\*💡 Recommendation:\*\* Use \[Neon](https://neon.tech) - it's free, serverless, and no credit card needed!



\### LLM Providers



| Provider | Free Tier | URL | Get Key |

|----------|-----------|-----|---------|

| \*\*OpenAI\*\* | ✅ $5 credit | https://platform.openai.com | \[Get Key](https://platform.openai.com/api-keys) |

| \*\*byNara Router\*\* | ✅ Free models | https://router.bynara.id | Sign up |

| \*\*DeepInfra\*\* | ✅ Free tier | https://deepinfra.com | \[Get Key](https://deepinfra.com/dashboard/keys) |

| \*\*Together AI\*\* | ✅ $5 credit | https://together.ai | \[Get Key](https://api.together.xyz/settings/api-keys) |

| \*\*Groq\*\* | ✅ Free tier | https://groq.com | \[Get Key](https://console.groq.com/keys) |



\---



\## 📋 Environment Variables Reference



\### Required Variables



| Variable | Description | Example |

|----------|-------------|---------|

| `OPENAI\_API\_KEY` | Your LLM provider API key | `sk-...` |

| `SECRET\_KEY` | JWT signing key (random string) | `my-super-secret-12345` |

| `DATABASE\_URL` | Neon PostgreSQL connection string | `postgresql+asyncpg://...` |



\### Optional Variables



| Variable | Description | Default |

|----------|-------------|---------|

| `OPENAI\_BASE\_URL` | Custom endpoint URL | `https://api.openai.com/v1` |

| `OPENAI\_MODEL` | Model name | `gpt-3.5-turbo` |

| `POSTGRES\_HOST` | Database host (Neon) | `ep-xxx.neon.tech` |

| `POSTGRES\_DB` | Database name | `neondb` |

| `POSTGRES\_PASSWORD` | PostgreSQL password | From Neon dashboard |



\---



\## 🐘 Setting Up Neon Database (Free)



\### 1. Create Neon Account

1\. Go to \[console.neon.tech](https://console.neon.tech/create)

2\. Sign up with GitHub/Google (free, no credit card)

3\. Create a new project



\### 2. Get Connection String

1\. In your project dashboard → \*\*Connection Details\*\*

2\. Copy the connection string

3\. It looks like: `postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require`



\### 3. Update `.env.docker`

```bash

\# Replace with your actual values from Neon dashboard

POSTGRES\_HOST=ep-wild-grass-ax5sozbb-pooler.c-4.us-east-2.aws.neon.tech

POSTGRES\_PORT=5432

POSTGRES\_DB=neondb

POSTGRES\_USER=neondb\_owner

POSTGRES\_PASSWORD=your-password



\# Async URL (copy this format exactly)

DATABASE\_URL=postgresql+asyncpg://neondb\_owner:your-password@ep-wild-grass-ax5sozbb-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require

```



\### 4. Run Docker

```bash

docker compose up -d --build

```



> ✅ \*\*No local PostgreSQL needed!\*\* Neon is cloud-based and auto-scales.



\---



\## 🔧 Troubleshooting



\### "OPENAI\_API\_KEY environment variable is required"

```bash

\# You forgot to set the API key in .env.docker

echo "OPENAI\_API\_KEY=your-key" >> .env.docker

docker compose restart api

```



\### "Authentication failed with LLM provider"

```bash

\# Your API key is invalid or expired

\# Check your key at your provider's dashboard

```



\### "Rate limit exceeded"

```bash

\# You've hit the free tier limit

\# Options:

\# 1. Wait for reset (usually daily)

\# 2. Upgrade to paid plan

\# 3. Use a different provider/model

```



\---



\## 🛡️ Security Notes



✅ \*\*Safe to commit to GitHub:\*\*

\- `.env.example` (contains only placeholders)

\- `docker-compose.yml` (references env vars)

\- All Python files (no hardcoded secrets)



❌ \*\*Never commit to GitHub:\*\*

\- `.env` or `.env.docker` (contains real keys)

\- Any file with actual API keys or passwords



These are already in `.gitignore`!



\---



\## 🎯 Quick Test After Setup



Once running, test the AI Copilot:



```bash

curl -X POST http://localhost:8000/auth/register \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"email": "test@example.com", "password": "testpass123"}'



\# Then login and query:

curl -X POST http://localhost:8000/copilot/query \\

&#x20; -H "Authorization: Bearer YOUR\_TOKEN" \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"question": "What are total sales?"}

```



\---



\## Need Help?



\- 📖 Full Documentation: See \[README.md](README.md)

\- 🐛 Issues: \[GitHub Issues](https://github.com/YOUR-USERNAME/issues)

\- 💬 Discussions: \[GitHub Discussions](https:///github.com/YOUR-USERNAME/discussions)



\---



\*\*Happy Coding! 🚀\*\*



