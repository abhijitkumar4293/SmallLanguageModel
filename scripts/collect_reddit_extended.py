"""
Collect extended conversational Reddit data from Indian entertainment, Bollywood,
cricket, and regional subreddits.
Target: 10-20M tokens of conversational Hinglish
"""

import sys
from pathlib import Path
import time
import re
from typing import List, Dict

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))
from reddit_api_client import RedditApiClient


class RedditExtendedCollector:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """Initialize Reddit API client."""
        self.reddit = RedditApiClient(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def is_valid_comment(self, text: str) -> bool:
        """Check if comment is valid for our corpus (more permissive)."""
        # Remove if too short or too long
        word_count = len(text.split())
        if word_count < 3 or word_count > 200:  # More permissive
            return False

        # Remove if too many URLs
        urls = re.findall(r'http\S+|www\.\S+', text)
        if len(urls) > 2:
            return False

        # Don't filter political content (user wants it)

        return True

    def clean_comment(self, text: str) -> str:
        """Clean a Reddit comment."""
        # Remove markdown links [text](url)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)

        # Remove Reddit-specific syntax
        text = re.sub(r'/r/\w+', '', text)
        text = re.sub(r'/u/\w+', '', text)
        text = re.sub(r'\bu/\w+', '', text)

        # Remove markdown formatting
        text = text.replace('**', '')
        text = text.replace('~~', '')
        text = text.replace('`', '')

        # Remove multiple newlines
        text = re.sub(r'\n+', ' ', text)

        # Clean whitespace
        text = ' '.join(text.split())

        return text.strip()

    def extract_conversation_flat(self, comments_data: List[Dict], max_depth: int = 3) -> List[str]:
        """
        Extract comments from hierarchical comment data as flat conversation.
        Each comment appears only once, preserving conversation flow.
        """
        all_comments = []

        def process_comment(comment_data, depth=0):
            """Recursively process comments and their replies."""
            if depth >= max_depth:
                return

            if comment_data['author'] == '[deleted]':
                return

            body = self.clean_comment(comment_data['body'])
            if body and self.is_valid_comment(body):
                all_comments.append(body)

            # Process replies
            if comment_data.get('replies'):
                for reply in comment_data['replies']:
                    process_comment(reply, depth + 1)

        # Process each top-level comment
        for comment in comments_data:
            process_comment(comment, 0)

        return all_comments

    def collect_from_subreddit(
        self,
        subreddit_name: str,
        limit: int = 100,
        time_filter: str = 'month'
    ) -> List[List[str]]:
        """
        Collect conversations from a subreddit.
        Returns list of conversations (each conversation is comments from one post).
        """
        print(f"\nCollecting from r/{subreddit_name}...")

        try:
            # Get top posts
            submissions = self.reddit.get_subreddit_top_posts(
                subreddit_name,
                limit=limit,
                time_filter=time_filter
            )

            all_conversations = []

            for submission in submissions:
                try:
                    # Extract post and comments
                    post_data = self.reddit.extract_post_and_comments(submission.id)

                    if not post_data or 'comments' not in post_data:
                        continue

                    # Extract all comments as flat conversation (no repetition)
                    comments = self.extract_conversation_flat(post_data['comments'])

                    # Only save if we have at least 2 valid comments
                    if len(comments) >= 2:
                        all_conversations.append(comments)

                    time.sleep(0.5)  # Rate limiting

                except Exception as e:
                    print(f"  Error processing post {submission.id}: {e}")
                    continue

            print(f"  → Collected {len(all_conversations)} conversations")
            return all_conversations

        except Exception as e:
            print(f"  Error: {e}")
            return []

    def collect_all(
        self,
        subreddits: List[str],
        posts_per_sub: int = 100,
        time_filter: str = 'month'
    ) -> List[List[str]]:
        """Collect from multiple subreddits."""
        all_conversations = []

        for subreddit_name in subreddits:
            conversations = self.collect_from_subreddit(
                subreddit_name,
                limit=posts_per_sub,
                time_filter=time_filter
            )
            all_conversations.extend(conversations)
            time.sleep(2)  # Rate limiting between subreddits

        return all_conversations

    def save_conversations(self, conversations: List[List[str]], output_file: Path):
        """Save conversations to file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for conversation in conversations:
                # Write each conversation as a block (all comments from one post)
                f.write('\n'.join(conversation))
                f.write('\n\n')

        print(f"\n✓ Saved {len(conversations)} conversations to {output_file}")

        # Estimate tokens
        total_words = sum(len(' '.join(conv).split()) for conv in conversations)
        estimated_tokens = int(total_words * 1.3)
        print(f"✓ Estimated tokens: {estimated_tokens:,}")

        return estimated_tokens


def main():
    """Main collection script for extended Indian subreddits."""
    # Use provided credentials
    client_id = "L-vjF_1bqyJR1eVn25Tb8A"
    client_secret = "gz5LEY0CSQbkpK70fN1-vPrwCRo4FA"
    user_agent = "TCApp/1.0 by Unique_Essay_58"

    print("Initializing Reddit API client...")
    collector = RedditExtendedCollector(client_id, client_secret, user_agent)

    # Extended subreddits for more conversational Hinglish
    # Focus on entertainment, Bollywood, cricket, regional culture
    subreddits = [
        # Bollywood & Movies
        'bollywood',
        'BollyBlindsNGossip',  # Very active, lots of casual discussion
        'indiancinema',

        # Sports (Cricket - huge in India, very conversational)
        'Cricket',
        'indiancricket',

        # Entertainment & Pop Culture
        'IndianDankMemes',  # Very Hinglish
        'IndiaNostalgia',
        'indianews',

        # Regional (more diverse language)
        'Chennai',
        'Hyderabad',
        'Pune',
        'Kolkata',

        # General Indian topics (keep some from original)
        'india',
        'AskIndia',
        'IndianTeenagers',

        # Music
        'indianmusic',
        'bollywoodmusic',
    ]

    print(f"\n{'='*60}")
    print("EXTENDED REDDIT COLLECTION")
    print(f"{'='*60}")
    print(f"\nTarget: 10-20M tokens of conversational Hinglish")
    print(f"Subreddits: {len(subreddits)} entertainment/Bollywood/cricket/regional subs")
    print(f"\nNote: Collecting more posts per subreddit (100) for more data")

    # Collect data
    conversations = collector.collect_all(
        subreddits=subreddits,
        posts_per_sub=100,  # More posts per sub
        time_filter='month'
    )

    # Save
    project_root = Path(__file__).parent.parent
    output_file = project_root / "data" / "raw" / "reddit_extended.txt"
    tokens = collector.save_conversations(conversations, output_file)

    print(f"\n{'='*60}")
    print("COLLECTION COMPLETE")
    print(f"{'='*60}")
    print(f"✓ Conversations collected: {len(conversations)}")
    print(f"✓ Estimated tokens: {tokens:,}")
    print(f"✓ Subreddits covered: {len(subreddits)}")
    print(f"\nNote: Each conversation contains all comments from one post (no repetition)")
    print(f"Focus: Bollywood, cricket, entertainment, regional culture")


if __name__ == "__main__":
    main()
