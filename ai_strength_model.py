# ai_strength_model.py

def predict_strength(length: int, include_uppercase: bool, include_lowercase: bool,
                     include_digits: bool, include_symbols: bool,
                     exclude_ambiguous: bool, exclude_custom_chars: str,
                     custom_character_set: str = '',
                     is_passphrase: bool = False, num_words: int = 0) -> int:
    """
    A simplified "AI" function to predict password strength based on characteristics.
    Returns a score from 0 (Very Weak) to 4 (Strong).

    This is a rule-based approximation. A real AI system would involve trained ML models.
    """
    score = 0
    entropy_score = 0 # Represents character set diversity

    if is_passphrase:
        # Passphrase specific logic
        if num_words >= 5:
            score += 1
        if num_words >= 8:
            score += 1 # Very strong passphrase
        # Simulating character set for passphrase
        base_chars = 26 # Lowercase words roughly
        if include_digits:
            base_chars += 10
        if include_symbols:
            base_chars += 32 # Common symbols
        # Logarithmic calculation for entropy based on word length and character set
        # This is a simplification; actual passphrase entropy is complex.
        entropy_score = (num_words * 11) + (base_chars / 5) # Heuristic for word entropy
    else:
        # Character password specific logic
        char_types_count = 0
        if custom_character_set:
            # If custom set is used, entropy is based on its unique characters
            entropy_score = len(set(custom_character_set))
            if entropy_score > 30: # Good diverse custom set
                score += 1
        else:
            if include_lowercase: char_types_count += 1
            if include_uppercase: char_types_count += 1
            if include_digits: char_types_count += 1
            if include_symbols: char_types_count += 1

            if char_types_count >= 3:
                score += 1 # Good mix of character types
            if char_types_count == 4:
                score += 1 # Excellent mix

            # Base entropy score on the number of character types
            if char_types_count == 1: entropy_score = 26 # e.g., only lowercase
            elif char_types_count == 2: entropy_score = 26 + 10 # e.g., lower + digits
            elif char_types_count == 3: entropy_score = 26 + 26 + 10 # e.g., lower+upper+digits
            elif char_types_count == 4: entropy_score = 26 + 26 + 10 + 32 # All common types

            # Adjust for ambiguous and custom exclusions
            if exclude_ambiguous:
                # Ambiguous chars like l1IO0 are often 5 characters
                # If they were included and now excluded, effectively reduces charset size
                if 'l' in custom_character_set or '1' in custom_character_set:
                   entropy_score = max(1, entropy_score - 5) # Approx reduction
            if exclude_custom_chars:
                entropy_score = max(1, entropy_score - len(set(exclude_custom_chars)))

        # Length contribution
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        if length >= 20:
            score += 1


    # Final score based on accumulated points and a basic entropy consideration
    # Max score is 4 (Strong)
    # This scaling is a simple heuristic, not based on true cryptographic entropy
    final_score = 0
    if entropy_score > 0 and length > 0: # Ensure no division by zero
        # This is a highly simplified proxy for entropy.
        # Real entropy calculation uses log2(charset_size) * length
        # For simplicity, we'll map a raw "strength_value" to 0-4
        strength_value = (score * 5) + (entropy_score / 5) + (length / 2)

        if strength_value < 10:
            final_score = 0 # Very Weak
        elif strength_value < 20:
            final_score = 1 # Weak
        elif strength_value < 35:
            final_score = 2 # Fair
        elif strength_value < 55:
            final_score = 3 # Good
        else:
            final_score = 4 # Strong

    # Ensure score is within bounds [0, 4]
    return max(0, min(4, final_score))

if __name__ == "__main__":
    print("--- AI Strength Predictions (Character Passwords) ---")
    print(f"Length 8, lower only: {predict_strength(8, False, True, False, False, False, '')}") # Expected: Low
    print(f"Length 12, all types: {predict_strength(12, True, True, True, True, False, '')}") # Expected: Medium-Good
    print(f"Length 16, all types: {predict_strength(16, True, True, True, True, False, '')}") # Expected: Good-Strong
    print(f"Length 20, all types, custom excluded 'a': {predict_strength(20, True, True, True, True, False, 'a')}") # Expected: Strong

    print("\n--- AI Strength Predictions (Passphrases) ---")
    print(f"4 words, no digit/symbol: {predict_strength(0, False, False, False, False, False, '', is_passphrase=True, num_words=4)}") # Expected: Medium
    print(f"6 words, with digit/symbol: {predict_strength(0, False, False, False, False, False, '', is_passphrase=True, num_words=6, include_digits=True, include_symbols=True)}") # Expected: Good
    print(f"8 words, with digit/symbol: {predict_strength(0, False, False, False, False, False, '', is_passphrase=True, num_words=8, include_digits=True, include_symbols=True)}") # Expected: Strong