# Data Preprocessing for Pre-training

## Why Preprocessing Matters

**Bad preprocessing = Bad model**, even with great architecture. Issues from poor preprocessing:

- **Memorization**: Model learns URLs, timestamps, usernames instead of language patterns
- **Format artifacts**: Model copies WhatsApp formatting, markdown syntax
- **Noise amplification**: Garbage in, garbage out
- **Biased outputs**: Unfiltered political/controversial content leaks into generation
- **Poor generalization**: Overfits to irrelevant patterns

**Good preprocessing = Model learns clean language patterns**

---

## Preprocessing Steps by Data Source

### 1. WhatsApp Chats (`process_whatsapp.py`)

#### **What We Remove:**
- ✗ Timestamps (`[11/9/18, 9:24:30 AM]`)
- ✗ System messages ("Messages are end-to-end encrypted", "You added...")
- ✗ Media placeholders ("image omitted", "video omitted", "sticker omitted")
- ✗ URLs (http://..., www...)
- ✗ Phone numbers
- ✗ Specific names → Replaced with `PERSON:`

#### **What We Keep:**
- ✓ Message text
- ✓ Emojis 😂 ✓
- ✓ Hinglish (mixed Hindi-English)
- ✓ Conversational flow
- ✓ Your messages (no prefix)
- ✓ Other's messages (with `PERSON:` prefix)

#### **Structural Processing:**
- **Chunking**: Group into 3-20 turn conversations
  - **Why**: Prevents memorizing entire chat history
  - **Why**: Creates natural conversation units for training
- **Whitespace normalization**: Clean extra spaces/newlines
  - **Why**: Consistent formatting across documents

#### **Example Transformation:**

**Before:**
```
[11/9/18, 9:24:30 AM] Abhijit: Bhej be
‎[11/9/18, 9:29:18 AM] Purdue JD: ‎image omitted
[11/9/18, 9:31:16 AM] Abhijit: JD book se padh Lun ho jarga na?
```

**After:**
```
Bhej be
PERSON: JD book se padh Lun ho jarga na?
```

---

### 2. Reddit Conversations (`collect_reddit.py`)

#### **Content Filtering:**
- ✓ **Length**: 5-150 tokens (too short = noise, too long = monologue)
- ✓ **Conversational**: 2-3 turn threads only
- ✗ **Political**: Remove comments with heavy political keywords (modi, bjp, congress, etc.)
- ✗ **Code-heavy**: Remove comments with markdown code blocks (```)
- ✗ **URL spam**: Remove if >1 URL

#### **What We Remove:**
- ✗ Reddit-specific syntax (`/r/subreddit`, `u/username`)
- ✗ Markdown formatting (`**bold**`, `~~strikethrough~~`, ` `code` `)
- ✗ Markdown links `[text](url)` → keep just `text`
- ✗ URLs
- ✗ `[deleted]` and `[removed]` comments

#### **What We Keep:**
- ✓ Natural conversation threads
- ✓ Questions and explanations
- ✓ Hinglish (from Indian subreddits)
- ✓ Diverse phrasing and paraphrasing

#### **Example Transformation:**

**Before:**
```
why do people wake up early?
i think it just becomes **habit** after some time. Check out r/productivity
also depends on [work schedule](http://example.com)
```

**After:**
```
why do people wake up early?
i think it just becomes habit after some time
also depends on work schedule
```

---

### 3. Hinglish Dataset (`process_hinglish_dataset.py`)

#### **What We Remove:**
- ✗ Topic labels (`Topic: Food`)
- ✗ Metadata headers
- ✗ Speaker labels if on separate lines (`Q:`, `A:`)
- ✗ Formatting markers (`---`, `###`)

#### **What We Keep:**
- ✓ Pure conversational text
- ✓ Hinglish code-switching
- ✓ Natural dialogue flow

#### **Example Transformation:**

**Before:**
```
Topic: Food
Q: kya khaya?
A: dal chawal, tu?
---
```

**After:**
```
kya khaya?
dal chawal, tu?
```

---

### 4. General Knowledge (`collect_knowledge.py`)

#### **Quality Filtering:**
- ✓ **Length**: 20-300 words (not too short, not encyclopedic)
- ✓ **Explanation style**: Must contain explanation words (because, when, so, means, like)
- ✗ **Technical**: Reject overly technical content (theorem, derivative, etc.)
- ✗ **Listicles**: Avoid bullet-point heavy content
- ✓ **Simple language**: ELI5-style, not academic

#### **What We Remove:**
- ✗ URLs
- ✗ Reddit syntax
- ✗ Markdown formatting
- ✗ Tables and formulas

#### **What We Keep:**
- ✓ Explanatory paragraphs
- ✓ Causal reasoning ("X happens because Y")
- ✓ Simple examples
- ✓ Conceptual understanding

#### **Example:**

**Good:**
```
inflation means prices go up when money loses value
this usually happens when demand is higher than supply
```

**Bad (rejected):**
```
Inflation is defined as a sustained increase in the general price level of goods and services in an economy over a period of time. The inflation rate is calculated using the Consumer Price Index (CPI)...
```

---

## Final Corpus Processing (`merge_corpus_with_ratios.py`)

### **Balancing:**
- **Ratio control**: Ensure proper distribution (default: 50% WhatsApp, 25% Hinglish, 15% Reddit, 10% Knowledge)
- **Sampling**:
  - If too little data: Oversample (repeat documents)
  - If too much data: Undersample (randomly select)

### **Shuffling:**
- **Document-level shuffle**: Mix all sources together
- **Seed=42**: Reproducible shuffle for debugging

### **Why This Matters:**
- WhatsApp dominates (50%) → Model learns your style first
- Other sources provide breadth without drowning your style
- Random ordering prevents model from learning "WhatsApp always comes first"

---

## Universal Preprocessing Rules

Applied to ALL data sources:

### 1. **Whitespace Normalization**
```python
text = ' '.join(text.split())  # Collapse multiple spaces
text = re.sub(r'\n+', ' ', text)  # Remove multiple newlines
```

### 2. **URL Removal**
```python
text = re.sub(r'http\S+', '', text)
text = re.sub(r'www\.\S+', '', text)
```
**Why**: URLs are noise, model shouldn't memorize them

### 3. **Keep Emojis**
```python
# We DON'T remove emojis - they're part of natural conversation
```
**Why**: Emojis convey tone and emotion in chat

### 4. **Keep Hinglish**
```python
# We DON'T transliterate or translate Hindi to English
```
**Why**: Your model should handle code-switching naturally

### 5. **No Lowercasing**
```python
# We DON'T lowercase everything
```
**Why**: Capitalization carries meaning ("I" vs "i", proper nouns)

---

## Validation Checks

Before finalizing corpus:

### 1. **Length Distribution**
```
✓ No documents < 3 words (too short, likely artifacts)
✓ No more than 10% > 500 words (too long, likely monologues)
```

### 2. **Character Diversity**
```
✓ Check for repeated patterns (copy-paste artifacts)
✓ Ensure mix of English and Hindi characters
```

### 3. **Token Estimation**
```
tokens ≈ words × 1.3 (for English/Hinglish)
```

### 4. **Ratio Validation**
```
✓ WhatsApp dominates (40-60%)
✓ Knowledge is minority (5-15%)
✓ Total within target range
```

---

## Common Preprocessing Mistakes to Avoid

### ❌ **Over-preprocessing**
- Don't remove ALL punctuation
- Don't remove ALL numbers
- Don't transliterate Hindi

### ❌ **Under-preprocessing**
- Don't include timestamps
- Don't include usernames
- Don't include system messages

### ❌ **Inconsistent preprocessing**
- Same rules across all sources
- Same whitespace handling
- Same emoji handling

### ❌ **No validation**
- Always check sample outputs
- Always verify token counts
- Always review edge cases

---

## Quality Checklist

Before training, verify:

- [ ] No timestamps in corpus
- [ ] No URLs in corpus
- [ ] No usernames/phone numbers
- [ ] Emojis preserved
- [ ] Hinglish preserved
- [ ] WhatsApp dominates token distribution
- [ ] Total tokens: 2-5M
- [ ] Documents are conversation-sized (not too long/short)
- [ ] Data is shuffled
- [ ] Sample outputs look natural

---

## Impact on 60M Parameter Model

With clean preprocessing:
- **Faster convergence**: Model learns patterns, not noise
- **Better generalization**: Focuses on language, not formatting
- **Style preservation**: Your WhatsApp style shines through
- **No hallucination of URLs/names**: Model hasn't memorized them

With poor preprocessing:
- **Slow convergence**: Wastes capacity on artifacts
- **Poor outputs**: Generates timestamps, usernames, "image omitted"
- **Format pollution**: Outputs markdown, Reddit syntax
- **Overfitting**: Memorizes specific URLs, names, dates

---

## Recommended Reading Order

1. This document (preprocessing rationale)
2. Individual script files (implementation details)
3. `QUICKSTART.md` (how to run)
4. Sample outputs from `data/raw/*` (verify quality)

---

**Bottom line**: Preprocessing is NOT optional. It's as important as model architecture for a 60M parameter model with limited training data.
