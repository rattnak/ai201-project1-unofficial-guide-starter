# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**Off-campus housing experiences near Boston-area universities** (BU, Northeastern, MIT, Harvard, BC, Tufts, Emerson).

University housing offices publish official policies and lottery rules, but they never tell you which landlords ghost maintenance requests, which buildings have roach problems, or which neighborhoods flood after rain. Students share that knowledge informally, in Reddit threads, Facebook groups, and Google/Yelp reviews, but it's scattered across dozens of sources and hard to search. This RAG system makes that collective knowledge queryable so an incoming student can ask "Is [neighborhood] safe to walk at night?" or "Which management companies have the worst reputation near Northeastern?" and get a grounded, cited answer.

---

## Documents

<!-- Sources collected for the Boston-area off-campus housing domain.
     Mix of Reddit threads, review aggregators, and student-written guides. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/NEU (Northeastern) | Thread: "off campus housing advice / recommendations" — students share neighborhood picks, landlord warnings, and lease tips | https://www.reddit.com/r/NEU/search/?q=off+campus+housing |
| 2 | r/BostonU | Thread: "Where do BU students live off campus?" — South End, Allston, Brighton recs and warnings | https://www.reddit.com/r/BostonU/search/?q=off+campus+housing |
| 3 | r/mit | Thread: "Off-campus housing recommendations in Cambridge/Somerville" | https://www.reddit.com/r/mit/search/?q=off+campus+housing |
| 4 | r/Harvard | Thread: "Best neighborhoods for grad students renting off campus" | https://www.reddit.com/r/harvard/search/?q=off+campus+housing |
| 5 | r/Boston | Thread: "Moving to Boston for college — which neighborhoods to avoid?" — safety, commute, rent discussions | https://www.reddit.com/r/boston/search/?q=college+student+apartment |
| 6 | Google Reviews — Allston landlords | 1-star and 5-star tenant reviews of major property management companies (RIOS, Charlesgate, etc.) near BU/BC | Collected manually from Google Maps searches for "apartment" in Allston 02134 |
| 7 | Yelp — Cambridge/Somerville apartments | Student tenant reviews of complexes near MIT/Harvard (e.g. Windsor, University Park area) | Collected manually from Yelp search "apartments Cambridge MA" |
| 8 | r/NEU wiki / pinned post | Pinned "Housing Megathread" with neighborhood breakdowns, average rents, and lease red flags | https://www.reddit.com/r/NEU/wiki/housing (or top pinned post) |
| 9 | Northeastern Off-Campus Housing student blog post | Unofficial student-written guide on Apartments.com or similar listing sites' forums | Search: "Northeastern off campus housing guide site:apartments.com OR site:apartmentlist.com" |
| 10 | r/Tufts | Thread: "Best off-campus housing near Tufts — Somerville/Medford tips" | https://www.reddit.com/r/Tufts/search/?q=off+campus+housing |
| 11 | r/Emerson | Thread: "Living off campus near Emerson — Downtown Boston tips" | https://www.reddit.com/r/Emerson/search/?q=off+campus+housing |
| 12 | Anonymous tenant reviews — Doorsteps/Zumper | Review aggregator pages for specific Boston student-heavy complexes (e.g. Fenway area, Mission Hill) | https://www.zumper.com/apartments-for-rent/boston-ma (filter by neighborhood, read reviews) |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
