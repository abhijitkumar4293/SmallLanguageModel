"""
Process Hinglish conversations from local clone.
Processes all .txt files from conversations/ directory.
"""

from pathlib import Path
import re


def process_conversation_file(file_path: Path) -> str:
    """
    Process a single conversation file.
    Format: [Name]: [Message]
    We remove names and keep just the conversational flow.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Remove speaker name prefix (Name: message -> message)
        # Keep "PERSON:" prefix for non-you messages for consistency with WhatsApp
        match = re.match(r'^([^:]+):\s*(.+)$', line)
        if match:
            name, message = match.groups()
            # Alternate between you and PERSON
            # For simplicity, we'll just keep the message without prefixes
            # since this is public conversation data
            cleaned_lines.append(message.strip())
        else:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def process_all_conversations(repo_path: Path, output_file: Path):
    """Process all conversation files from the repository."""
    conversations_dir = repo_path / "conversations"

    if not conversations_dir.exists():
        print(f"Error: {conversations_dir} not found")
        return

    # Get all .txt files
    conversation_files = sorted(conversations_dir.glob("*.txt"))
    print(f"Found {len(conversation_files)} conversation files")

    all_conversations = []
    for file_path in conversation_files:
        try:
            conversation = process_conversation_file(file_path)
            if conversation:
                all_conversations.append(conversation)
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

    # Save all conversations
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for conv in all_conversations:
            f.write(conv)
            f.write('\n\n')

    print(f"\n✓ Processed {len(all_conversations)} conversations")
    print(f"✓ Saved to: {output_file}")

    # Estimate tokens
    total_words = sum(len(conv.split()) for conv in all_conversations)
    estimated_tokens = int(total_words * 1.3)
    print(f"✓ Estimated tokens: {estimated_tokens:,}")

    return estimated_tokens


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    repo_path = project_root / "data" / "temp" / "hinglish-dataset"
    output_file = project_root / "data" / "raw" / "hinglish_public.txt"

    process_all_conversations(repo_path, output_file)
