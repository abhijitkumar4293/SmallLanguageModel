#!/usr/bin/env python
"""
Test script to verify conda environment is set up correctly.
Run this after creating the environment to ensure all dependencies work.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...")

    tests = {
        'numpy': 'Data processing',
        'pandas': 'Data processing',
        'requests': 'HTTP requests',
        'praw': 'Reddit API',
        'tqdm': 'Progress bars',
    }

    failed = []

    for package, description in tests.items():
        try:
            __import__(package)
            print(f"  ✓ {package:15} ({description})")
        except ImportError as e:
            print(f"  ✗ {package:15} FAILED: {e}")
            failed.append(package)

    return len(failed) == 0


def test_python_version():
    """Test Python version."""
    print("\nChecking Python version...")

    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 10:
        print(f"  ✓ Python version OK")
        return True
    else:
        print(f"  ✗ Python 3.10+ required")
        return False


def test_project_structure():
    """Test project structure."""
    print("\nChecking project structure...")

    required_dirs = ['data', 'scripts', 'tokenizer', 'model', 'train', 'eval']
    project_root = Path(__file__).parent

    all_exist = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_exist = False

    return all_exist


def test_data_files():
    """Test if data files exist."""
    print("\nChecking collected data...")

    project_root = Path(__file__).parent
    data_files = {
        'whatsapp.txt': 'WhatsApp conversations',
        'hinglish_public.txt': 'Hinglish dataset',
        'reddit_conversations.txt': 'Reddit conversations (optional)',
        'explainers.txt': 'Knowledge data (optional)',
    }

    for filename, description in data_files.items():
        file_path = project_root / 'data' / 'raw' / filename
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f"  ✓ {filename:25} ({size_kb:.1f} KB) - {description}")
        else:
            if 'optional' in description:
                print(f"  ○ {filename:25} (not collected) - {description}")
            else:
                print(f"  ✗ {filename:25} (missing) - {description}")


def test_reddit_credentials():
    """Test Reddit API credentials."""
    print("\nTesting Reddit API credentials...")

    try:
        import praw

        # Use provided credentials
        reddit = praw.Reddit(
            client_id="L-vjF_1bqyJR1eVn25Tb8A",
            client_secret="gz5LEY0CSQbkpK70fN1-vPrwCRo4FA",
            user_agent="TCApp/1.0 by Unique_Essay_58"
        )

        # Test connection (read-only)
        reddit.read_only = True
        subreddit = reddit.subreddit('python')
        _ = subreddit.display_name

        print(f"  ✓ Reddit API connection successful")
        return True

    except Exception as e:
        print(f"  ✗ Reddit API test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print("ENVIRONMENT VERIFICATION TEST")
    print("="*70)

    results = {
        'Python version': test_python_version(),
        'Package imports': test_imports(),
        'Project structure': test_project_structure(),
        'Reddit API': test_reddit_credentials(),
    }

    # Data files test (doesn't affect pass/fail)
    test_data_files()

    print("\n" + "="*70)
    print("TEST RESULTS")
    print("="*70)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status:8} {test_name}")

    all_passed = all(results.values())

    print("="*70)

    if all_passed:
        print("\n✓ Environment is ready!")
        print("\nNext steps:")
        print("  1. Run data collection: python scripts/collect_reddit_enhanced.py")
        print("  2. Merge corpus: python scripts/merge_corpus_with_ratios.py")
        print("  3. Train tokenizer: python tokenizer/train_tokenizer.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  - Ensure conda environment is activated: conda activate llm_project")
        print("  - Try reinstalling: ./setup_env.sh remove && ./setup_env.sh create")
        return 1


if __name__ == "__main__":
    sys.exit(main())
