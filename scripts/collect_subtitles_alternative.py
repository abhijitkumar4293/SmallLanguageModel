"""
Alternative approach to collect conversational dialogue data.
Uses publicly available conversational datasets instead of subtitles.
Target: 5-10M tokens of natural dialogue
"""

from pathlib import Path
from tqdm import tqdm
import re


def clean_dialogue(text: str) -> str:
    """Clean dialogue text."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()


def is_valid_dialogue(text: str) -> bool:
    """Check if dialogue is valid."""
    word_count = len(text.split())
    if word_count < 2 or word_count > 100:
        return False
    return True


def main():
    """Collect conversational dialogue from alternative sources."""
    print("="*60)
    print("CONVERSATIONAL DIALOGUE COLLECTION (Alternative)")
    print("="*60)
    print("\nTarget: 5-10M tokens of natural conversation")
    print("\nTrying multiple dialogue datasets...")

    try:
        from datasets import load_dataset
    except ImportError:
        print("\n✗ Error: 'datasets' library not installed")
        return

    all_conversations = []
    total_tokens = 0
    target_tokens = 10_000_000

    # Try dataset 1: Daily Dialog
    print("\n[1/3] Trying DailyDialog dataset...")
    try:
        dataset = load_dataset("daily_dialog", split="train")
        print(f"  → Loaded {len(dataset):,} dialogues")

        for item in tqdm(dataset, desc="Processing DailyDialog"):
            dialog = item.get('dialog', [])
            if len(dialog) >= 2:
                cleaned = [clean_dialogue(turn) for turn in dialog if is_valid_dialogue(clean_dialogue(turn))]
                if len(cleaned) >= 2:
                    all_conversations.append(cleaned)
                    words = sum(len(turn.split()) for turn in cleaned)
                    total_tokens += int(words * 1.3)

        print(f"  → Collected {len(all_conversations):,} conversations")
        print(f"  → Total tokens so far: {total_tokens:,}")

    except Exception as e:
        print(f"  ⚠ Could not load DailyDialog: {e}")

    # Try dataset 2: PersonaChat
    if total_tokens < target_tokens:
        print("\n[2/3] Trying PersonaChat dataset...")
        try:
            dataset = load_dataset("bavard/personachat_truecased", split="train")
            print(f"  → Loaded {len(dataset):,} conversations")

            for item in tqdm(dataset, desc="Processing PersonaChat"):
                utterances = item.get('utterances', [])
                if not utterances:
                    # Try 'history' field
                    utterances = item.get('history', [])

                if len(utterances) >= 2:
                    cleaned = [clean_dialogue(turn) for turn in utterances if isinstance(turn, str) and is_valid_dialogue(clean_dialogue(turn))]
                    if len(cleaned) >= 2:
                        all_conversations.append(cleaned)
                        words = sum(len(turn.split()) for turn in cleaned)
                        total_tokens += int(words * 1.3)

                if total_tokens >= target_tokens:
                    break

            print(f"  → Collected {len(all_conversations):,} conversations total")
            print(f"  → Total tokens so far: {total_tokens:,}")

        except Exception as e:
            print(f"  ⚠ Could not load PersonaChat: {e}")

    # Try dataset 3: EmpatheticDialogues
    if total_tokens < target_tokens:
        print("\n[3/3] Trying EmpatheticDialogues dataset...")
        try:
            dataset = load_dataset("empathetic_dialogues", split="train")
            print(f"  → Loaded {len(dataset):,} dialogues")

            current_conv = []
            for item in tqdm(dataset, desc="Processing EmpatheticDialogues"):
                utterance = item.get('utterance', '')
                conv_id = item.get('conv_id', '')

                if utterance:
                    cleaned = clean_dialogue(utterance)
                    if is_valid_dialogue(cleaned):
                        current_conv.append(cleaned)

                # New conversation starts
                if len(current_conv) >= 5:  # Save every 5 turns
                    all_conversations.append(current_conv[:])
                    words = sum(len(turn.split()) for turn in current_conv)
                    total_tokens += int(words * 1.3)
                    current_conv = []

                if total_tokens >= target_tokens:
                    break

            print(f"  → Collected {len(all_conversations):,} conversations total")
            print(f"  → Total tokens: {total_tokens:,}")

        except Exception as e:
            print(f"  ⚠ Could not load EmpatheticDialogues: {e}")

    if not all_conversations:
        print("\n✗ No conversations collected. All datasets failed.")
        print("\nPlease check internet connection or try manual download.")
        return

    # Save
    print("\n[4/4] Saving conversations...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "dialogue_conversations.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for conversation in all_conversations:
            f.write('\n'.join(conversation))
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Conversations: {len(all_conversations):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")

    print("\n" + "="*60)
    print("COLLECTION COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
