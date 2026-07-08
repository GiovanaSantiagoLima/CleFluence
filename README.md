# CléFluence

**An integrated French learning ecosystem, powered by AI.**

CléFluence maps a learner's progression across the four core language skills — **listening**, **reading**, **writing**, and **speaking** — combining curated, level-appropriate content, a personal knowledge graph of learning progress, and lightweight AI only where it actually adds judgment. The goal is a product that feels adaptive and alive, built on an architecture that stays cheap enough to run in production on a portfolio budget.

---

## The 4 pillars

Language fluency isn't one skill, it's four moving in parallel. CléFluence is designed around that from the ground up:

| Pillar | What it does | Status |
|---|---|---|
| 🎧 **Listen** | Curated audio content by CEFR level — podcasts, radio, TV clips | Planned (phase 1) |
| 📖 **Read** | Curated news/text content by difficulty level | Planned (phase 1) |
| ✍️ **Write** | Vocabulary, connectors, and CEFR-level feedback on written production | Designed (phase 2) |
| 🗣️ **Speak** | Pronunciation feedback via speech-to-text + phonetic comparison | Designed (phase 3) |

Each pillar generates its own signal — words learned, connectors mastered, recurring errors, pronunciation gaps — that all feed into a single progression graph per learner.

## Design philosophy: expensive AI only where it earns its keep

A recurring temptation with "AI-powered" language apps is to throw a large model at every step. CléFluence deliberately doesn't:

- **Listening & reading are aggregation, not generation.** High-quality, free sources already exist — RFI Savoirs' *Journal en français facile* (audio + transcript + level built in), TV5Monde's *Apprendre le français* (leveled A1–C2 video), France Inter, and 1jour1actu (news simplified for beginners). A scheduled scraper/aggregator pulls their RSS feeds, and a cheap LLM (e.g. Claude Haiku) classifies each piece by CEFR level using a fixed rubric — it never needs to touch the audio itself, only the text/transcript. This is also how the cold-start "empty database" problem gets solved: real, well-produced content from day one, without writing a single lesson from scratch.
- **Writing** uses spaCy for structural/grammatical analysis plus an LLM agent (with a rubric + RAG) for feedback — already scoped in earlier design work.
- **Speaking** is the hardest and most technically interesting pillar, and the one place a heavier local model is worth it: Whisper (OpenAI's open-source speech-to-text, run locally — no per-minute API cost) transcribes what the learner said, and a phonetic comparison layer (`epitran` or `phonemizer` to convert target French text to IPA) diffs it against the reference to flag where pronunciation likely drifted.
- The LLM is only invoked where judgment is genuinely required: CEFR classification, writing correction, feedback generation. Everything else is deterministic pipeline work.

## Data architecture

Three specialized databases, each solving one problem, all on free/near-free tiers:

| Database | Role | Tier |
|---|---|---|
| **MongoDB Atlas** | Curated content corpus + embeddings, semantic search via Atlas Vector Search | Free tier (512MB is enough to start) |
| **Neo4j Aura** | The learner's progression graph — vocabulary, connectors, recurring errors, pronunciation gaps, and how they connect over time | Aura Free |
| **Redis** | Cache for expensive lookups (search, graph aggregations) + session state | Redis Cloud / Upstash free tier |

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   MongoDB Atlas  │      │   Neo4j Aura      │      │      Redis      │
│  corpus + vector │      │  progression      │      │  cache/session  │
│                  │      │  graph            │      │                 │
└────────┬─────────┘      └─────────┬────────┘      └────────┬────────┘
         │                          │                         │
         └──────────────┬───────────┴─────────────────────────┘
                         │
                   ┌─────▼─────┐
                   │  API REST │
                   │ (FastAPI) │
                   └───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
  Content scraper    Cheap LLM         Whisper (local)
  (RFI, TV5Monde,   (classification,  + phonetic diff
   1jour1actu)        feedback)       (epitran/phonemizer)
```

## Stack

- **Backend:** Python + FastAPI
- **Document store / vector search:** MongoDB Atlas (Atlas Vector Search)
- **Graph database:** Neo4j Aura
- **Cache / session:** Redis

## Project structure

```
app/

  db/
    mongodb.py         # Atlas connection + vector search
    neo4j_db.py        # Neo4j connection + Cypher queries
    redis_db.py        # cache and session state
  schemas/             # Pydantic request/response models
  routers/
    users.py           # learner profile
    content.py          # content CRUD + semantic search
    progress.py          # vocabulary, connectors, errors on the graph
  ingestion/            # (planned) RFI/TV5Monde/1jour1actu scraper + CEFR classifier
  speech/               # (planned) Whisper transcription + phonetic scoring
  main.py                # API entry point
  config.py         # settings via environment variables
requirements.txt

```

