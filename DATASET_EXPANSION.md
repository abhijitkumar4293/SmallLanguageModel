# Dataset Expansion Plan

**Goal:** Expand from 3M tokens to ~100M+ tokens for better 50-60M parameter model training.

## Current Status
- WhatsApp: 894,000 tokens ✅
- Hinglish public: 873,000 tokens ✅
- Reddit: 1,044,000 tokens ✅
- Wikipedia (intros): 254,000 tokens ✅
- **Total: 3,066,000 tokens**

## New Data Sources (Ready to Collect)

### 1. Simple English Wikipedia
**Script:** `scripts/collect_simple_wiki.py`
**Target:** 10-15M tokens
**Why:** Easier vocabulary, perfect for small models to learn factual phrasing

```bash
conda activate llm_project
python scripts/collect_simple_wiki.py
```

**Output:** `data/raw/simple_wiki.txt`

---

### 2. WikiText-103
**Script:** `scripts/collect_wikitext.py`
**Target:** ~100M tokens
**Why:** Curated, high-quality English Wikipedia prose

```bash
python scripts/collect_wikitext.py
```

**Output:** `data/raw/wikitext_103.txt`

---

### 3. Full Wikipedia Articles
**Script:** `scripts/collect_full_wikipedia.py`
**Target:** 30-40M tokens
**Why:** Comprehensive knowledge coverage (beyond just intros)

```bash
python scripts/collect_full_wikipedia.py
```

**Output:** `data/raw/wikipedia_full.txt`

**Note:** Uses streaming to avoid memory issues. Collects until reaching 40M tokens.

---

### 4. Reasoning Datasets
**Script:** `scripts/collect_reasoning.py`
**Target:** 2-3M tokens
**Sources:**
- GSM8K (grade-school math word problems)
- AI2 ARC (science reasoning questions)

```bash
python scripts/collect_reasoning.py
```

**Output:** `data/raw/reasoning.txt`

**Format:** Structured Q&A format suitable for pretraining:
```
[PROBLEM]
...
[SOLUTION]
...
```

---

### 5. Hindi Text (IndicCorpV2)
**Script:** `scripts/collect_indic_hindi.py`
**Target:** 20-30M tokens
**Why:** Non-conversational Hinglish (formal/informational) via romanization

```bash
python scripts/collect_indic_hindi.py
```

**Options:**
1. Keep Devanagari script (original Hindi)
2. Romanize to Latin script (for Hinglish-style)

**Output:**
- `data/raw/hindi_devanagari.txt` (if keeping Devanagari)
- `data/raw/hindi_romanized.txt` (if romanizing)

**Note:** Romanization requires `indic-transliteration` library:
```bash
pip install indic-transliteration
```

---

## Setup Instructions

### 1. Update Dependencies
```bash
conda activate llm_project
pip install -r requirements.txt
```

This installs:
- `datasets` (Hugging Face datasets library)
- Optionally: `indic-transliteration` (for Hindi romanization)

### 2. Run Collection Scripts

**Recommended order:**

```bash
# 1. Simple Wikipedia (quick, ~15 minutes)
python scripts/collect_simple_wiki.py

# 2. Reasoning datasets (quick, ~5 minutes)
python scripts/collect_reasoning.py

# 3. Full Wikipedia (longer, ~1-2 hours)
python scripts/collect_full_wikipedia.py

# 4. WikiText-103 (medium, ~30 minutes)
python scripts/collect_wikitext.py

# 5. Hindi text (optional, ~1-2 hours)
python scripts/collect_indic_hindi.py
```

### 3. Verify Collection

```bash
# Check output files
ls -lh data/raw/

# Count total tokens (rough estimate)
wc -w data/raw/*.txt
```

---

## Expected Results

After running all scripts:

| Source | Tokens (est.) | Status |
|--------|---------------|--------|
| WhatsApp | 894k | ✅ Collected |
| Hinglish public | 873k | ✅ Collected |
| Reddit | 1,044k | ✅ Collected |
| Wikipedia intros | 254k | ✅ Collected |
| Simple Wikipedia | 10-15M | ⏳ Ready |
| WikiText-103 | 100M | ⏳ Ready |
| Full Wikipedia | 30-40M | ⏳ Ready |
| Reasoning | 2-3M | ⏳ Ready |
| Hindi (optional) | 20-30M | ⏳ Ready |
| **TOTAL** | **~165-190M** | |

---

## Next Steps After Collection

### 1. Decide Final Mix Ratios

Current recommendation for 100M token corpus:
- **Conversational (Hinglish/English)**: 35% (35M)
  - WhatsApp, Hinglish public, Reddit
- **Knowledge/Expository English**: 40% (40M)
  - Full Wikipedia, Simple Wikipedia, WikiText-103
- **Non-conversational Hinglish**: 20% (20M)
  - Romanized Hindi from IndicCorpV2
- **Structured reasoning**: 2% (2M)
  - GSM8K, AI2 ARC
- **Glue/misc**: 3% (3M)

### 2. Merge Corpus

Update `scripts/merge_corpus.py` to include new sources and run:

```bash
python scripts/merge_corpus.py --target-tokens 100000000
```

### 3. Train Tokenizer

After merging, train a custom tokenizer on the final corpus:

```bash
python tokenizer/train_tokenizer.py
```

---

## Notes

- **Streaming vs Full Download:** Large datasets (Wikipedia, IndicCorpV2) use streaming to avoid memory issues
- **First Run is Slower:** Hugging Face datasets cache after first download
- **Disk Space:** Expect ~20-30GB for raw data files
- **Processing Time:** Total collection time ~3-5 hours depending on internet speed

---

## Troubleshooting

### Error: "datasets library not found"
```bash
pip install datasets
```

### Error: "No module named 'indic_transliteration'"
Only needed for Hindi romanization:
```bash
pip install indic-transliteration
```

### Dataset download is slow
- First download caches to `~/.cache/huggingface/datasets`
- Subsequent runs are much faster
- Check internet connection

### Out of memory
- Scripts use streaming for large datasets
- If still issues, reduce target tokens in script
- Process datasets one at a time

---

**Ready to expand your dataset! Start with the smaller ones (Simple Wikipedia, Reasoning) to test the pipeline.**
