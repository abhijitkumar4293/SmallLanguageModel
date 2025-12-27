# Quick Start Guide

This guide will help you prepare data for pre-training your 50M parameter language model.

## Overview

You're building a personal conversational LLM trained on:
- ✓ Your WhatsApp chats (already in `data/wc/`)
- Hinglish conversational dataset
- Reddit conversations (r/india, r/delhi, etc.)
- Lightweight general knowledge

**Target**: 3-5M tokens total

---

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Reddit API Setup (Optional but Recommended)

Reddit data collection requires API credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: Personal LLM Data Collector
   - **App type**: Select "script"
   - **Redirect URI**: http://localhost:8080
4. Click "Create app"
5. Note your **Client ID** (under the app name) and **Client Secret**

Set environment variables:

```bash
export REDDIT_CLIENT_ID='your_client_id_here'
export REDDIT_CLIENT_SECRET='your_client_secret_here'
export REDDIT_USER_AGENT='personal_llm_collector/1.0'
```

Or add to your `~/.bashrc` or `~/.zshrc` to persist.

---

## Data Preparation

### Option A: Run Full Pipeline (Recommended)

```bash
python scripts/prepare_data.py --all
```

This will:
1. Process your WhatsApp chats
2. Download Hinglish dataset
3. Collect Reddit data (requires credentials)
4. Collect general knowledge (requires credentials)
5. Merge everything into final corpus

The script will ask before steps that need API credentials.

### Option B: Run Individual Steps

If you want more control or don't have Reddit credentials yet:

```bash
# 1. Process WhatsApp chats (no credentials needed)
python scripts/process_whatsapp.py

# 2. Download Hinglish dataset (no credentials needed)
python scripts/process_hinglish_dataset.py

# 3. Collect Reddit data (needs credentials)
python scripts/collect_reddit.py

# 4. Collect general knowledge (needs credentials)
python scripts/collect_knowledge.py

# 5. Merge all sources
python scripts/merge_corpus.py
```

### Option C: Skip Reddit/Knowledge Collection

If you don't want to set up Reddit API credentials:

```bash
python scripts/prepare_data.py --no-reddit --no-knowledge
```

This will use only WhatsApp + Hinglish data (~2-3.5M tokens).

---

## Verify Your Data

After running the pipeline:

### Check the final corpus:

```bash
# View statistics
cat data/processed/manifest.txt

# Sample the corpus
head -50 data/processed/pretrain_corpus.txt
```

### Expected output:

```
Pre-training Corpus Manifest
============================================================

Source: whatsapp
  Documents: ~1,500-3,000
  Estimated tokens: 1,500,000-2,500,000

Source: hinglish_public
  Documents: ~500-1,000
  Estimated tokens: 600,000-1,000,000

Source: reddit
  Documents: ~300-800
  Estimated tokens: 300,000-800,000

Source: knowledge
  Documents: ~200-300
  Estimated tokens: 200,000-400,000

Total estimated tokens: 3,000,000-5,000,000
```

---

## Troubleshooting

### "WhatsApp file not found"

Make sure your WhatsApp chats are in `data/wc/*.txt`

### "Reddit API credentials not set"

Either:
- Set up Reddit API credentials (see step 2 above)
- OR skip Reddit collection: `--no-reddit`

### "Hinglish dataset download failed"

Manual download:
```bash
cd data/temp
git clone https://github.com/skmanish/hinglish-conv-dataset.git
cd ../..
python scripts/process_hinglish_dataset.py
```

### "Not enough tokens"

If your total is below 3M tokens:
- Run Reddit collection with higher limits
- Run scripts multiple times with different `time_filter` settings
- Add more WhatsApp conversations

---

## Next Steps

Once you have your corpus (`data/processed/pretrain_corpus.txt`):

### 1. Train Tokenizer

```bash
python tokenizer/train_tokenizer.py
```

This creates a custom BPE tokenizer optimized for your Hinglish data.

### 2. Start Pre-training

```bash
python train/pretrain.py
```

Start on Mac, resume on GPU later if needed.

### 3. Monitor Progress

Track:
- Loss curves
- Sample generations
- Perplexity on held-out set

---

## Data Distribution Guidelines

Your corpus should roughly follow:

| Source | Target Tokens | Purpose |
|--------|--------------|---------|
| WhatsApp | 1.5-2.5M | Personal style anchor |
| Hinglish | 600k-1M | Conversational breadth |
| Reddit | 300k-800k | OOD robustness |
| Knowledge | 200k-400k | Conceptual understanding |

The WhatsApp data dominates → model learns your style first.

---

## Important Notes

### What This Data WILL Do:
- ✓ Teach conversational patterns
- ✓ Handle Hinglish code-switching
- ✓ Explain simple concepts
- ✓ Adapt to your personal style

### What This Data WON'T Do:
- ✗ Memorize facts
- ✗ Replace Wikipedia
- ✗ Know current events
- ✗ Handle highly technical queries

That's by design. You want a conversational model, not an encyclopedia.

---

## Questions?

Check:
- `README.md` - Project overview and structure
- Individual script files - Each has detailed docstrings
- `data/processed/manifest.txt` - Your data statistics

---

**Ready to start training!** 🚀
