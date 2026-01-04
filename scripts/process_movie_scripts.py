"""
Process Bollywood movie scripts to extract conversational dialogues.
Extracts character dialogues while removing scene descriptions.
Target: ~491k tokens of natural Hinglish dialogue
"""

from pathlib import Path
import re
from tqdm import tqdm


def extract_dialogues(script_text: str) -> list:
    """Extract dialogue lines from movie script."""
    dialogues = []
    lines = script_text.split('\n')

    current_dialogue = []
    in_dialogue = False

    for line in lines:
        line = line.strip()

        # Skip empty lines, technical directions, scene headers
        if not line:
            if current_dialogue:
                dialogues.append(' '.join(current_dialogue))
                current_dialogue = []
            in_dialogue = False
            continue

        # Skip scene headers and technical directions
        if (line.startswith('INT.') or line.startswith('EXT.') or
            line.startswith('CUT TO:') or line.startswith('FADE') or
            line.startswith('CONTINUED:') or line.endswith('(CONTINUED)') or
            line.startswith('(') and line.endswith(')') or
            re.match(r'^\d+\.$', line)):  # Skip numbers
            if current_dialogue:
                dialogues.append(' '.join(current_dialogue))
                current_dialogue = []
            in_dialogue = False
            continue

        # Check if line is a character name (usually all caps or specific pattern)
        if (line.isupper() and len(line) < 50 and
            not line.startswith('NARRATOR') and
            not line.endswith('VIDEO')):
            # Start of new dialogue
            if current_dialogue:
                dialogues.append(' '.join(current_dialogue))
                current_dialogue = []
            in_dialogue = True
            continue

        # Check for character name with (O.S.) or other annotations
        if re.match(r'^[A-Z\s]+\(.*?\)$', line):
            if current_dialogue:
                dialogues.append(' '.join(current_dialogue))
                current_dialogue = []
            in_dialogue = True
            continue

        # If we're in dialogue mode, collect the line
        if in_dialogue or current_dialogue:
            # Skip pure action lines (usually lowercase start or descriptive)
            if not (line[0].islower() if line else False):
                current_dialogue.append(line)

    # Add last dialogue if any
    if current_dialogue:
        dialogues.append(' '.join(current_dialogue))

    return dialogues


def clean_dialogue(text: str) -> str:
    """Clean dialogue text."""
    # Remove (O.S.), (V.O.), (CONT'D) etc
    text = re.sub(r'\(O\.S\.\)', '', text)
    text = re.sub(r'\(V\.O\.\)', '', text)
    text = re.sub(r'\(CONT\'D\)', '', text)
    text = re.sub(r'\(.*?\)', '', text)

    # Clean whitespace
    text = ' '.join(text.split())

    return text.strip()


def is_valid_dialogue(text: str) -> bool:
    """Check if dialogue is valid."""
    # Must have at least 3 words
    word_count = len(text.split())
    if word_count < 3:
        return False

    # Must not be too long
    if word_count > 150:
        return False

    # Must not be mostly English technical terms
    tech_words = ['camera', 'frame', 'zoom', 'visual', 'background']
    if sum(1 for w in tech_words if w in text.lower()) > 2:
        return False

    return True


def group_into_conversations(dialogues: list, window_size: int = 8) -> list:
    """Group dialogues into conversation chunks."""
    conversations = []

    for i in range(0, len(dialogues), window_size // 2):  # 50% overlap
        window = dialogues[i:i + window_size]
        if len(window) >= 3:  # At least 3 turns
            conversations.append(window)

    return conversations


def main():
    """Process all movie scripts."""
    print("="*60)
    print("BOLLYWOOD MOVIE SCRIPTS PROCESSING")
    print("="*60)

    scripts_dir = Path("/Users/abhijitkumar/Downloads/movie")

    if not scripts_dir.exists():
        print(f"\n✗ Error: Scripts directory not found: {scripts_dir}")
        return

    script_files = list(scripts_dir.glob("*.txt"))

    if not script_files:
        print(f"\n✗ Error: No .txt files found in {scripts_dir}")
        return

    print(f"\nFound {len(script_files)} movie scripts")
    print("Processing to extract dialogues...")

    all_dialogues = []
    all_conversations = []
    total_tokens = 0

    for script_file in tqdm(script_files, desc="Processing scripts"):
        try:
            # Read script
            with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                script_text = f.read()

            # Extract dialogues
            dialogues = extract_dialogues(script_text)

            # Clean and filter
            cleaned = []
            for dialogue in dialogues:
                cleaned_dialogue = clean_dialogue(dialogue)
                if cleaned_dialogue and is_valid_dialogue(cleaned_dialogue):
                    cleaned.append(cleaned_dialogue)
                    all_dialogues.append(cleaned_dialogue)

            # Group into conversations for this script
            conversations = group_into_conversations(cleaned)
            all_conversations.extend(conversations)

            # Estimate tokens for this script
            words = sum(len(d.split()) for d in cleaned)
            tokens = int(words * 1.3)
            total_tokens += tokens

        except Exception as e:
            print(f"\n  ⚠ Error processing {script_file.name}: {e}")
            continue

    print(f"\n  → Total dialogues extracted: {len(all_dialogues):,}")
    print(f"  → Conversations created: {len(all_conversations):,}")
    print(f"  → Estimated tokens: {total_tokens:,}")

    # Save dialogues
    print("\nSaving processed dialogues...")
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "movie_dialogues.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        for conversation in all_conversations:
            # Write each conversation as a dialogue block
            f.write('\n'.join(conversation))
            f.write('\n\n')

    print(f"✓ Saved to {output_file}")
    print(f"✓ Dialogues: {len(all_dialogues):,}")
    print(f"✓ Conversations: {len(all_conversations):,}")
    print(f"✓ Estimated tokens: {total_tokens:,}")

    # Also save as flat dialogue list
    flat_output = project_root / "data" / "raw" / "movie_dialogues_flat.txt"
    with open(flat_output, 'w', encoding='utf-8') as f:
        for dialogue in all_dialogues:
            f.write(dialogue)
            f.write('\n')

    print(f"✓ Also saved flat version to {flat_output}")

    print("\n" + "="*60)
    print("MOVIE SCRIPTS PROCESSING COMPLETE")
    print("="*60)
    print("\nFiles from:")
    for i, script_file in enumerate(script_files[:5], 1):
        print(f"  {i}. {script_file.name}")
    if len(script_files) > 5:
        print(f"  ... and {len(script_files) - 5} more")


if __name__ == "__main__":
    main()
