# Environment Setup Guide

Complete guide for setting up the conda environment for the LLM project.

## Quick Start

```bash
# 1. Create conda environment
./setup_env.sh create

# 2. Activate environment
conda activate llm_project

# 3. Verify installation
python -c "import praw; print('✓ Environment ready!')"
```

---

## Prerequisites

### Install Conda

If you don't have conda installed:

**Option 1: Miniconda (Recommended - Lightweight)**
```bash
# Mac (Intel)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh

# Mac (M1/M2)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
```

**Option 2: Anaconda (Full featured)**
Download from: https://www.anaconda.com/download

After installation, restart your terminal.

---

## Environment Management

### Create Environment

```bash
./setup_env.sh create
```

This will:
- Create a conda environment named `llm_project`
- Install Python 3.10
- Install all dependencies from `environment.yml`

### Activate Environment

```bash
conda activate llm_project
```

You should see `(llm_project)` in your terminal prompt.

### Deactivate Environment

```bash
conda deactivate
```

---

## Managing Dependencies

### Install Additional Package

**Via conda (preferred):**
```bash
./setup_env.sh install sentencepiece
```

**Or manually:**
```bash
conda activate llm_project
conda install sentencepiece
# If not available in conda:
pip install sentencepiece
```

### Update All Dependencies

After modifying `environment.yml`:
```bash
./setup_env.sh update
```

### List Installed Packages

```bash
./setup_env.sh list
```

---

## Environment Maintenance

### Export Environment (for reproducibility)

Export with exact versions:
```bash
./setup_env.sh export
```

This creates `environment_export.yml` with pinned versions.

### Clean Cache

Remove unused packages and cache:
```bash
./setup_env.sh clean
```

### Remove Environment

To completely remove the environment:
```bash
./setup_env.sh remove
```

---

## All Available Commands

```bash
./setup_env.sh create        # Create new environment
./setup_env.sh remove        # Remove environment
./setup_env.sh update        # Update dependencies
./setup_env.sh export        # Export with exact versions
./setup_env.sh list          # List installed packages
./setup_env.sh clean         # Clean cache
./setup_env.sh install PKG   # Install additional package
./setup_env.sh info          # Show environment info
./setup_env.sh activate      # Show activation instructions
./setup_env.sh help          # Show help
```

---

## Adding New Dependencies

### For Data Collection Phase (Current)

Edit `environment.yml`:
```yaml
dependencies:
  - pip:
      - your-package>=1.0.0
```

Then update:
```bash
./setup_env.sh update
```

### For Future Phases (Tokenizer, Training)

Uncomment the relevant sections in `environment.yml`:

```yaml
dependencies:
  - pip:
      # Uncomment when needed:
      - sentencepiece>=0.1.99   # For tokenizer training
      - torch>=2.0.0            # For model training
```

Then:
```bash
./setup_env.sh update
```

---

## Troubleshooting

### "conda: command not found"

Conda is not in your PATH. Add to `~/.zshrc` or `~/.bashrc`:
```bash
export PATH="$HOME/miniconda3/bin:$PATH"
```

Then:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Environment creation fails

Try creating manually:
```bash
conda env create -f environment.yml
```

Check error messages for missing dependencies.

### Package conflicts

Remove and recreate:
```bash
./setup_env.sh remove
./setup_env.sh create
```

### Slow package resolution

Use mamba (faster conda alternative):
```bash
conda install mamba -n base -c conda-forge
mamba env create -f environment.yml
```

---

## Best Practices

### 1. Always Activate Before Working

```bash
conda activate llm_project
python scripts/process_whatsapp.py  # ✓ Good
```

Not:
```bash
python scripts/process_whatsapp.py  # ✗ Bad (uses system Python)
```

### 2. Keep environment.yml Updated

When you install new packages manually, update `environment.yml`:
```bash
# After: conda install new-package
# Update environment.yml with: - new-package>=x.y.z
```

### 3. Use Environment Export for Reproducibility

Before major milestones:
```bash
./setup_env.sh export
git add environment_export.yml
git commit -m "Checkpoint: working environment"
```

### 4. Clean Regularly

```bash
./setup_env.sh clean  # Run monthly
```

---

## Verifying Installation

After creating the environment:

```bash
conda activate llm_project

# Test Python
python --version
# Should show: Python 3.10.x

# Test imports
python -c "import numpy; import pandas; import praw; print('✓ All imports successful')"

# Check package versions
python -c "import praw; print(f'praw version: {praw.__version__}')"
```

---

## Integration with Data Scripts

All data collection scripts will automatically use the conda environment if activated:

```bash
# Activate once
conda activate llm_project

# Run all scripts
python scripts/process_whatsapp.py
python scripts/collect_reddit_enhanced.py
python scripts/collect_knowledge.py
python scripts/merge_corpus_with_ratios.py
```

---

## Next Steps

After environment setup:

1. ✓ Verify installation (see above)
2. ✓ Run data collection scripts
3. When ready for tokenizer training:
   - Uncomment `sentencepiece` in `environment.yml`
   - Run `./setup_env.sh update`
4. When ready for model training:
   - Uncomment `torch` and `transformers` in `environment.yml`
   - Run `./setup_env.sh update`

---

## File Reference

- `environment.yml` - Conda environment specification
- `setup_env.sh` - Environment management script
- `requirements.txt` - Pip-only fallback (for backwards compatibility)
- `environment_export.yml` - Exported environment with exact versions (auto-generated)

---

**Ready to go!** 🚀

Run `./setup_env.sh create` to get started.
