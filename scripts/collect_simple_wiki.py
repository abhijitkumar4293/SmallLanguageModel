"""
Collect Simple English Wikipedia dataset from Hugging Face.
Simple Wikipedia uses easier vocabulary and grammar, perfect for small models.
Target: 10-15M tokens
"""

from pathlib import Path
from tqdm import tqdm
import re


def clean_text(text: str) -> str:
    """Clean Simple Wikipedia text."""
    # Remove citations like [1], [2]
    text = re.sub(r'\[\d+\]', '', text)

    # Remove common mathematical notation artifacts
    text = re.sub(r'{\s*displaystyle[^}]*}', '', text)
    text = re.sub(r'\\[a-zA-Z]+\s*\{[^}]*\}', '', text)  # LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remaining LaTeX

    # Clean up parentheses with only whitespace
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\[\s*\]', '', text)

    # Remove extra whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'  +', ' ', text)

    # Remove "See also" and similar sections
    text = re.split(r'\n== ', text)[0]

    # Final cleanup
    text = text.replace('  ', ' ')

    return text.strip()


def is_valid_article(text: str) -> bool:
    """Check if article is valid for our corpus."""
    # Must have at least 20 words
    word_count = len(text.split())
    if word_count < 20:
        return False

    # Must not be a stub
    if 'stub' in text.lower()[:200]:
        return False

    return True


def main():
    """Download and process Simple English Wikipedia."""
    print("="*60)
    print("SIMPLE ENGLISH WIKIPEDIA COLLECTION")
    print("="*60)
    print("\nTarget: 10-15M tokens")
    print("This will download ~770k articles from Hugging Face")

    # Check if datasets library is available
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        print("\nPlease install it:")
        print("  pip install datasets")
        return

    print("\n[1/3] Downloading Simple Wikipedia from Hugging Face...")
    print("(This may take a few minutes on first run)")

    try:
        # Load the dataset
        dataset = load_dataset(
            "rahular/simple-wikipedia",
            split="train",
            trust_remote_code=True
        )
        print(f"  → Loaded {len(dataset):,} articles")

    except Exception as e:
        print(f"✗ Error loading dataset: {e}")
        return

    print("\n[2/3] Processing articles...")

    processed_articles = []
    total_tokens = 0

    for row in tqdm(dataset, desc="Processing"):
        # Get the text (column name might be 'text' or 'content')
        text = row.get('text') or row.get('content') or row.get('article') or ''

        if not text:
            continue

        # Clean the text
        cleaned = clean_text(text)

        # Validate
        if not is_valid_article(cleaned):
            continue

        # Add to corpus
        processed_articles.append(cleaned)

        # Estimate tokens
        words = len(cleaned.split())
        tokens = int(words * 1.3)
        total_tokens += tokens

    print(f"  → Kept {len(processed_articles):,} valid articles")
    print(f"  → Estimated tokens: {total_tokens:,}")

    # Save
    print("\n[3/3] Saving to file...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "simple_wiki.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for article in processed_articles:
            f.write(article)
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Articles: {len(processed_articles):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
