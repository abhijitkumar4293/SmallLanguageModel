# Data Preparation Summary

## Your Questions Answered

### 1. Token Size vs Model Parameters (60M)

**Current Status:**
- ✓ WhatsApp: **894,000 tokens** (processed from 6,165 conversation chunks)
- ⏳ Hinglish: Not yet collected (~600k-1M estimated)
- ⏳ Reddit: Not yet collected (~300k-800k estimated)
- ⏳ Knowledge: Not yet collected (~200k-400k estimated)

**Projected Total: 2-3.5M tokens**

#### Understanding the Numbers

| Metric | Value | Meaning |
|--------|-------|---------|
| **Model Parameters** | 60M | Size of model (weights) - this is your architecture |
| **Training Tokens** | 2-5M | Amount of text data for training |
| **Tokens per Parameter** | 33-83 | Industry standard: 20-100+ tokens per parameter |

**Your ratio**: With 3M tokens on 60M params = **50 tokens/parameter**

This is on the LOW side but acceptable because:
- ✓ High-quality, focused data (personal conversations)
- ✓ Specific use case (conversational, not general knowledge)
- ✓ Style transfer (learning YOUR way of speaking)
- ⚠ Risk of overfitting (model may memorize data)

**Industry Context:**
- GPT-3 (175B params): ~300B tokens = **1,714 tokens/param**
- LLaMA (7B params): ~1T tokens = **142,857 tokens/param**
- Your model (60M params): ~3M tokens = **50 tokens/param**

**Recommendations:**

| Scenario | Target Tokens | Strategy |
|----------|--------------|----------|
| **Minimum Viable** | 2-3M | WhatsApp + Hinglish only |
| **Recommended** | 3-5M | All 4 sources |
| **Ideal** | 5-10M | Run Reddit/knowledge scripts multiple times |
| **Overkill** | 10M+ | Not needed for 60M model, risk of noise |

---

### 2. Controlling Data Source Balance

I've created **two versions** of the merge script:

#### **Option A: Simple Merge** (`merge_corpus.py`)
- Shuffles everything together
- Natural distribution based on what you collect
- No control over ratios

#### **Option B: Balanced Merge** (`merge_corpus_with_ratios.py`) ⭐ **RECOMMENDED**

Allows you to specify exact percentages:

```python
# Edit this in the script:
DATA_SOURCE_RATIOS = {
    'whatsapp': 0.50,        # 50% - Your personal style
    'hinglish_public': 0.25, # 25% - Public conversations
    'reddit': 0.15,          # 15% - OOD patterns
    'knowledge': 0.10,       # 10% - Conceptual understanding
}

TARGET_TOTAL_TOKENS = 3_000_000  # 3M tokens
```

**How it works:**
- If a source has too little data → **Oversamples** (repeats documents)
- If a source has too much data → **Undersamples** (randomly selects)
- Ensures final corpus matches your target ratios

**Usage:**
```bash
# Use default ratios (50/25/15/10)
python scripts/merge_corpus_with_ratios.py

# Custom ratios via command line
python scripts/merge_corpus_with_ratios.py \
    --whatsapp-ratio 0.6 \
    --hinglish-ratio 0.2 \
    --reddit-ratio 0.1 \
    --knowledge-ratio 0.1 \
    --target-tokens 4000000
```

**Recommended Ratios for 60M Model:**

| Use Case | WhatsApp | Hinglish | Reddit | Knowledge |
|----------|----------|----------|--------|-----------|
| **Max Personalization** | 70% | 20% | 5% | 5% |
| **Balanced** ⭐ | 50% | 25% | 15% | 10% |
| **More General** | 30% | 30% | 25% | 15% |

---

### 3. Preprocessing Steps (Detailed)

See `PREPROCESSING.md` for full details. Summary:

#### **WhatsApp** (`process_whatsapp.py`)

**Removed:**
- ✗ Timestamps: `[11/9/18, 9:24:30 AM]`
- ✗ System messages: "Messages are end-to-end encrypted"
- ✗ Media: "image omitted", "video omitted"
- ✗ URLs: http://..., www...
- ✗ Names: Replaced with `PERSON:`

**Kept:**
- ✓ Message text
- ✓ Emojis 😂
- ✓ Hinglish
- ✓ Conversational flow

**Structure:**
- Grouped into 3-20 turn conversations
- Prevents memorizing entire chat histories

#### **Reddit** (`collect_reddit.py`)

**Filtering:**
- ✓ Length: 5-150 tokens only
- ✓ Conversational: 2-3 turn threads
- ✗ Political: Heavy filtering
- ✗ Code blocks: Removed
- ✗ URLs: Removed

**Cleaned:**
- ✗ Reddit syntax: `/r/subreddit`, `u/username`
- ✗ Markdown: `**bold**`, `[links](url)`
- ✗ Deleted/removed comments

#### **Hinglish Dataset** (`process_hinglish_dataset.py`)

**Removed:**
- ✗ Topic labels
- ✗ Metadata headers
- ✗ Speaker labels on separate lines

**Kept:**
- ✓ Pure conversational text
- ✓ Hinglish code-switching

#### **Knowledge** (`collect_knowledge.py`)

**Quality Filtering:**
- ✓ Length: 20-300 words (not encyclopedic)
- ✓ Explanation style: Must contain "because", "when", "so", etc.
- ✗ Technical jargon: Filtered out
- ✗ Listicles: Avoided

**Source:**
- Reddit r/explainlikeimfive (best quality)
- Simple Wikipedia (carefully filtered)

#### **Universal Rules (All Sources)**

1. **Whitespace normalization**: Collapse multiple spaces
2. **URL removal**: All http://, www. removed
3. **Keep emojis**: Part of natural conversation
4. **Keep Hinglish**: No transliteration
5. **No lowercasing**: Preserve capitalization
6. **Document-level shuffle**: Mix all sources

---

### 4. Is Preprocessing Important?

**YES. CRITICAL.**

For a 60M parameter model with limited data (3-5M tokens):
- Every token matters
- Model has limited capacity
- Will memorize patterns quickly

**Bad preprocessing consequences:**

| Issue | Impact on Model |
|-------|----------------|
| Keep timestamps | Generates `[11/9/18, 9:24:30 AM]` in outputs |
| Keep URLs | Hallucinates fake URLs, wastes capacity |
| Keep usernames | Leaks names, privacy issues |
| Keep system messages | Outputs "image omitted" in conversation |
| Inconsistent formatting | Confuses model, slower convergence |
| Political content | Biased outputs |

**Good preprocessing benefits:**

| Benefit | Impact |
|---------|--------|
| Clean text | Faster convergence (fewer epochs needed) |
| No artifacts | Natural outputs |
| Consistent format | Model focuses on language, not formatting |
| Balanced sources | Your style dominates, but with breadth |
| Privacy-safe | No leaked names/numbers |

**Example of preprocessing impact:**

**Without preprocessing:**
```
[11/9/18, 9:24:30 AM] Abhijit: are you coming?
‎[11/9/18, 9:29:18 AM] Friend: ‎image omitted
[11/9/18, 9:31:16 AM] Abhijit: ok cool
```
→ Model learns to generate timestamps and "image omitted"

**With preprocessing:**
```
are you coming?
PERSON: yeah leaving now
ok cool
```
→ Model learns conversational patterns

---

## Current Project Status

### ✅ Completed

1. ✓ Project structure setup
2. ✓ WhatsApp processing (894k tokens extracted)
3. ✓ All data collection scripts created
4. ✓ Balanced merge script with ratio control
5. ✓ Documentation (README, QUICKSTART, PREPROCESSING)
6. ✓ RedditApiClient integration

### ⏳ Next Steps

1. **Collect Hinglish dataset**
   ```bash
   python scripts/process_hinglish_dataset.py
   ```

2. **Collect Reddit data** (requires API credentials)
   ```bash
   # Set credentials first:
   export REDDIT_CLIENT_ID='...'
   export REDDIT_CLIENT_SECRET='...'
   export REDDIT_USER_AGENT='personal_llm/1.0'

   python scripts/collect_reddit.py
   ```

3. **Collect knowledge** (optional, requires Reddit API)
   ```bash
   python scripts/collect_knowledge.py
   ```

4. **Merge with balanced ratios**
   ```bash
   python scripts/merge_corpus_with_ratios.py
   ```

5. **Review final corpus**
   ```bash
   cat data/processed/manifest.txt
   head -100 data/processed/pretrain_corpus.txt
   ```

---

## Final Recommendations

### For Your 60M Parameter Model:

1. **Minimum Target**: 3M tokens
   - WhatsApp: 1.5M (50%)
   - Hinglish: 900k (30%)
   - Reddit: 450k (15%)
   - Knowledge: 150k (5%)

2. **Use Balanced Merge**: `merge_corpus_with_ratios.py`
   - Ensures WhatsApp dominates (your style)
   - Prevents any source from being overrepresented

3. **Validate Preprocessing**:
   ```bash
   # Check for artifacts in final corpus
   grep -E '\[.*,.*\]' data/processed/pretrain_corpus.txt  # Should be empty (no timestamps)
   grep -E 'http|www\.' data/processed/pretrain_corpus.txt  # Should be empty (no URLs)
   head -100 data/processed/pretrain_corpus.txt  # Manual review
   ```

4. **Quality > Quantity**:
   - 3M high-quality tokens > 10M noisy tokens
   - Your preprocessing is solid, trust it

5. **Next Phase**: After corpus is ready
   - Train tokenizer (BPE with ~8k-16k vocab for Hinglish)
   - Design 60M model architecture
   - Start pre-training on Mac (can move to GPU later)

---

## Quick Command Reference

```bash
# 1. Process WhatsApp (already done - 894k tokens)
python scripts/process_whatsapp.py

# 2. Get Hinglish dataset
python scripts/process_hinglish_dataset.py

# 3. Get Reddit data (needs credentials)
python scripts/collect_reddit.py

# 4. Get knowledge (optional)
python scripts/collect_knowledge.py

# 5. Merge with balanced ratios (recommended)
python scripts/merge_corpus_with_ratios.py

# OR: Simple merge (no ratio control)
python scripts/merge_corpus.py

# 6. Validate
cat data/processed/manifest.txt
```

---

**You're in good shape!** The preprocessing is thorough, the ratio control gives you flexibility, and 894k tokens from WhatsApp is a solid foundation. Collect the remaining sources and you'll be ready for tokenizer training.
