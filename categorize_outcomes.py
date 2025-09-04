import pandas as pd
import re

def categorize_lab_result(result, test_name):
    """
    Categorize lab test results as 'bn' (below normal), 'n' (normal), or 'an' (above normal)
    based on the result value and test name
    """
    result_str = str(result).strip() if pd.notna(result) else ''
    test_name_str = str(test_name).lower().strip()
    
    # Handle missing or invalid results
    if result_str in ['.', '', '#NAME?', 'nan']:
        return 'n'  # Default to normal for missing data
    
    # Handle "attach" variations for Complete Blood Count
    if 'attach' in result_str.lower():
        return 'n'  # CBC attached reports are typically normal documentation
    
    # Extract numeric value from comparison operators (<, >, >=, <=)
    def extract_numeric_from_comparison(text):
        # Handle patterns like "< 5", "> 100", "≤ 10", etc.
        patterns = [
            r'[<>≤≥]\s*(\d+(?:\.\d+)?)',  # < 5, > 100, etc.
            r'(\d+(?:\.\d+)?)\s*[<>]',    # 5<, 100>, etc.
            r'[<>≤≥]\s*(\d+(?:,\d+)*(?:\.\d+)?)',  # Handle comma separators
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    return float(value_str)
                except ValueError:
                    continue
        return None
    
    # Handle percentage values
    if '%' in result_str:
        try:
            numeric_value = float(result_str.replace('%', ''))
            # For packed cell volume (hematocrit)
            if 'packed cell volume' in test_name_str or 'hematocrit' in test_name_str:
                if numeric_value < 36:
                    return 'bn'
                elif numeric_value > 46:
                    return 'an'
                else:
                    return 'n'
        except ValueError:
            pass
    
    # Handle time format results (for bleeding time, clotting time)
    if ':' in result_str and any(word in test_name_str for word in ['bleeding', 'clotting']):
        try:
            parts = result_str.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                total_seconds = minutes * 60 + seconds
                
                if 'bleeding' in test_name_str:
                    # Normal bleeding time: 2-9 minutes (120-540 seconds)
                    if total_seconds < 120:
                        return 'bn'
                    elif total_seconds > 540:
                        return 'an'
                    else:
                        return 'n'
                elif 'clotting' in test_name_str:
                    # Normal clotting time: 5-15 minutes (300-900 seconds)
                    if total_seconds < 300:
                        return 'bn'
                    elif total_seconds > 900:
                        return 'an'
                    else:
                        return 'n'
        except ValueError:
            pass
    
    # Handle blood group results (all normal)
    if 'blood group' in test_name_str and any(group in result_str.upper() for group in ['A', 'B', 'O', 'AB']):
        return 'n'
    
    # Handle positive/negative results
    positive_indicators = ['positive', '+ve', '+v', 'positve', 'possitive', 'posative', 'posetive', 'reactiv', 'detected', 'presence']
    negative_indicators = ['negative', '-ve', '-v', 'negativ', 'negatv', 'negetive', 'not detected', 'absent', 'no reactive']
    
    result_lower = result_str.lower()
    
    # Check for positive indicators
    if any(indicator in result_lower for indicator in positive_indicators):
        # For certain tests, positive is normal
        if any(test in test_name_str for test in ['blood group', 'covid-19 igg']):
            return 'n'
        # For infection/disease markers, positive is abnormal
        elif any(test in test_name_str for test in ['brucella', 'typhoid', 'helicobacter', 'hepatitis', 'hiv', 'pregnancy', 'beta-hcg']):
            return 'an'
        # For inflammation markers like CRP, positive usually means elevated
        elif any(test in test_name_str for test in ['c-reactive', 'crp', 'rheumatoid', 'occult blood']):
            return 'an'
        else:
            return 'an'  # Default: positive is abnormal
    
    # Check for negative indicators
    if any(indicator in result_lower for indicator in negative_indicators):
        # For most tests, negative is normal
        return 'n'
    
    # Handle weak positive results
    if 'weak' in result_lower and any(indicator in result_lower for indicator in positive_indicators):
        # Weak positive is usually mildly abnormal
        return 'an'
    
    # Handle comparison operators with extracted values
    numeric_value = extract_numeric_from_comparison(result_str)
    if numeric_value is not None:
        # Define test-specific normal ranges for comparison results
        test_ranges = {
            'albumin-to-creatinine ratio': (0, 30),  # > 1100 is very high
            'alpha-fetoprotein': (0, 10),  # < 0.75 is normal
            'anti-cyclic citrullinated peptide': (0, 20),  # < 1 is normal, >100 is high
            'anti-thyroid peroxidase antibody': (0, 35),  # < 5 normal, >600-1000 high
            'beta-hcg': (0, 5),  # < 0.1 normal, >10000 very high
            'ca 19-9': (0, 37),  # < 0.6 is normal
            'carcinoembryonic antigen': (0, 3),  # < 0.2 is normal
            'd-dimer': (0, 0.5),  # < 0.1 normal, > 20 very high
            'estradiol': (15, 350),  # < 5 is low
            'fecal calprotectein': (0, 50),  # > 60 is high
            'fecal occult blood': (0, 7),  # < 7.5 is normal
            'follicle-stimulating hormone': (1.5, 12.4),  # < 0.3 is low
            'free t4': (0.8, 1.8),  # < 0.005 very low, > 100 very high
            'gamma-glutamyl transferase': (7, 64),  # > 1200 very high
            'hiv antibody': (0, 1),  # < 0.1 is normal
            'high-sensitivity troponin t': (0, 14),  # < 3 is normal
            'immunoglobulin e': (0, 100),  # < 1.0 might be low
            'luteinizing hormone': (1.7, 8.6),  # < 0.1 is low
            'n-terminal pro-b-type natriuretic peptide': (0, 125),  # < 50 normal, > 25000 very high
            'parathyroid hormone': (15, 65),  # < 2.40 is low
            'progesterone': (0.2, 25),  # < 0.25 might be low, > 60 high
            'prolactin': (4, 23),  # < 0.047 is low
            'prostate-specific antigen': (0, 4),  # < 0.006 very low, > 100 very high
            'rheumatoid factor': (0, 14),  # < 3 normal, > 160 high
            'serum ferritin': (15, 150),  # < 0.5 very low, > 2000 very high
            'serum triglycerides': (0, 150),  # > 500 high
            'stool for calprotectin': (0, 50),  # < 15 normal
            'tsh': (0.4, 4.0),  # < 0.005 very low, > 100 very high
            'testosterone': (300, 1000),  # < 0.025 very low, > 15 might be normal range
            'thyroglobulin': (1.4, 78),  # < 0.04 is low
            'tissue transglutaminase': (0, 20),  # < 3 is normal
            'triglycerides': (0, 150),  # < 1178 might be borderline
            'triiodothyronine': (80, 200),  # > 10 might be in normal range
            'urine albumin': (0, 30),  # > 66 is high
            'vitamin b12': (200, 900),  # < 50 low, > 2000 high
            'vitamin d3': (30, 100),  # < 3 deficient, > 120 toxic
        }
        
        # Find matching test range
        for test_key, (low, high) in test_ranges.items():
            if test_key in test_name_str:
                # Handle < comparisons
                if '<' in result_str:
                    if numeric_value < low:
                        return 'bn'
                    else:
                        return 'n'
                # Handle > comparisons
                elif '>' in result_str:
                    if numeric_value > high:
                        return 'an'
                    else:
                        return 'n'
                break
    
    # Handle numeric values with decimal separators (comma instead of dot)
    if ',' in result_str and '"' in result_str:
        try:
            # Handle format like "12,2" or "5,88"
            clean_value = result_str.replace('"', '').replace(',', '.')
            numeric_value = float(clean_value)
            
            # Determine normal ranges based on test name
            if 'ast' in test_name_str or 'aspartate' in test_name_str:
                # AST normal range: 8-40 U/L
                if numeric_value < 8:
                    return 'bn'
                elif numeric_value > 40:
                    return 'an'
                else:
                    return 'n'
            elif 'hba1c' in test_name_str:
                # HbA1c normal range: 4.0-5.6%
                if numeric_value < 4.0:
                    return 'bn'
                elif numeric_value > 5.6:
                    return 'an'
                else:
                    return 'n'
            elif 'tsh' in test_name_str:
                # TSH normal range: 0.4-4.0 mIU/L
                if numeric_value < 0.4:
                    return 'bn'
                elif numeric_value > 4.0:
                    return 'an'
                else:
                    return 'n'
            elif 'vitamin d' in test_name_str:
                # Vitamin D normal range: 30-100 ng/mL
                if numeric_value < 30:
                    return 'bn'
                elif numeric_value > 100:
                    return 'an'
                else:
                    return 'n'
        except ValueError:
            pass
    
    # Handle other special numeric patterns
    if '..' in result_str:
        try:
            # Handle format like "5..81" or "18..1"
            clean_value = result_str.replace('..', '.')
            numeric_value = float(clean_value)
            
            if 'free t3' in test_name_str:
                # Free T3 normal range: 2.3-4.2 pg/mL
                if numeric_value < 2.3:
                    return 'bn'
                elif numeric_value > 4.2:
                    return 'an'
                else:
                    return 'n'
            elif 'free t4' in test_name_str:
                # Free T4 normal range: 0.8-1.8 ng/dL
                if numeric_value < 0.8:
                    return 'bn'
                elif numeric_value > 1.8:
                    return 'an'
                else:
                    return 'n'
            elif 'luteinizing hormone' in test_name_str:
                # LH varies by gender and cycle, use broad range
                if numeric_value < 1:
                    return 'bn'
                elif numeric_value > 20:
                    return 'an'
                else:
                    return 'n'
        except ValueError:
            pass
    
    # Handle special cases
    if 'no growth' in result_lower:
        return 'n'  # No growth in culture is normal
    
    if 'hyphae of fungi' in result_lower:
        return 'an'  # Fungal presence is abnormal
    
    if 'suspected' in result_lower:
        return 'an'  # Suspected results are concerning
    
    # Handle other numeric patterns with special characters
    numeric_patterns = [
        r'(\d+)\s*\*',  # Numbers with asterisk like "69*"
        r'`(\d+)',      # Numbers with backtick like "`196"
        r'(\d+)\.;(\d+)', # Numbers with .; like "28.;91"
        r'(\d+)`\.(\d+)', # Numbers with `. like "31`.43"
    ]
    
    for pattern in numeric_patterns:
        match = re.search(pattern, result_str)
        if match:
            try:
                if len(match.groups()) == 1:
                    numeric_value = float(match.group(1))
                else:
                    # Combine groups for decimal numbers
                    numeric_value = float(f"{match.group(1)}.{match.group(2)}")
                
                # Apply general ranges based on test type
                if 'cholesterol' in test_name_str:
                    if numeric_value > 200:
                        return 'an'
                    else:
                        return 'n'
                elif 'chloride' in test_name_str:
                    # Normal chloride: 98-107 mEq/L
                    if numeric_value < 98:
                        return 'bn'
                    elif numeric_value > 107:
                        return 'an'
                    else:
                        return 'n'
                elif 'urea' in test_name_str:
                    # Normal BUN: 7-20 mg/dL
                    if numeric_value < 7:
                        return 'bn'
                    elif numeric_value > 45:
                        return 'an'
                    else:
                        return 'n'
                
            except ValueError:
                continue
    
    # Default case for unrecognized patterns
    return 'n'  # Default to normal when uncertain

# Read the CSV file
df = pd.read_csv('processed_data/non_numeric_results_analysis.csv')

print(f"Processing {len(df)} records...")

# Apply the categorization function
df['Outcome'] = df.apply(lambda row: categorize_lab_result(row['Result'], row['Standard Test Name']), axis=1)

# Show distribution of outcomes
print("\nOutcome distribution:")
print(df['Outcome'].value_counts())
print(f"\nPercentage distribution:")
print(df['Outcome'].value_counts(normalize=True) * 100)

# Save the updated CSV
df.to_csv('processed_data/non_numeric_results_analysis.csv', index=False)

# Show some examples of each category
print("\n=== EXAMPLES OF EACH CATEGORY ===")

print("\nBELOW NORMAL (bn) examples:")
bn_examples = df[df['Outcome'] == 'bn'].head(10)
for _, row in bn_examples.iterrows():
    print(f"  {row['Standard Test Name']}: '{row['Result']}' -> {row['Outcome']}")

print("\nNORMAL (n) examples:")
n_examples = df[df['Outcome'] == 'n'].head(10)
for _, row in n_examples.iterrows():
    print(f"  {row['Standard Test Name']}: '{row['Result']}' -> {row['Outcome']}")

print("\nABOVE NORMAL (an) examples:")
an_examples = df[df['Outcome'] == 'an'].head(10)
for _, row in an_examples.iterrows():
    print(f"  {row['Standard Test Name']}: '{row['Result']}' -> {row['Outcome']}")

print("\nProcessing complete! Updated file saved as 'processed_data/non_numeric_results_analysis.csv'")
