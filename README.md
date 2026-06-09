# The Unofficial Guide — Boston Student Off-Campus Housing

A RAG (Retrieval-Augmented Generation) system that makes student-generated knowledge about off-campus housing near Boston-area universities searchable and answerable. Ask a plain-language question; get a grounded, cited answer drawn from real Reddit threads and tenant reviews.

---

## Domain

**Off-campus housing experiences near Boston-area universities** (Northeastern, BU, MIT, Harvard, Tufts, Emerson).

University housing offices publish official policies and lottery rules, but they never tell you which landlords ghost maintenance requests, which buildings have roach problems, or which neighborhoods flood after rain. Students share that knowledge informally — in Reddit threads, Facebook groups, and Yelp/Google reviews — but it's scattered across dozens of sources and hard to search. This system makes that collective knowledge queryable: an incoming student can ask "Is Mission Hill safe?" or "Which landlords in Allston have the worst reviews?" and get a grounded, cited answer.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/NEU — off campus housing thread | Reddit thread | documents/neu_housing_reddit.txt |
| 2 | r/BostonU — where BU students live | Reddit thread | documents/bu_housing_reddit.txt |
| 3 | r/mit — Cambridge/Somerville housing | Reddit thread | documents/mit_cambridge_housing_reddit.txt |
| 4 | r/Tufts — Somerville/Medford tips | Reddit thread | documents/tufts_housing_reddit.txt |
| 5 | r/boston — neighborhoods for students | Reddit thread | documents/boston_general_housing_reddit.txt |
| 6 | r/harvard — grad student housing | Reddit thread | documents/harvard_housing_reddit.txt |
| 7 | r/Emerson — downtown Boston living | Reddit thread | documents/emerson_housing_reddit.txt |
| 8 | Google/Yelp reviews — Allston landlords | Tenant reviews | documents/allston_landlord_reviews.txt |
| 9 | Yelp reviews — Cambridge/Somerville buildings | Tenant reviews | documents/cambridge_somerville_reviews.txt |
| 10 | Zumper/Doorsteps — Fenway/Mission Hill | Tenant reviews | documents/zumper_fenway_reviews.txt |
| 11 | r/NEU housing megathread (wiki) | Pinned guide | documents/neu_housing_megathread.txt |
| 12 | Student-written Boston lease guide | How-to guide | documents/boston_lease_guide.txt |

---

## Chunking Strategy

**Chunk size:** 1,200 characters (~300 tokens)

**Overlap:** 200 characters (~50 tokens)

**Why these choices fit your documents:** The corpus is mostly short Reddit comments and Yelp/Google reviews — individual opinions ranging from one sentence to a short paragraph. A 1,200-character chunk is large enough to capture one complete thought (e.g., a reviewer describing a specific maintenance dispute) without pulling in unrelated opinions from adjacent comments. Anything larger would blend multiple reviewers' distinct experiences into a single chunk, making source attribution unreliable. The 200-character overlap guards against key facts split at chunk boundaries — for example, if a reviewer names a specific street on one line and describes a mold problem on the next. For longer documents (the wiki megathread and lease guide), 1,200 characters maps roughly to one coherent sub-topic per chunk, which is the right retrieval granularity.

The `RecursiveCharacterTextSplitter` respects paragraph and sentence boundaries before falling back to character splitting, so chunks tend to end at natural breaks rather than mid-sentence.

**Preprocessing applied:** Removed Reddit HTML entities (`&amp;`, `&gt;`), `**bold**` markdown, `[deleted]`/`[removed]` placeholders, URL-only lines, and collapsed 3+ consecutive blank lines to 2. Filtered out chunks shorter than 50 characters.

**Final chunk count:** ~180–220 chunks across 12 documents (varies by run; depends on exact document lengths).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`

This model runs locally with no API key, no rate limits, and produces 384-dimension embeddings. It performs well on short opinionated text and is fast enough to embed the full corpus in under a minute on a laptop CPU.

**Production tradeoff reflection:** For a real system serving thousands of daily students, I'd weigh several tradeoffs:

- **Context length:** `all-MiniLM-L6-v2` has a 256-token input limit and silently truncates longer inputs. At 1,200-character (~300 token) chunks, some content is truncated. A model with a longer context window — such as `nomic-embed-text` (8,192 tokens) — would handle the wiki-style long documents without truncation.
- **Accuracy on domain-specific text:** This is a general-purpose model. A model fine-tuned on real estate reviews or housing text would likely improve retrieval precision for domain jargon like "broker fee," "first/last/security," or "heat not included."
- **Cost vs. quality:** OpenAI `text-embedding-3-small` and Cohere `embed-v3` score higher on benchmarks but require API calls and billing. For a free prototype, local inference is the right tradeoff.
- **Multilingual support:** Not needed for this corpus, but relevant if extended to serve international students.

---

## Grounded Generation

**LLM:** Groq `llama-3.3-70b-versatile` (free tier)

**System prompt grounding instruction:**

```
You are The Unofficial Guide — a helpful assistant that answers questions about
off-campus housing near Boston-area universities.

CRITICAL RULES:
1. Answer ONLY using the information in the provided documents. Do not use your general knowledge.
2. If the documents do not contain enough information to answer the question, say exactly:
   "I don't have enough information in my sources to answer that question."
3. Always cite your sources inline using the format [source: filename].
   Every factual claim must have a citation.
4. Do not make up facts, prices, addresses, or advice not present in the documents.
```

**How source attribution is surfaced in the response:** Attribution is enforced two ways. First, the system prompt instructs the model to cite `[source: filename]` inline for every factual claim. Second, the `ask()` function in `app.py` programmatically collects unique source filenames from all retrieved chunks and appends them to the response in a "Retrieved from" panel — so sources are always shown even if the model omits inline citations.

Retrieved chunks are formatted as labeled blocks (`[Document: filename]`) in the user message so the model can reference them by name.

---

## Sample Chunks

Five representative chunks produced by the ingestion pipeline, each with its source document:

**Chunk 1** — `neu_housing_reddit.txt`
> "The biggest thing nobody tells you: Boston leases almost always start September 1st. If you need housing for a January or May co-op start, you'll either sublease or pay rent on an empty room for months. Start looking WAY earlier than you think — like 4-5 months out."

**Chunk 2** — `allston_landlord_reviews.txt`
> "RIOS was the worst landlord I've ever had. The heat went out twice during winter. The first time was 10 days with no heat in February — they said the boiler needed a part and there were supply chain delays. We had to buy space heaters. They did not compensate us for the extra electric bill or reduce rent."

**Chunk 3** — `boston_lease_guide.txt`
> "Many Boston apartments do NOT include heat. This is crucial to understand: Gas heat: You pay the gas bill directly. In an old, poorly-insulated triple-decker, this can be $150-400/month in winter. Electric baseboard heat: The most expensive option. Can be $300-500/month in a poorly-insulated apartment."

**Chunk 4** — `tufts_housing_reddit.txt`
> "Davis Square in Somerville is the gold standard for Tufts students. You're right on the Red Line, there are tons of restaurants and bars, and it has a great neighborhood feel. The downside: it's gotten expensive. A room in a 3-bed near Davis runs $1,350-1,500/month now."

**Chunk 5** — `mission_hill_safety_reviews.txt`
> "I've lived in Mission Hill for 3 years now and my honest take: it depends entirely on which part and what time. The area immediately around Huntington Ave — especially the blocks between NEU's campus and Brigham and Women's Hospital — is totally fine. Lots of students, hospital workers, foot traffic at all hours."

---

## Retrieval Test Results

**Query 1: "What do students say about landlords in Allston?"**

Top returned chunks:
- `allston_landlord_reviews.txt` (distance: 0.18) — RIOS heat outage and security deposit dispute
- `allston_landlord_reviews.txt` (distance: 0.21) — Charlesgate mold response time
- `bu_housing_reddit.txt` (distance: 0.29) — warning about Charlesgate, advice to talk to current tenants
- `allston_landlord_reviews.txt` (distance: 0.31) — positive review of owner-occupied building on Pratt Street

*Why relevant:* All top chunks are directly about landlord experiences in Allston — specific company names, specific problems (mice, mold, heat, deposits). Distance scores below 0.35 indicate strong semantic matches.

---

**Query 2: "What lease red flags should Boston students watch out for?"**

Top returned chunks:
- `neu_housing_megathread.txt` (distance: 0.17) — lease red flags list (no move-in inspection, utilities not specified, no subletting clause)
- `boston_lease_guide.txt` (distance: 0.19) — red flags list (cash only, verbal lease, security deposit over 1 month)
- `boston_general_housing_reddit.txt` (distance: 0.28) — broker fee explanation and September 1st lease tips
- `neu_housing_reddit.txt` (distance: 0.33) — advice to read lease, check sublease policy

*Why relevant:* The top two chunks are purpose-built lists of lease red flags from two different sources, giving the model multiple perspectives. The lower-ranked chunks add context on broker fees and the September 1st problem, which are Boston-specific lease issues.

---

**Query 3: "Is Mission Hill safe for college students at night?"**

Top returned chunks:
- `mission_hill_safety_reviews.txt` (distance: 0.14) — 3-year resident breakdown by area and time of day
- `mission_hill_safety_reviews.txt` (distance: 0.22) — crime statistics comparison vs. Back Bay/Fenway
- `neu_housing_reddit.txt` (distance: 0.38) — general note about Mission Hill being fine near Huntington Ave
- `neu_housing_megathread.txt` (distance: 0.41) — neighborhood safety note in the Mission Hill entry

*Why relevant:* The top two chunks are from the dedicated safety document with the most specific information. Distance scores are low, indicating the query is well-matched to the document content.

---

## Example Responses

**Example 1 — grounded response with citations**

*Query:* "What do students say about landlords in Allston?"

*Response:*
> Students have mixed reviews about landlords in Allston. One reviewer had a very positive experience with a private landlord who owns the building himself, citing prompt responses to maintenance issues and fair rent increases [source: allston_landlord_reviews.txt]. However, another student warned about Charlesgate Realty, which had mixed reviews and was slow to address a mold problem [source: bu_housing_reddit.txt]. A former tenant described RIOS Management as the worst landlord they'd had — the heat went out twice during winter, and when they moved out RIOS kept the entire security deposit without justification, requiring a small claims court filing to recover it [source: allston_landlord_reviews.txt]. Students are advised to ask current tenants about pest issues before signing, as older Allston buildings may have problems with mice [source: bu_housing_reddit.txt].

*Retrieved from:* allston_landlord_reviews.txt, bu_housing_reddit.txt, harvard_housing_reddit.txt, boston_general_housing_reddit.txt

---

**Example 2 — grounded response with citations**

*Query:* "What lease red flags should Boston students watch out for?"

*Response:*
> Boston students should watch out for several lease red flags. These include: no written move-in inspection form [source: neu_housing_megathread.txt], heat and utilities not specified in the lease [source: neu_housing_megathread.txt], a "no subletting" clause which is a dealbreaker for co-op students [source: neu_housing_megathread.txt], and vague damage clauses [source: neu_housing_megathread.txt]. Additionally, students should be cautious of leases with no written promises, no lease at all (month-to-month verbal arrangements are extremely risky), security deposits over 1 month's rent (illegal in Massachusetts), and landlords who ask for cash only [source: boston_lease_guide.txt]. It's also important to insist on a written move-in inspection or photograph everything with timestamped photos [source: boston_lease_guide.txt].

*Retrieved from:* neu_housing_reddit.txt, boston_lease_guide.txt, boston_general_housing_reddit.txt, neu_housing_megathread.txt

---

**Example 3 — out-of-scope refusal**

*Query:* "What are the best restaurants near Harvard Medical School?"

*Response:*
> I don't have enough information in my sources to answer that question.

*Why:* The corpus contains no restaurant reviews or HMS-specific content. The system correctly declined rather than generating a plausible-sounding answer from general knowledge.

---

## Query Interface

The interface is a Gradio web app launched with `python app.py`, accessible at `http://localhost:7860`.

**Input fields:**
- *Your question* — a free-text box where the user types any plain-language question about Boston student housing. Pressing Enter or clicking "Ask" submits it.

**Output fields:**
- *Answer* — the LLM-generated response, grounded in retrieved documents with inline `[source: filename]` citations
- *Retrieved from* — a list of the source documents whose chunks were used to construct the answer

**Sample interaction transcript:**

```
Input:  Which neighborhoods near Northeastern have the cheapest rent?

Answer: According to the NEU housing megathread, the cheapest neighborhoods
        near Northeastern are Roxbury Crossing ($950-1,150/month per person)
        and parts of Jamaica Plain ($1,050-1,300/month per person)
        [source: neu_housing_megathread.txt]. Mission Hill is the next tier
        at $1,100-1,300/month, followed by Fenway at $1,400-1,800/month
        [source: neu_housing_megathread.txt]. One student noted that Roxbury
        Crossing is only 2 Orange Line stops from campus, making it a good
        value option despite being farther from campus than Mission Hill
        [source: neu_housing_reddit.txt].

Retrieved from:
• neu_housing_megathread.txt
• neu_housing_reddit.txt
• boston_lease_guide.txt
• boston_general_housing_reddit.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about landlords in Allston? | Multiple reviewers describe slow maintenance, specific companies (Charlesgate, RIOS), specific problems (mice, mold, heat, deposits) | Cited Charlesgate and RIOS by name, described 3-week mouse response time, RIOS heat outage, security deposit dispute. Cited allston_landlord_reviews.txt and bu_housing_reddit.txt. | Relevant | Accurate |
| 2 | Is Mission Hill safe for college students at night? | Sources note mixed picture — fine near Huntington Ave, more variable on side streets; property crime (bikes) common; violent crime against students rare | Correctly conveyed the nuanced picture: safe near Huntington Ave, more variable on side streets, property crime common, recommended normal urban precautions. Cited mission_hill_safety_reviews.txt. | Relevant | Accurate |
| 3 | Which neighborhoods near Northeastern have the cheapest rent? | Roxbury Crossing ($950-1,150/mo), parts of JP ($1,050-1,300/mo) cheaper than Mission Hill or Fenway | Correctly identified Roxbury Crossing as cheapest, JP as affordable mid-tier, cited specific price ranges from neu_housing_megathread.txt. | Relevant | Accurate |
| 4 | What lease red flags should Boston students watch out for? | Should mention: broker fees, no written move-in inspection, heat not included, no subletting clause, security deposit >1 month | Correctly listed 5+ red flags with specifics, cited boston_lease_guide.txt and neu_housing_megathread.txt. Included broker fee, heat, subletting clause, move-in inspection. | Relevant | Accurate |
| 5 | What are students' experiences with off-campus housing near Tufts in Somerville or Medford? | Sources describe Davis Square as popular but expensive ($1,350-1,500/mo), Medford cheaper ($1,050/mo), Ball Square as underrated middle ground, September 1st lease problem | System retrieved tufts_housing_reddit.txt correctly but mixed in one chunk from cambridge_somerville_reviews.txt about MIT students. The Davis Square and Medford price ranges were correct but the answer conflated a Somerville review from a non-Tufts source with the Tufts-specific thread. | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "What are students' experiences with off-campus housing near Tufts in Somerville or Medford?"

**What the system returned:** The answer correctly cited Davis Square prices ($1,350-1,500/month) and Medford as cheaper, but included a detail from `cambridge_somerville_reviews.txt` about a Somerville landlord who was described in the context of MIT students — not Tufts students. The distinction was lost because both chunks mention Somerville and Davis Square, and the embedding model assigned them similar distances.

**Root cause (tied to a specific pipeline stage):** This is a **retrieval failure caused by geographic overlap between university-specific documents**. The query "near Tufts" is semantically similar to any document mentioning Somerville, Davis Square, or the Red Line — regardless of which university the review is about. The `all-MiniLM-L6-v2` model embeds geographic terms (Somerville, Davis Square) with high weight, and the source university (Tufts vs. MIT) is not a strong enough signal in a 1,200-character chunk to differentiate the results. The chunk from `cambridge_somerville_reviews.txt` about an MIT student in Somerville scored a distance of 0.31 — close enough to appear in the top-5 alongside the genuinely Tufts-specific chunks.

**What you would change to fix it:** Two improvements would address this. First, adding **metadata filtering** — tagging each chunk with the university it pertains to (derived from the source filename) and filtering retrieval to only return chunks from relevant sources when the query names a specific school. Second, including the source university name in the chunk text during ingestion (e.g., prepending "Tufts student review:" to each chunk from the Tufts document) would give the embedding model a stronger signal to distinguish university-specific content.

---

**Question that failed:** "What is the average security deposit amount in Boston?"

**What the system returned:**

> The average security deposit in Boston is up to 1 month's rent, as stated by Massachusetts law [source: boston_lease_guide.txt]. For example, for a $1,200/month apartment, the security deposit would be up to $1,200 [source: boston_lease_guide.txt].

*Retrieved from:* boston_lease_guide.txt, cambridge_somerville_reviews.txt, neu_housing_megathread.txt, emerson_housing_reddit.txt

**Why this is a partial failure:** The answer is technically correct but incomplete — it only cites one source inline (`boston_lease_guide.txt`) while the "Retrieved from" panel lists four sources. The three additional chunks (cambridge_somerville_reviews.txt, neu_housing_megathread.txt, emerson_housing_reddit.txt) were retrieved as relevant context but contributed nothing to the final answer, and no inline citation was generated for them. A better response would have surfaced any corroborating details from those chunks (e.g., student-reported deposit disputes or advice from the NEU megathread) or, if those chunks were truly off-topic, they should not have been in the top-4 retrieved results.

**Root cause (tied to a specific pipeline stage):** This is a **generation + retrieval mismatch**. The retriever correctly found the authoritative chunk in `boston_lease_guide.txt` but also pulled in three loosely related chunks that mention deposits only in passing (e.g., a review mentioning a landlord kept a deposit, or a thread comment about first/last/security). The LLM correctly ignored the off-topic chunks rather than hallucinating, but the result is that cited sources in the answer (1) don't match the full retrieved set (4) — creating a transparency gap for the user.

**What you would change to fix it:** Two improvements would address this. First, **raising the similarity threshold** for retrieval (or reducing `k` from 4 to 3) would avoid pulling in weakly-related chunks that don't actually contribute. Second, updating the system prompt to instruct the model to either cite every retrieved document or explicitly note "the other retrieved documents did not contain additional relevant information" would make the gap visible to the user rather than silently dropping sources.

---

## Spec Reflection

**One way the spec helped you during implementation:** The chunking strategy section of planning.md specified 1,200-character chunks with 200-character overlap before a single line of code was written. This made the `ingest.py` implementation straightforward — the parameters were already decided and justified, so there was no temptation to just use a default value. More importantly, the reasoning in the spec (short review text warrants smaller chunks to avoid blending reviewers' opinions) gave a clear criterion for evaluating whether the chunks looked right at the inspection step.

**One way your implementation diverged from the spec, and why:** The spec called for using `RecursiveCharacterTextSplitter` with `chunk_size=1200, chunk_overlap=200` in character units, which matches the implementation. However, the spec framed chunk size in "tokens (~300)" while the implementation correctly uses characters (which is what LangChain's splitter accepts). The spec was slightly imprecise on this point — 300 tokens is approximately 1,200 characters for English text, but they are not the same unit and the distinction matters when the embedding model has a 256-token limit. The implementation used characters throughout to be consistent with LangChain's API, which is the right call.

---

## AI Usage

**Instance 1 — Ingestion and chunking pipeline**

- *What I gave the AI:* The Chunking Strategy and Documents sections of planning.md, plus the requirement that the pipeline must load `.txt` files, clean Reddit formatting artifacts, and output chunks with source metadata preserved.
- *What it produced:* `ingest.py` with `load_documents()`, `clean_text()`, and `chunk_documents()` functions using `RecursiveCharacterTextSplitter` at the specified parameters. The cleaning function covered HTML entities, markdown bold/italic, and `[deleted]` placeholders.
- *What I changed or overrode:* The initial version used `chunk_size=300` (treating it as tokens). I corrected this to `chunk_size=1200` in character units to match LangChain's API. I also added a `len(piece) > 50` filter to drop trivially short fragments, which the AI-generated version didn't include.

**Instance 2 — Grounded generation system prompt**

- *What I gave the AI:* The grounding requirement from the project spec ("answers from retrieved context only, with source attribution"), the output format (answer + inline citations + source list), and the pipeline diagram from planning.md.
- *What it produced:* A system prompt and `ask()` function that passed retrieved chunks as context and instructed the model to cite sources.
- *What I changed or overrode:* The initial system prompt said "try to answer only from the documents." I hardened this to "Answer ONLY using the information in the provided documents. Do not use your general knowledge." — the word "try" leaves too much room for the model to fall back on training data. I also added the explicit fallback instruction ("say exactly: 'I don't have enough information'") which the AI-generated version omitted, and added programmatic source collection in `ask()` to guarantee attribution even if the model's inline citations are incomplete.
