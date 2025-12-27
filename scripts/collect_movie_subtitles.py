"""
Collect movie subtitles from Bollywood/Hindi films.
Subtitles provide natural conversational dialogue.
Target: 5-10M tokens of conversational dialogue
"""

from pathlib import Path
from tqdm import tqdm
import re


def clean_subtitle_line(text: str) -> str:
    """Clean a subtitle line."""
    # Remove timing codes and HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\d{2}:\d{2}:\d{2}[,\.]\d{3}', '', text)
    text = re.sub(r'-->', '', text)
    text = re.sub(r'^\d+$', '', text)  # Remove sequence numbers

    # Remove stage directions in brackets/parentheses
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)

    # Remove music/sound indicators
    text = re.sub(r'♪.*?♪', '', text)
    text = re.sub(r'#.*?#', '', text)

    # Clean up whitespace
    text = ' '.join(text.split())

    return text.strip()


def is_valid_dialogue(text: str) -> bool:
    """Check if dialogue line is valid."""
    # Must have at least 2 words
    word_count = len(text.split())
    if word_count < 2:
        return False

    # Must not be too long (single line)
    if word_count > 50:
        return False

    # Skip if it's just a number or timestamp remnant
    if text.isdigit():
        return False

    return True


def format_as_conversation(dialogues: list, window_size: int = 10) -> list:
    """
    Format subtitle lines into conversation chunks.
    Groups consecutive dialogues into conversation windows.
    """
    conversations = []

    for i in range(0, len(dialogues), window_size // 2):  # 50% overlap
        window = dialogues[i:i + window_size]
        if len(window) >= 3:  # At least 3 lines for a conversation
            conversations.append(window)

    return conversations


def main():
    """Download and process movie subtitles."""
    print("="*60)
    print("MOVIE SUBTITLES COLLECTION")
    print("="*60)
    print("\nTarget: 5-10M tokens from Bollywood/Hindi film dialogues")

    # Check if datasets library is available
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        print("\nPlease install it:")
        print("  pip install datasets")
        return

    print("\n[1/4] Downloading OpenSubtitles dataset from Hugging Face...")
    print("(This may take several minutes - dataset is large)")
    print("Filtering for Hindi and English subtitles...")

    try:
        # Load Hindi subtitles
        # Note: We'll try both Hindi and English-Hindi pairs
        dataset = load_dataset(
            "Helsinki-NLP/open_subtitles",
            "en-hi",  # English-Hindi pairs (common in Bollywood)
            split="train",
            streaming=True,
            trust_remote_code=True
        )
        print("  → Dataset loaded in streaming mode")

    except Exception as e:
        print(f"✗ Error loading dataset: {e}")
        print("\nTrying alternative approach...")

        # Alternative: Try to load a simpler subtitle dataset
        # or provide instructions for manual download
        print("\nOpenSubtitles dataset may require manual setup.")
        print("Alternative approach: Download Hindi movie subtitles manually")
        print("\nRecommended sources:")
        print("  1. OpenSubtitles.org - Filter for Hindi/Bollywood")
        print("  2. Subscene.com - Hindi section")
        print("\nFor now, collecting from available datasets...")
        return

    print("\n[2/4] Processing subtitle dialogues...")
    print("(Collecting until we reach ~10M tokens)")

    all_dialogues = []
    all_conversations = []
    total_tokens = 0
    target_tokens = 10_000_000
    processed_count = 0

    for item in tqdm(dataset, desc="Processing", unit=" subtitle files"):
        processed_count += 1

        # Get translation pairs (English and Hindi)
        translation = item.get('translation', {})

        # Prefer Hindi side, fallback to English
        text = translation.get('hi') or translation.get('en') or ''

        if not text:
            continue

        # Split into lines
        lines = text.split('\n')

        # Clean and filter each line
        for line in lines:
            cleaned = clean_subtitle_line(line)
            if cleaned and is_valid_dialogue(cleaned):
                all_dialogues.append(cleaned)

        # Every 1000 files, create conversation windows
        if processed_count % 1000 == 0 and all_dialogues:
            conversations = format_as_conversation(all_dialogues[-5000:])
            all_conversations.extend(conversations)

            # Estimate tokens
            words = sum(len(' '.join(conv).split()) for conv in conversations)
            tokens = int(words * 1.3)
            total_tokens += tokens

            if total_tokens >= target_tokens:
                print(f"\n  → Reached target of {target_tokens:,} tokens")
                break

            if processed_count % 5000 == 0:
                print(f"  → Processed {processed_count:,} files, collected {total_tokens:,} tokens so far...")

    # Process remaining dialogues
    if all_dialogues and total_tokens < target_tokens:
        conversations = format_as_conversation(all_dialogues)
        all_conversations.extend(conversations)
        words = sum(len(' '.join(conv).split()) for conv in conversations)
        total_tokens += int(words * 1.3)

    print(f"\n  → Total subtitle files processed: {processed_count:,}")
    print(f"  → Total conversations created: {len(all_conversations):,}")
    print(f"  → Estimated tokens: {total_tokens:,}")

    # Save
    print("\n[3/4] Saving to file...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "movie_subtitles.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for conversation in all_conversations:
            # Write each conversation (dialogue window)
            f.write('\n'.join(conversation))
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Conversations: {len(all_conversations):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")

    print("\n[4/4] Collection complete!")
    print("\n" + "="*60)
    print("MOVIE SUBTITLES COLLECTION COMPLETE")
    print("="*60)
    print(f"\nNote: Dialogues are grouped into conversation windows")
    print(f"Each window contains ~10 consecutive lines of dialogue")


if __name__ == "__main__":
    main()
