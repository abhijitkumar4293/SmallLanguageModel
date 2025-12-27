"""
Merge all data sources into final pre-training corpus WITH CONFIGURABLE RATIOS.

This version allows you to specify exact proportions for each data source.

Usage:
    # Use default ratios
    python scripts/merge_corpus_with_ratios.py

    # Custom ratios via config
    Edit the DATA_SOURCE_RATIOS in this file, then run
"""

import random
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import argparse


# ============================================================================
# CONFIGURATION: Adjust these ratios to control data source balance
# ============================================================================

DATA_SOURCE_RATIOS = {
    # Target percentage of final corpus (must sum to 1.0)
    'whatsapp': 0.50,           # 50% - Your personal style (ANCHOR)
    'hinglish_public': 0.25,    # 25% - Public Hinglish breadth
    'reddit': 0.15,             # 15% - OOD conversational patterns
    'knowledge': 0.10,          # 10% - Conceptual understanding
}

# Target total tokens in final corpus
TARGET_TOTAL_TOKENS = 3_000_000  # 3M tokens

# ============================================================================


class BalancedCorpusMerger:
    def __init__(self, project_root: Path, ratios: Dict[str, float], target_tokens: int):
        self.project_root = project_root
        self.raw_dir = project_root / "data" / "raw"
        self.processed_dir = project_root / "data" / "processed"
        self.ratios = ratios
        self.target_tokens = target_tokens

        # Validate ratios
        ratio_sum = sum(ratios.values())
        if not (0.99 <= ratio_sum <= 1.01):
            raise ValueError(f"Ratios must sum to 1.0, got {ratio_sum}")

        # Data sources
        self.sources = {
            'whatsapp': {
                'file': 'whatsapp.txt',
                'description': 'Personal conversational style'
            },
            'hinglish_public': {
                'file': 'hinglish_public.txt',
                'description': 'Public Hinglish conversations'
            },
            'reddit': {
                'file': 'reddit_conversations.txt',
                'description': 'Reddit conversational breadth'
            },
            'knowledge': {
                'file': 'explainers.txt',
                'description': 'Lightweight knowledge'
            }
        }

    def load_documents(self, file_path: Path) -> List[str]:
        """Load documents from a file (separated by blank lines)."""
        if not file_path.exists():
            print(f"  ⚠ Warning: {file_path.name} not found")
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by double newlines (document separator)
        documents = [doc.strip() for doc in content.split('\n\n') if doc.strip()]
        return documents

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate: ~1.3 tokens per word for English/Hinglish."""
        words = text.split()
        return int(len(words) * 1.3)

    def sample_to_target(
        self,
        documents: List[str],
        target_tokens: int,
        source_name: str
    ) -> List[str]:
        """
        Sample documents to reach target token count.

        - If we have fewer tokens than target: use all + oversample (repeat)
        - If we have more tokens than target: undersample
        """
        current_tokens = sum(self.estimate_tokens(doc) for doc in documents)

        if current_tokens == 0:
            print(f"  ⚠ {source_name}: No data available")
            return []

        print(f"  {source_name}:")
        print(f"    Available: {current_tokens:,} tokens ({len(documents)} docs)")
        print(f"    Target: {target_tokens:,} tokens")

        if current_tokens < target_tokens:
            # Need to oversample (repeat documents)
            ratio = target_tokens / current_tokens
            num_repeats = int(ratio)
            remainder = ratio - num_repeats

            sampled = documents * num_repeats

            # Add remainder
            if remainder > 0:
                extra_docs = random.sample(documents, int(len(documents) * remainder))
                sampled.extend(extra_docs)

            print(f"    ⚠ Oversampled {ratio:.2f}x to reach target")

        else:
            # Undersample
            # Calculate how many documents we need
            avg_tokens_per_doc = current_tokens / len(documents)
            num_docs_needed = int(target_tokens / avg_tokens_per_doc)

            sampled = random.sample(documents, min(num_docs_needed, len(documents)))

            sampled_tokens = sum(self.estimate_tokens(doc) for doc in sampled)
            print(f"    Sampled: {sampled_tokens:,} tokens ({len(sampled)} docs)")

        return sampled

    def merge_with_ratios(self, all_documents: Dict[str, List[str]], output_file: Path):
        """Merge documents according to specified ratios."""
        print("\n" + "="*60)
        print("BALANCING DATA SOURCES")
        print("="*60)

        print("\nTarget distribution:")
        for source, ratio in self.ratios.items():
            target_tokens = int(self.target_tokens * ratio)
            print(f"  {source:20} {ratio*100:5.1f}% → {target_tokens:,} tokens")

        print(f"\nTotal target: {self.target_tokens:,} tokens")

        # Sample each source to target
        print("\n" + "="*60)
        print("SAMPLING SOURCES")
        print("="*60)

        balanced_documents = {}
        for source_key in self.ratios.keys():
            if source_key in all_documents:
                target_tokens = int(self.target_tokens * self.ratios[source_key])
                sampled = self.sample_to_target(
                    all_documents[source_key],
                    target_tokens,
                    source_key
                )
                balanced_documents[source_key] = sampled

        # Merge and shuffle
        print("\n" + "="*60)
        print("MERGING AND SHUFFLING")
        print("="*60)

        merged = []
        for source, docs in balanced_documents.items():
            for doc in docs:
                merged.append((source, doc))

        # Shuffle
        random.seed(42)  # Reproducible
        random.shuffle(merged)

        # Write to output
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for source, doc in merged:
                f.write(doc)
                f.write('\n\n')

        print(f"✓ Merged corpus saved to: {output_file}")

        return merged

    def analyze_final_corpus(self, merged: List[Tuple[str, str]]):
        """Analyze the final balanced corpus."""
        print("\n" + "="*60)
        print("FINAL CORPUS ANALYSIS")
        print("="*60)

        # Source distribution
        source_counts = Counter(source for source, _ in merged)
        total_docs = len(merged)

        print("\nDocument Distribution:")
        for source, count in source_counts.most_common():
            pct = (count / total_docs) * 100
            target_pct = self.ratios.get(source, 0) * 100
            print(f"  {source:20} {count:6} docs ({pct:5.1f}% | target: {target_pct:.1f}%)")

        # Token distribution
        print("\nToken Distribution:")
        source_tokens = {}
        for source in source_counts.keys():
            docs = [doc for s, doc in merged if s == source]
            tokens = sum(self.estimate_tokens(doc) for doc in docs)
            source_tokens[source] = tokens

        total_tokens = sum(source_tokens.values())

        for source, tokens in sorted(source_tokens.items(), key=lambda x: x[1], reverse=True):
            pct = (tokens / total_tokens) * 100
            target_pct = self.ratios.get(source, 0) * 100
            print(f"  {source:20} {tokens:8,} tokens ({pct:5.1f}% | target: {target_pct:.1f}%)")

        print(f"\n  {'TOTAL':20} {total_tokens:8,} tokens")
        print(f"  {'TARGET':20} {self.target_tokens:8,} tokens")

        # Check if close to target
        deviation = abs(total_tokens - self.target_tokens) / self.target_tokens
        if deviation < 0.05:
            print(f"  ✓ Within 5% of target")
        else:
            print(f"  ⚠ Deviation: {deviation*100:.1f}%")

        print("\n" + "="*60)

    def create_manifest(self, merged: List[Tuple[str, str]], output_file: Path):
        """Create manifest with ratios."""
        manifest_file = output_file.parent / "manifest.txt"

        source_counts = Counter(source for source, _ in merged)
        source_tokens = {}
        for source in source_counts.keys():
            docs = [doc for s, doc in merged if s == source]
            tokens = sum(self.estimate_tokens(doc) for doc in docs)
            source_tokens[source] = tokens

        total_tokens = sum(source_tokens.values())

        with open(manifest_file, 'w', encoding='utf-8') as f:
            f.write("Pre-training Corpus Manifest (Balanced)\n")
            f.write("="*60 + "\n\n")

            f.write("Target Ratios:\n")
            for source, ratio in self.ratios.items():
                f.write(f"  {source}: {ratio*100:.1f}%\n")
            f.write(f"\nTarget Total Tokens: {self.target_tokens:,}\n\n")

            f.write("Actual Distribution:\n")
            for source in sorted(source_tokens.keys()):
                tokens = source_tokens[source]
                docs = source_counts[source]
                pct = (tokens / total_tokens) * 100
                f.write(f"\n{source}:\n")
                f.write(f"  Documents: {docs:,}\n")
                f.write(f"  Tokens: {tokens:,} ({pct:.1f}%)\n")

            f.write(f"\nTotal tokens: {total_tokens:,}\n")

        print(f"✓ Manifest saved to: {manifest_file}")

    def run(self):
        """Main pipeline."""
        print("="*60)
        print("BALANCED CORPUS MERGER")
        print("="*60)

        print("\nConfiguration:")
        print(f"  Target total tokens: {self.target_tokens:,}")
        print("\nRatios:")
        for source, ratio in self.ratios.items():
            print(f"  {source}: {ratio*100:.0f}%")

        # Load all sources
        print("\n" + "="*60)
        print("LOADING DATA SOURCES")
        print("="*60)

        all_documents = {}
        for source_key, source_info in self.sources.items():
            file_path = self.raw_dir / source_info['file']
            documents = self.load_documents(file_path)
            if documents:
                all_documents[source_key] = documents
                tokens = sum(self.estimate_tokens(doc) for doc in documents)
                print(f"  ✓ {source_key}: {len(documents)} docs, {tokens:,} tokens")

        # Merge with ratios
        output_file = self.processed_dir / "pretrain_corpus.txt"
        merged = self.merge_with_ratios(all_documents, output_file)

        # Analyze
        self.analyze_final_corpus(merged)

        # Manifest
        self.create_manifest(merged, output_file)

        print("\n✓ Balanced corpus preparation complete!")
        print(f"\nNext steps:")
        print(f"1. Review: {output_file}")
        print(f"2. Train tokenizer: python tokenizer/train_tokenizer.py")
        print(f"3. Start pre-training: python train/pretrain.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge corpus with configurable ratios")
    parser.add_argument('--target-tokens', type=int, default=TARGET_TOTAL_TOKENS,
                        help=f'Target total tokens (default: {TARGET_TOTAL_TOKENS:,})')
    parser.add_argument('--whatsapp-ratio', type=float, help='WhatsApp ratio (0-1)')
    parser.add_argument('--hinglish-ratio', type=float, help='Hinglish ratio (0-1)')
    parser.add_argument('--reddit-ratio', type=float, help='Reddit ratio (0-1)')
    parser.add_argument('--knowledge-ratio', type=float, help='Knowledge ratio (0-1)')

    args = parser.parse_args()

    # Use custom ratios if provided
    ratios = DATA_SOURCE_RATIOS.copy()
    if args.whatsapp_ratio:
        ratios['whatsapp'] = args.whatsapp_ratio
    if args.hinglish_ratio:
        ratios['hinglish_public'] = args.hinglish_ratio
    if args.reddit_ratio:
        ratios['reddit'] = args.reddit_ratio
    if args.knowledge_ratio:
        ratios['knowledge'] = args.knowledge_ratio

    # Run
    project_root = Path(__file__).parent.parent
    merger = BalancedCorpusMerger(project_root, ratios, args.target_tokens)
    merger.run()
