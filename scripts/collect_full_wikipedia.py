"""
Collect full Wikipedia articles from Hugging Face.
This expands beyond just intro paragraphs to full article content.
Target: 30-40M tokens
"""

from pathlib import Path
from tqdm import tqdm
import re


def clean_text(text: str) -> str:
    """Clean Wikipedia text."""
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

    # Remove "See also", "References", "External links" sections
    text = re.split(r'\n(?:See also|References|External links|Further reading)', text, flags=re.IGNORECASE)[0]

    # Final cleanup
    text = text.replace('  ', ' ')

    return text.strip()


def is_valid_article(text: str) -> bool:
    """Check if article is valid for our corpus."""
    # Must have at least 100 words for full articles
    word_count = len(text.split())
    if word_count < 100:
        return False

    # Must not be a disambiguation page
    if 'may refer to:' in text.lower()[:500]:
        return False

    return True


def main():
    """Download and process full Wikipedia articles."""
    print("="*60)
    print("FULL WIKIPEDIA COLLECTION")
    print("="*60)
    print("\nTarget: 30-40M tokens")
    print("This downloads full articles from Hugging Face")

    # Check if datasets library is available
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        print("\nPlease install it:")
        print("  pip install datasets")
        return

    print("\n[1/3] Downloading Wikipedia (English) from Hugging Face...")
    print("(This may take several minutes on first run - dataset is large)")

    try:
        # Load the English Wikipedia dataset
        # Using streaming to avoid loading all at once
        dataset = load_dataset(
            "wikimedia/wikipedia",
            "20231101.en",  # English Wikipedia dump from Nov 2023
            split="train",
            streaming=True  # Stream to avoid memory issues
        )
        print("  → Dataset loaded in streaming mode")

    except Exception as e:
        print(f"✗ Error loading dataset: {e}")
        print("\nTrying alternative configuration...")
        try:
            dataset = load_dataset(
                "wikipedia",
                "20220301.en",
                split="train",
                streaming=True
            )
            print("  → Alternative dataset loaded")
        except Exception as e2:
            print(f"✗ Error: {e2}")
            return

    print("\n[2/3] Processing articles...")
    print("(Collecting until we reach ~40M tokens)")

    processed_articles = []
    total_tokens = 0
    target_tokens = 40_000_000
    articles_processed = 0

    # Use take() to limit the stream
    for row in tqdm(dataset, desc="Processing", unit=" articles"):
        articles_processed += 1

        # Get the text
        text = row.get('text', '')

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

        # Stop if we've reached our target
        if total_tokens >= target_tokens:
            print(f"\n  → Reached target of {target_tokens:,} tokens")
            break

        # Progress update every 10k articles
        if articles_processed % 10000 == 0:
            print(f"  → Processed {articles_processed:,} articles, collected {total_tokens:,} tokens so far...")

    print(f"\n  → Total articles examined: {articles_processed:,}")
    print(f"  → Kept {len(processed_articles):,} valid articles")
    print(f"  → Estimated tokens: {total_tokens:,}")

    # Save
    print("\n[3/3] Saving to file...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "wikipedia_full.txt"
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
