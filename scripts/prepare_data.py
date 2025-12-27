"""
Master script to prepare all pre-training data.

Runs all data collection scripts in sequence:
1. Process WhatsApp chats
2. Download and process Hinglish dataset
3. Collect Reddit conversations (requires API credentials)
4. Collect general knowledge (requires API credentials)
5. Merge everything into final corpus

Usage:
    # Full pipeline
    python scripts/prepare_data.py --all

    # Individual steps
    python scripts/prepare_data.py --whatsapp
    python scripts/prepare_data.py --hinglish
    python scripts/prepare_data.py --reddit
    python scripts/prepare_data.py --knowledge
    python scripts/prepare_data.py --merge

    # Skip steps that need API credentials
    python scripts/prepare_data.py --no-reddit --no-knowledge
"""

import argparse
import sys
from pathlib import Path
import subprocess


class DataPipeline:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts"

    def run_script(self, script_name: str, description: str) -> bool:
        """Run a Python script and return success status."""
        print("\n" + "="*60)
        print(f"{description}")
        print("="*60)

        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            print(f"✗ Script not found: {script_path}")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                check=True
            )
            print(f"✓ {description} completed")
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ {description} failed with error code {e.returncode}")
            return False

        except Exception as e:
            print(f"✗ Error running {script_name}: {e}")
            return False

    def run_pipeline(self, args):
        """Run the full data preparation pipeline."""
        print("="*60)
        print("DATA PREPARATION PIPELINE")
        print("="*60)
        print("\nThis will prepare all data sources for pre-training.")
        print("Target: 3-5M tokens total\n")

        steps_run = []
        steps_failed = []

        # Step 1: WhatsApp
        if args.all or args.whatsapp:
            success = self.run_script(
                "process_whatsapp.py",
                "Step 1/4: Processing WhatsApp chats"
            )
            if success:
                steps_run.append("WhatsApp")
            else:
                steps_failed.append("WhatsApp")

        # Step 2: Hinglish dataset
        if args.all or args.hinglish:
            success = self.run_script(
                "process_hinglish.py",
                "Step 2/4: Processing Hinglish dataset"
            )
            if success:
                steps_run.append("Hinglish")
            else:
                steps_failed.append("Hinglish")

        # Step 3: Reddit (optional, needs credentials)
        if (args.all or args.reddit) and not args.no_reddit:
            print("\n" + "="*60)
            print("Step 3/4: Collecting Reddit conversations")
            print("="*60)
            print("\nThis requires Reddit API credentials.")
            print("If you haven't set them up yet, you can skip this step.")

            if args.interactive:
                response = input("\nContinue with Reddit collection? [y/N]: ")
                if response.lower() != 'y':
                    print("Skipping Reddit collection")
                else:
                    success = self.run_script(
                        "collect_reddit.py",
                        "Collecting Reddit conversations"
                    )
                    if success:
                        steps_run.append("Reddit")
                    else:
                        steps_failed.append("Reddit")
            else:
                success = self.run_script(
                    "collect_reddit.py",
                    "Collecting Reddit conversations"
                )
                if success:
                    steps_run.append("Reddit")
                else:
                    steps_failed.append("Reddit")

        # Step 4: General knowledge (optional, needs credentials)
        if (args.all or args.knowledge) and not args.no_knowledge:
            print("\n" + "="*60)
            print("Step 4/4: Collecting general knowledge")
            print("="*60)
            print("\nThis requires Reddit API credentials (for ELI5).")

            if args.interactive:
                response = input("\nContinue with knowledge collection? [y/N]: ")
                if response.lower() != 'y':
                    print("Skipping knowledge collection")
                else:
                    success = self.run_script(
                        "collect_knowledge.py",
                        "Collecting general knowledge"
                    )
                    if success:
                        steps_run.append("Knowledge")
                    else:
                        steps_failed.append("Knowledge")
            else:
                success = self.run_script(
                    "collect_knowledge.py",
                    "Collecting general knowledge"
                )
                if success:
                    steps_run.append("Knowledge")
                else:
                    steps_failed.append("Knowledge")

        # Step 5: Merge everything
        if args.all or args.merge:
            success = self.run_script(
                "merge_corpus.py",
                "Final Step: Merging all data sources"
            )
            if success:
                steps_run.append("Merge")
            else:
                steps_failed.append("Merge")

        # Summary
        print("\n" + "="*60)
        print("PIPELINE SUMMARY")
        print("="*60)

        if steps_run:
            print(f"\n✓ Completed steps: {', '.join(steps_run)}")

        if steps_failed:
            print(f"\n✗ Failed steps: {', '.join(steps_failed)}")

        print("\n" + "="*60)

        if "Merge" in steps_run:
            print("\n✓ Data preparation complete!")
            print("\nNext steps:")
            print("1. Review the corpus: data/processed/pretrain_corpus.txt")
            print("2. Train tokenizer: python tokenizer/train_tokenizer.py")
            print("3. Start pre-training: python train/pretrain.py")
        else:
            print("\nTo complete data preparation, run:")
            print("  python scripts/merge_corpus.py")


def main():
    parser = argparse.ArgumentParser(description="Prepare pre-training data")

    # Pipeline options
    parser.add_argument('--all', action='store_true',
                        help='Run all steps')
    parser.add_argument('--whatsapp', action='store_true',
                        help='Process WhatsApp chats only')
    parser.add_argument('--hinglish', action='store_true',
                        help='Download Hinglish dataset only')
    parser.add_argument('--reddit', action='store_true',
                        help='Collect Reddit data only')
    parser.add_argument('--knowledge', action='store_true',
                        help='Collect knowledge data only')
    parser.add_argument('--merge', action='store_true',
                        help='Merge all data sources only')

    # Skip options
    parser.add_argument('--no-reddit', action='store_true',
                        help='Skip Reddit collection (no API credentials needed)')
    parser.add_argument('--no-knowledge', action='store_true',
                        help='Skip knowledge collection (no API credentials needed)')

    # Interactive mode
    parser.add_argument('--interactive', action='store_true',
                        help='Ask before each step that requires API credentials')

    args = parser.parse_args()

    # Default to --all if no specific steps chosen
    if not any([args.all, args.whatsapp, args.hinglish, args.reddit, args.knowledge, args.merge]):
        args.all = True
        args.interactive = True  # Default to interactive for --all

    # Run pipeline
    project_root = Path(__file__).parent.parent
    pipeline = DataPipeline(project_root)
    pipeline.run_pipeline(args)


if __name__ == "__main__":
    main()
