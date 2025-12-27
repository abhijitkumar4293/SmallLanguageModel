"""
Collect reasoning datasets from Hugging Face:
1. GSM8K (grade-school math word problems)
2. AI2 ARC (science reasoning questions)

Target: 2-3M tokens
Format for pretraining (not instruction tuning)
"""

from pathlib import Path
from tqdm import tqdm


def format_gsm8k_example(question: str, answer: str) -> str:
    """Format GSM8K example for pretraining."""
    # Use simple Q/A format
    return f"[PROBLEM]\n{question}\n\n[SOLUTION]\n{answer}"


def format_arc_example(question: str, choices: dict, answer_key: str) -> str:
    """Format ARC example for pretraining."""
    # Format choices
    choices_text = "\n".join([f"{k}) {v}" for k, v in choices.items()])

    # Find the correct answer text
    answer_text = choices.get(answer_key, '')

    return f"[QUESTION]\n{question}\n\n[OPTIONS]\n{choices_text}\n\n[ANSWER]\n{answer_key}) {answer_text}"


def main():
    """Download and process reasoning datasets."""
    print("="*60)
    print("REASONING DATASETS COLLECTION")
    print("="*60)
    print("\nTarget: 2-3M tokens")
    print("Sources: GSM8K (math) + AI2 ARC (science)")

    # Check if datasets library is available
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        print("\nPlease install it:")
        print("  pip install datasets")
        return

    all_examples = []
    total_tokens = 0

    # ==================== GSM8K ====================
    print("\n[1/4] Downloading GSM8K (math reasoning)...")

    try:
        gsm8k = load_dataset("openai/gsm8k", "main", split="train")
        print(f"  → Loaded {len(gsm8k):,} math problems")

        print("\n[2/4] Processing GSM8K...")
        for row in tqdm(gsm8k, desc="GSM8K"):
            question = row.get('question', '')
            answer = row.get('answer', '')

            if not question or not answer:
                continue

            formatted = format_gsm8k_example(question, answer)
            all_examples.append(formatted)

            # Estimate tokens
            words = len(formatted.split())
            tokens = int(words * 1.3)
            total_tokens += tokens

        print(f"  → Processed {len(all_examples):,} GSM8K examples")

    except Exception as e:
        print(f"  ⚠ Warning: Could not load GSM8K: {e}")

    # ==================== AI2 ARC ====================
    print("\n[3/4] Downloading AI2 ARC (science reasoning)...")

    arc_start = len(all_examples)

    try:
        # Load both ARC-Easy and ARC-Challenge
        for subset in ["ARC-Easy", "ARC-Challenge"]:
            arc = load_dataset("allenai/ai2_arc", subset, split="train")
            print(f"  → Loaded {len(arc):,} questions from {subset}")

            for row in tqdm(arc, desc=f"ARC ({subset})"):
                question = row.get('question', '')
                choices = row.get('choices', {})
                answer_key = row.get('answerKey', '')

                if not question or not choices or not answer_key:
                    continue

                # Extract choice labels and texts
                choice_dict = {}
                if isinstance(choices, dict):
                    labels = choices.get('label', [])
                    texts = choices.get('text', [])
                    choice_dict = dict(zip(labels, texts))

                formatted = format_arc_example(question, choice_dict, answer_key)
                all_examples.append(formatted)

                # Estimate tokens
                words = len(formatted.split())
                tokens = int(words * 1.3)
                total_tokens += tokens

        arc_count = len(all_examples) - arc_start
        print(f"  → Processed {arc_count:,} ARC examples")

    except Exception as e:
        print(f"  ⚠ Warning: Could not load AI2 ARC: {e}")

    print(f"\n  Total examples: {len(all_examples):,}")
    print(f"  Estimated tokens: {total_tokens:,}")

    # Save
    print("\n[4/4] Saving to file...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "reasoning.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for example in all_examples:
            f.write(example)
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Examples: {len(all_examples):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
