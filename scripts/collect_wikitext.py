"""
Collect WikiText-103 dataset from Hugging Face.
Clean, high-quality English Wikipedia prose.
Target: ~100M tokens
"""

from pathlib import Path
from tqdm import tqdm
import re


def clean_text(text: str) -> str:
    """Clean WikiText-103 text."""
    # WikiText is already quite clean, but let's do basic cleanup

    # Remove multiple blank lines
    text = re.sub(r'\n\n+', '\n\n', text)

    # Remove leading/trailing whitespace per line
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)

    # Remove excessive spaces
    text = re.sub(r'  +', ' ', text)

    return text.strip()


def is_valid_article(text: str) -> bool:
    """Check if article is valid for our corpus."""
    # Must have at least 50 words (WikiText has good articles)
    word_count = len(text.split())
    if word_count < 50:
        return False

    return True


def main():
    """Download and process WikiText-103."""
    print("="*60)
    print("WIKITEXT-103 COLLECTION")
    print("="*60)
    print("\nTarget: ~100M tokens")
    print("This is a curated, high-quality Wikipedia corpus")

    # Check if datasets library is available
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        print("\nPlease install it:")
        print("  pip install datasets")
        return

    print("\n[1/3] Downloading WikiText-103 from Hugging Face...")
    print("(This may take a few minutes on first run)")

    try:
        # Load the dataset (train split has the most data)
        dataset = load_dataset(
            "Salesforce/wikitext",
            "wikitext-103-raw-v1",
            split="train"
        )
        print(f"  → Loaded {len(dataset):,} documents")

    except Exception as e:
        print(f"✗ Error loading dataset: {e}")
        return

    print("\n[2/3] Processing documents...")

    processed_docs = []
    total_tokens = 0

    for row in tqdm(dataset, desc="Processing"):
        # Get the text
        text = row.get('text', '')

        if not text or text.strip() == '':
            continue

        # Clean the text
        cleaned = clean_text(text)

        # Validate
        if not is_valid_article(cleaned):
            continue

        # Add to corpus
        processed_docs.append(cleaned)

        # Estimate tokens
        words = len(cleaned.split())
        tokens = int(words * 1.3)
        total_tokens += tokens

    print(f"  → Kept {len(processed_docs):,} valid documents")
    print(f"  → Estimated tokens: {total_tokens:,}")

    # Save
    print("\n[3/3] Saving to file...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "wikitext_103.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for doc in processed_docs:
            f.write(doc)
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Documents: {len(processed_docs):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
