# Lab Test Result Outcome Categorization Summary

## Overview

Successfully categorized 879 unique non-numeric lab test results into three categories using abbreviated labels:

- **bn**: Below Normal (54 results, 6.1%)
- **n**: Normal (596 results, 67.8%)
- **an**: Above Normal (229 results, 26.1%)

## Categorization Logic Applied

### 1. Positive/Negative Results

- **Negative results**: Generally categorized as "n" (normal) for most tests
- **Positive results**: Categorized based on test type:
  - Infection markers (Brucella, Hepatitis, HIV, etc.): "an" (abnormal)
  - Pregnancy tests: "an" (above normal/positive)
  - Blood group typing: "n" (normal - just identification)

### 2. Comparison Operators (< and >)

Applied test-specific normal ranges for results like:

- `< 0.1` for Beta-hCG → "n" (normal, not pregnant)
- `> 1100` for Albumin-to-Creatinine Ratio → "an" (above normal)
- `< 5` for Anti-Thyroid Peroxidase → "n" (normal)

### 3. Time-based Results

- **Bleeding Time**: Normal range 2-9 minutes
  - `1:00`, `1:15`, `1:30`, `1:45` → "bn" (below normal, too fast)
  - `2:00` to `5:30` → "n" (normal)
  - `6:30` and above → "an" (above normal, too slow)

- **Clotting Time**: Normal range 5-15 minutes
  - Under 5 minutes → "bn" (too fast)
  - 5-15 minutes → "n" (normal)
  - Over 15 minutes → "an" (too slow)

### 4. Percentage Values

- **Packed Cell Volume (Hematocrit)**: Normal range 36-46%
  - Below 36% → "bn"
  - 36-46% → "n"
  - Above 46% → "an"

### 5. Special Cases

- **Blood Group Results**: All categorized as "n" (normal identification)
- **Attach/Attached** (CBC reports): "n" (normal documentation)
- **Missing values** (., #NAME?): "n" (default to normal)
- **"No growth"** (cultures): "n" (normal, no infection)
- **"Hyphae of Fungi presence"**: "an" (abnormal, infection present)
- **"Suspected"** results: "an" (concerning, needs follow-up)

### 6. Numeric Patterns with Special Formatting

- **Comma decimal separators**: `"12,2"` → parsed as 12.2
- **Double dots**: `"5..81"` → parsed as 5.81
- **Special characters**: `"69*"`, `"`196"` → extracted numeric values

## Test-Specific Normal Ranges Applied

| Test Category | Normal Range | Below Normal | Above Normal |
|---------------|--------------|--------------|--------------|
| TSH | 0.4-4.0 mIU/L | < 0.4 | > 4.0 |
| Free T4 | 0.8-1.8 ng/dL | < 0.8 | > 1.8 |
| HbA1c | 4.0-5.6% | < 4.0 | > 5.6 |
| Vitamin D3 | 30-100 ng/mL | < 30 | > 100 |
| PSA | 0-4 ng/mL | Very low < 0.01 | > 4 |
| Ferritin | 15-150 ng/mL | < 15 | > 150 |
| Triglycerides | 0-150 mg/dL | N/A | > 150 |

## Quality Assurance

- Handled multiple spelling variations (Positive/Positve/Possitive)
- Processed various negative formats (-ve, -Ve, (-ve), etc.)
- Applied context-aware logic (positive pregnancy test ≠ positive infection test)
- Maintained consistency across similar test types

## Files Updated

- **Input**: `processed_data/non_numeric_results_analysis.csv` (Original data)
- **Output**: Same file with added `Outcome` column containing bn/n/an categories
- **Script**: `categorize_outcomes.py` (Categorization logic)

## Validation

The categorization successfully processed all 879 unique result patterns with appropriate medical logic applied to ensure clinical relevance.
