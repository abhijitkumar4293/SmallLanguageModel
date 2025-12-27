# Personal Language Model (60M Parameters)

A small language model trained on personal conversational data with Hinglish support.

## Quick Start

```bash
# 1. Set up conda environment
./setup_env.sh create
conda activate llm_project

# 2. Verify setup
python test_env.py

# 3. Collect data
python scripts/collect_reddit_enhanced.py
python scripts/collect_knowledge.py

# 4. Merge corpus
python scripts/merge_corpus_with_ratios.py

# 5. Train tokenizer (coming soon)
# python tokenizer/train_tokenizer.py
```

For detailed setup instructions, see [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)

## Project Structure

```
personal_llm/
│
├── data/
│   ├── wc/                          # WhatsApp chats (raw)
│   ├── raw/                         # Processed raw data sources
│   │   ├── whatsapp.txt
│   │   ├── hinglish_public.txt
│   │   ├── reddit_conversations.txt
│   │   └── explainers.txt
│   │
│   ├── processed/                   # Final merged corpus
│   │   └── pretrain_corpus.txt
│   │
│   ├── sft/                         # Supervised fine-tuning data
│   │   └── persona_slot_examples.jsonl
│   │
│   └── rlhf/                        # RLHF data
│       └── preference_pairs.jsonl
│
├── scripts/                         # Data processing scripts
│   ├── process_whatsapp.py
│   ├── collect_reddit.py
│   ├── collect_knowledge.py
│   └── merge_corpus.py
│
├── tokenizer/
│   ├── train_tokenizer.py
│   └── tokenizer.model
│
├── model/
│   ├── config.py
│   ├── transformer.py
│   └── lm_head.py
│
├── train/
│   ├── pretrain.py
│   ├── sft.py
│   └── dpo.py
│
├── eval/
│   ├── probes.txt
│   └── generate_samples.py
│
└── checkpoints/
    └── pretrain/
```

## Data Sources

1. **WhatsApp Chats** (1.5-2.5M tokens): Personal conversational style
2. **Hinglish Dataset** (600k-1M tokens): Public conversational breadth
3. **Reddit Conversations** (300k-800k tokens): OOD robustness
4. **Knowledge Explainers** (200k-400k tokens): Conceptual understanding

**Total Target**: 3-5M tokens

## Pipeline

1. **Data Preparation**: Process raw sources → `data/raw/`
2. **Corpus Merging**: Merge all sources → `data/processed/pretrain_corpus.txt`
3. **Tokenizer Training**: Train BPE tokenizer on corpus
4. **Pre-training**: Train 50M parameter model
5. **SFT**: Fine-tune for persona/behavior
6. **RLHF/DPO**: Align preferences

## Next Steps

1. Process all data sources
2. Train tokenizer
3. Start pre-training on Mac (move to GPU later)
