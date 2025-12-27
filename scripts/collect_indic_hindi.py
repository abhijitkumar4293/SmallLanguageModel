"""
Collect Hindi text from IndicCorpV2 and optionally romanize it.
This provides non-conversational Hinglish (formal/informational).
Target: 20-30M tokens
"""

from pathlib import Path
from tqdm import tqdm
import re


def clean_hindi_text(text: str) -> str:
    """Clean Hindi text."""
    # Remove extra whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'  +', ' ', text)

    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # Final cleanup
    text = ' '.join(text.split())

    return text.strip()


def romanize_hindi(text: str) -> str:
    """
    Romanize Hindi text (Devanagari to Latin script).
    This is a basic implementation using common transliteration rules.
    For production, consider using a library like 'indic-transliteration'.
    """
    # Check if indic-transliteration is available
    try:
        from indic_transliteration import sanscript
        from indic_transliteration.sanscript import transliterate

        # Transliterate from Devanagari to ITRANS (or ISO)
        romanized = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        return romanized

    except ImportError:
        # If library not available, return as-is with a warning
        # (First time only - we'll track this)
        return text


def is_valid_text(text: str, min_words: int = 50) -> bool:
    """Check if text is valid for our corpus."""
    # Must have minimum words
    word_count = len(text.split())
    if word_count < min_words:
        return False

    return True


def main():
    """Download and process Hindi text from IndicCorpV2."""
    print("="*60)
    print("INDIC HINDI COLLECTION")
    print("="*60)
    print("\nTarget: 20-30M tokens")
    print("Source: IndicCorpV2 (Hindi subset)")

    # Check for romanization library
    romanize_enabled = False
    try:
        from indic_transliteration import sanscript
        romanize_enabled = True
        print("✓ Romanization library available")
    except ImportError:
        print("⚠ Warning: 'indic-transliteration' not installed")
        print("  Hindi text will be kept in Devanagari script")
        print("\nTo enable romanization, install:")
        print("  pip install indic-transliteration")

    # Ask user if they want to romanize
    print("\nOptions:")
    print("  1) Keep Devanagari script (original Hindi)")
    print("  2) Romanize to Latin script (for Hinglish-style)")

    # For non-interactive mode, default to Devanagari
    choice = input("\nEnter choice (1 or 2, default=1): ").strip() or "1"
    should_romanize = (choice == "2" and romanize_enabled)

    if should_romanize:
        print("→ Will romanize Hindi to Latin script")
    else:
        print("→ Will keep Devanagari script")

    # Check if datasets library is available
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        print("\nPlease install it:")
        print("  pip install datasets")
        return

    print("\n[1/3] Downloading IndicCorpV2 (Hindi) from Hugging Face...")
    print("(This may take several minutes - dataset is large)")

    try:
        # Load Hindi subset with streaming
        dataset = load_dataset(
            "ai4bharat/IndicCorpV2",
            "hi",  # Hindi
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        print("  → Dataset loaded in streaming mode")

    except Exception as e:
        print(f"✗ Error loading dataset: {e}")
        return

    print("\n[2/3] Processing Hindi text...")
    print("(Collecting until we reach ~30M tokens)")

    processed_texts = []
    total_tokens = 0
    target_tokens = 30_000_000
    texts_processed = 0

    for row in tqdm(dataset, desc="Processing", unit=" docs"):
        texts_processed += 1

        # Get the text (column name might vary)
        text = row.get('text') or row.get('content') or ''

        if not text:
            continue

        # Clean the text
        cleaned = clean_hindi_text(text)

        # Validate
        if not is_valid_text(cleaned, min_words=50):
            continue

        # Romanize if requested
        if should_romanize:
            cleaned = romanize_hindi(cleaned)

        # Add to corpus
        processed_texts.append(cleaned)

        # Estimate tokens
        words = len(cleaned.split())
        tokens = int(words * 1.3)
        total_tokens += tokens

        # Stop if we've reached our target
        if total_tokens >= target_tokens:
            print(f"\n  → Reached target of {target_tokens:,} tokens")
            break

        # Progress update every 5k documents
        if texts_processed % 5000 == 0:
            print(f"  → Processed {texts_processed:,} documents, collected {total_tokens:,} tokens so far...")

    print(f"\n  → Total documents examined: {texts_processed:,}")
    print(f"  → Kept {len(processed_texts):,} valid documents")
    print(f"  → Estimated tokens: {total_tokens:,}")

    # Save
    print("\n[3/3] Saving to file...")
    project_root = Path(__file__).parent.parent

    if should_romanize:
        output_file = project_root / "data" / "raw" / "hindi_romanized.txt"
    else:
        output_file = project_root / "data" / "raw" / "hindi_devanagari.txt"

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for text in processed_texts:
            f.write(text)
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Documents: {len(processed_texts):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")
    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
