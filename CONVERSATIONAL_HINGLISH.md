# Conversational Hinglish Data Collection

**Goal:** Expand conversational Hinglish data from ~2.8M to 15-30M tokens.

## New Collection Scripts

### 1. Extended Reddit Collection
**Script:** `scripts/collect_reddit_extended.py`
**Target:** 10-20M tokens
**Status:** ⏳ Running

**Subreddits Covered (18 total):**

**Bollywood & Movies:**
- `r/bollywood` - Bollywood discussions
- `r/BollyBlindsNGossip` - Very active, casual Hinglish gossip
- `r/indiancinema` - Indian cinema discussions

**Sports:**
- `r/Cricket` - Cricket (huge in India, very conversational)
- `r/indiancricket` - Indian cricket specifically

**Entertainment & Pop Culture:**
- `r/IndianDankMemes` - Very Hinglish memes/culture
- `r/IndiaNostalgia` - Nostalgia discussions
- `r/indianews` - Indian news

**Regional (diverse language):**
- `r/Chennai`
- `r/Hyderabad`
- `r/Pune`
- `r/Kolkata`

**General Indian:**
- `r/india`
- `r/AskIndia`
- `r/IndianTeenagers`

**Music:**
- `r/indianmusic`
- `r/bollywoodmusic`

**Key Changes from Original:**
- **100 posts per subreddit** (vs 50 previously)
- **No political filter** (user requested political content)
- **More permissive validation** (3-200 words vs 5-150)
- **Focus on entertainment/culture** for natural Hinglish

**Expected Output:** `data/raw/reddit_extended.txt`

---

### 2. Movie Subtitles Collection
**Script:** `scripts/collect_movie_subtitles.py`
**Target:** 5-10M tokens
**Status:** ⏳ Ready to run

**Source:** OpenSubtitles dataset (Helsinki-NLP/open_subtitles)
**Language:** English-Hindi pairs (common in Bollywood)

**Processing:**
- Cleans timing codes, HTML tags, stage directions
- Removes music/sound indicators
- Groups dialogues into conversation windows (~10 lines each)
- 50% overlap between windows for context

**Expected Output:** `data/raw/movie_subtitles.txt`

**Note:** OpenSubtitles dataset may require manual setup. If automated collection fails:
- Download manually from OpenSubtitles.org (Hindi/Bollywood filter)
- Alternative: Subscene.com Hindi section

---

## Running the Collections

### Extended Reddit (running now):
```bash
conda activate llm_project
python scripts/collect_reddit_extended.py
```

**Estimated time:** ~2-3 hours (18 subreddits × 100 posts each)
**Rate limiting:** 0.5s between posts, 2s between subreddits

### Movie Subtitles:
```bash
python scripts/collect_movie_subtitles.py
```

**Estimated time:** ~1-2 hours (streaming large dataset)
**Note:** May require manual intervention if dataset loading fails

---

## Expected Results

### After Extended Reddit Collection:

| Source | Tokens | Type |
|--------|--------|------|
| WhatsApp | 894k | Conversational (existing) |
| Hinglish public | 873k | Conversational (existing) |
| Reddit (original) | 1,044k | Conversational (existing) |
| **Reddit (extended)** | **10-20M** | **Conversational (NEW)** |
| **Subtotal** | **~13-23M** | **Conversational Hinglish** |

### After Movie Subtitles Collection:

| Source | Tokens | Type |
|--------|--------|------|
| Conversational (above) | 13-23M | Reddit + WhatsApp + Hinglish |
| **Movie Subtitles** | **5-10M** | **Dialogue (NEW)** |
| **Total Conversational** | **~18-33M** | **All conversational sources** |

---

## Updated Dataset Breakdown (After All Collections)

### Conversational: ~18-33M tokens (9-17%)
- WhatsApp, Hinglish public, Reddit (original + extended), Movie subtitles

### Knowledge (English): ~192M tokens (78-82%)
- WikiText-103, Full Wikipedia, Simple Wikipedia, Wiki intros

### Reasoning: ~1.2M tokens (1%)
- GSM8K, AI2 ARC

### Total: ~211-226M tokens

---

## Recommended Mix for Final 100M Token Corpus

After collecting conversational data, you'll have flexibility to balance:

**Option 1: Hinglish-focused (for conversational model)**
- Conversational: 50% (50M from ~18-33M available)
- Knowledge: 45% (45M from ~192M available)
- Reasoning: 5% (5M from ~1.2M available, oversampled)

**Option 2: Balanced (knowledge + conversation)**
- Conversational: 30% (30M)
- Knowledge: 65% (65M)
- Reasoning: 5% (5M)

**Option 3: Knowledge-heavy (with Hinglish flavor)**
- Conversational: 20% (20M)
- Knowledge: 75% (75M)
- Reasoning: 5% (5M)

---

## Next Steps

1. ⏳ **Wait for extended Reddit collection to complete** (~2-3 hours)
2. **Run movie subtitles collection**
3. **Verify output files and token counts**
4. **Decide on final corpus mix ratio**
5. **Update and run merge_corpus.py**
6. **Train tokenizer on merged corpus**
7. **Begin pre-training**

---

## Troubleshooting

### Reddit Collection Issues:
- **Rate limiting:** Script already includes delays (0.5s/2s)
- **API errors:** Reddit credentials are embedded in script
- **Low yield:** Some subreddits may have less activity than expected

### Movie Subtitles Issues:
- **Dataset loading fails:** May need manual download from OpenSubtitles.org
- **Language mismatch:** Filter for Hindi/Bollywood during manual download
- **File format:** Convert SRT files to plain text if needed

---

**Status:** Extended Reddit collection running in background. Movie subtitles ready to run after Reddit completes.
