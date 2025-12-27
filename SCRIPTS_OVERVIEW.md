# Scripts Overview

Clean, focused collection of data preparation scripts.

## Data Collection Scripts

### 1. `process_whatsapp.py`
**Purpose:** Process WhatsApp chat exports
**Status:** ✅ Tested and working
**Output:** `data/raw/whatsapp.txt` (894,000 tokens)

```bash
python scripts/process_whatsapp.py
```

**What it does:**
- Removes timestamps, system messages, media placeholders
- Replaces names with `PERSON:`
- Groups into 3-20 turn conversations
- Keeps emojis and Hinglish

---

### 2. `process_hinglish.py`
**Purpose:** Process Hinglish conversation dataset
**Status:** ✅ Tested and working
**Output:** `data/raw/hinglish_public.txt` (873,000 tokens)

```bash
python scripts/process_hinglish.py
```

**What it does:**
- Processes 1,597 conversation files from GitHub repo
- Removes speaker names and metadata
- Keeps pure conversational Hinglish text

**Note:** Requires the GitHub repo to be cloned first (script handles this automatically)

---

### 3. `collect_reddit.py`
**Purpose:** Collect conversations from Indian subreddits
**Status:** Ready to run
**Output:** `data/raw/reddit_conversations.txt` (target: 300k-800k tokens)

```bash
python scripts/collect_reddit.py
```

**What it does:**
- Collects from r/india, r/AskIndia, r/IndianTeenagers, etc.
- Extracts 2-3 turn conversation threads
- Filters political content, code blocks, URLs
- Uses hierarchical comment extraction

**Requirements:** Reddit API credentials (already configured in the script)

---

### 4. `collect_knowledge.py`
**Purpose:** Collect lightweight general knowledge
**Status:** Ready to run
**Output:** `data/raw/explainers.txt` (target: 200k-400k tokens)

```bash
python scripts/collect_knowledge.py
```

**What it does:**
- Collects from r/explainlikeimfive (ELI5-style explanations)
- Samples Simple English Wikipedia
- Filters for 20-300 word explanations
- Avoids technical jargon and encyclopedic content

**Requirements:** Reddit API credentials (already configured)

---

## Data Merging Script

### 5. `merge_corpus.py`
**Purpose:** Merge all data sources with balanced ratios
**Status:** Ready to run
**Output:** `data/processed/pretrain_corpus.txt`

```bash
python scripts/merge_corpus.py
```

**What it does:**
- Merges all 4 data sources
- Applies configurable ratios (default: 50% WhatsApp, 25% Hinglish, 15% Reddit, 10% Knowledge)
- Oversamples or undersamples to reach target distribution
- Shuffles at document level
- Creates manifest with statistics

**Configuration:**
Edit ratios in the script:
```python
DATA_SOURCE_RATIOS = {
    'whatsapp': 0.50,        # 50%
    'hinglish_public': 0.25, # 25%
    'reddit': 0.15,          # 15%
    'knowledge': 0.10,       # 10%
}
TARGET_TOTAL_TOKENS = 3_000_000  # 3M tokens
```

Or use command-line arguments:
```bash
python scripts/merge_corpus.py --whatsapp-ratio 0.6 --target-tokens 4000000
```

---

## Helper Scripts

### 6. `reddit_api_client.py`
**Purpose:** Reddit API wrapper with hierarchical comment extraction
**Type:** Helper class (imported by other scripts)

**Not run directly** - used by `collect_reddit.py` and `collect_knowledge.py`

---

### 7. `prepare_data.py` (Optional)
**Purpose:** Master orchestrator to run all scripts in sequence
**Status:** Optional convenience wrapper

```bash
# Run all steps
python scripts/prepare_data.py --all

# Run specific steps
python scripts/prepare_data.py --whatsapp --hinglish

# Skip optional steps
python scripts/prepare_data.py --no-reddit --no-knowledge
```

**Recommendation:** Run scripts individually for more control

---

## Recommended Workflow

### Current Status:
- ✅ WhatsApp: 894,000 tokens
- ✅ Hinglish: 873,000 tokens
- ⏳ Reddit: Not collected yet
- ⏳ Knowledge: Not collected yet

### Next Steps:

```bash
# 1. Set up conda environment (if not done)
./setup_env.sh create
conda activate llm_project

# 2. Collect Reddit data
python scripts/collect_reddit.py

# 3. Collect knowledge data
python scripts/collect_knowledge.py

# 4. Merge everything
python scripts/merge_corpus.py

# 5. Verify final corpus
cat data/processed/manifest.txt
head -100 data/processed/pretrain_corpus.txt
```

---

## File Outputs

All scripts write to `data/raw/`:
```
data/raw/
├── whatsapp.txt           (894k tokens) ✅
├── hinglish_public.txt    (873k tokens) ✅
├── reddit_conversations.txt  (pending)
└── explainers.txt         (pending)
```

Final merged corpus:
```
data/processed/
├── pretrain_corpus.txt    (target: 3-5M tokens)
└── manifest.txt           (statistics)
```

---

## Script Maintenance

### What NOT to do:
- ❌ Don't edit `reddit_api_client.py` (stable helper)
- ❌ Don't run scripts outside conda environment
- ❌ Don't modify data in `data/raw/` manually

### What TO do:
- ✅ Adjust ratios in `merge_corpus.py` as needed
- ✅ Run scripts multiple times with different settings for more data
- ✅ Check output statistics after each script
- ✅ Review samples from output files

---

## Quick Reference

| Script | Input | Output | Tokens | Status |
|--------|-------|--------|--------|--------|
| `process_whatsapp.py` | `data/wc/*.txt` | `whatsapp.txt` | 894k | ✅ Done |
| `process_hinglish.py` | GitHub repo | `hinglish_public.txt` | 873k | ✅ Done |
| `collect_reddit.py` | Reddit API | `reddit_conversations.txt` | 300-800k | ⏳ Ready |
| `collect_knowledge.py` | Reddit API | `explainers.txt` | 200-400k | ⏳ Ready |
| `merge_corpus.py` | All above | `pretrain_corpus.txt` | 2.3-3M | ⏳ Ready |

**Current Total:** 1.77M tokens (59% of 3M target)
**After Reddit+Knowledge:** 2.3-3M tokens (77-100% of target) ✅

---

**Next:** Run `collect_reddit.py` and `collect_knowledge.py` to complete data collection.
