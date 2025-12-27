"""
Process WhatsApp chat exports into pre-training format.

Removes:
- Timestamps
- System messages
- Media placeholders
- Names (replaced with PERSON)

Groups into short conversational chunks (5-20 turns).
Keeps emojis and Hinglish text.
"""

import re
import os
from pathlib import Path
from typing import List, Tuple


def parse_whatsapp_line(line: str) -> Tuple[str, str, str]:
    """
    Parse a WhatsApp line into (timestamp, sender, message).
    Returns (None, None, None) if line doesn't match format.
    """
    # Pattern: [date, time] Sender: message
    pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s(?:AM|PM))\]\s([^:]+):\s(.+)'
    match = re.match(pattern, line)

    if match:
        timestamp, sender, message = match.groups()
        return timestamp, sender.strip(), message.strip()

    return None, None, None


def is_system_message(message: str) -> bool:
    """Check if message is a system message to be removed."""
    system_patterns = [
        r'Messages and calls are end-to-end encrypted',
        r'image omitted',
        r'video omitted',
        r'audio omitted',
        r'sticker omitted',
        r'document omitted',
        r'GIF omitted',
        r'Contact card omitted',
        r'You deleted this message',
        r'This message was deleted',
        r'changed the subject',
        r'changed this group',
        r'added you',
        r'left',
        r'joined using this group',
        r'created group',
    ]

    for pattern in system_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False


def clean_message(message: str) -> str:
    """Clean individual message (keep emojis, Hinglish)."""
    # Remove URLs
    message = re.sub(r'http\S+', '', message)
    message = re.sub(r'www\.\S+', '', message)

    # Clean extra whitespace
    message = ' '.join(message.split())

    return message.strip()


def process_chat_file(file_path: Path, your_name: str = "Abhijit") -> List[str]:
    """
    Process a single WhatsApp chat file.
    Returns list of messages (alternating speakers when possible).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    messages = []
    current_sender = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        timestamp, sender, message = parse_whatsapp_line(line)

        # Skip unparseable lines (continuations of previous messages)
        if sender is None:
            continue

        # Skip system messages
        if is_system_message(message):
            continue

        # Clean message
        message = clean_message(message)
        if not message:
            continue

        # Replace sender names
        if sender == your_name:
            prefix = ""  # Your messages have no prefix
        else:
            prefix = "PERSON: "

        messages.append(f"{prefix}{message}")

    return messages


def chunk_conversations(messages: List[str], min_turns: int = 3, max_turns: int = 20) -> List[str]:
    """
    Group messages into conversational chunks.
    Each chunk is min_turns to max_turns messages.
    """
    chunks = []

    i = 0
    while i < len(messages):
        # Take a chunk of messages
        chunk_size = min(max_turns, len(messages) - i)

        # Ensure minimum size
        if chunk_size < min_turns and i > 0:
            break

        chunk = messages[i:i + chunk_size]
        chunks.append('\n'.join(chunk))

        i += chunk_size

    return chunks


def process_all_chats(
    input_dir: Path,
    output_file: Path,
    your_name: str = "Abhijit",
    min_turns: int = 3,
    max_turns: int = 20
):
    """
    Process all WhatsApp chat files in input_dir.
    Write chunked conversations to output_file.
    """
    all_chunks = []

    chat_files = list(input_dir.glob("*.txt"))
    print(f"Found {len(chat_files)} chat files")

    for chat_file in chat_files:
        print(f"Processing {chat_file.name}...")
        messages = process_chat_file(chat_file, your_name=your_name)
        chunks = chunk_conversations(messages, min_turns=min_turns, max_turns=max_turns)
        all_chunks.extend(chunks)
        print(f"  → {len(messages)} messages → {len(chunks)} chunks")

    # Write to output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(chunk + '\n\n')

    print(f"\nTotal: {len(all_chunks)} conversation chunks")
    print(f"Written to: {output_file}")

    # Calculate token count (rough estimate: ~1.3 tokens per word for English)
    total_words = sum(len(chunk.split()) for chunk in all_chunks)
    estimated_tokens = int(total_words * 1.3)
    print(f"Estimated tokens: {estimated_tokens:,}")

    return all_chunks


if __name__ == "__main__":
    # Paths
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "data" / "wc"
    output_file = project_root / "data" / "raw" / "whatsapp.txt"

    # Process
    process_all_chats(
        input_dir=input_dir,
        output_file=output_file,
        your_name="Abhijit",  # Change this to your name in WhatsApp
        min_turns=3,
        max_turns=20
    )
