# ai_strength_model.py
import random
import string
import math  # For logarithmic calculations

# Global variable to store loaded wordlists to avoid re-loading
_WORDLISTS = {}


# Function to load wordlist (duplicated from password_generator.py for self-containment)
def load_wordlist(filepath="eff_long_wordlist.txt"):
    # Use a dictionary to cache loaded wordlists
    if filepath in _WORDLISTS:
        return _WORDLISTS[filepath]

    try:
        with open(filepath, 'r') as f:
            words = [line.strip() for line in f if line.strip()]
        if not words:
            raise ValueError(
                f"Wordlist file '{filepath}' is empty or could not be read.")
        _WORDLISTS[filepath] = words  # Cache the loaded wordlist
        return words
    except FileNotFoundError:
        # Create dummy wordlists if not found for demonstration purposes
        print(
            f"Warning: Wordlist file not found at: {filepath}. Using a dummy wordlist for AI strength prediction."
        )
        if filepath == "eff_long_wordlist.txt":
            dummy_words = [
                "apple", "banana", "cherry", "date", "elephant", "flower",
                "garden", "happiness", "internet", "jungle", "kangaroo",
                "lemon", "mountain", "night", "ocean", "penguin", "queen",
                "rainbow", "sunshine", "tiger", "umbrella", "violet",
                "whisper", "xylophone", "yellow", "zebra"
            ]
        elif filepath == "eff_short_wordlist.txt":
            dummy_words = [
                "cat", "dog", "bird", "fish", "tree", "rock", "sky", "moon",
                "star", "cloud"
            ]
        else:
            dummy_words = ["word1", "word2", "word3"]  # Generic fallback

        _WORDLISTS[filepath] = dummy_words  # Cache the dummy wordlist
        return dummy_words
    except Exception as e:
        print(f"Error loading wordlist for AI strength prediction: {e}")
        return []  # Return empty list on error


def predict_strength(
    length: int,
    include_uppercase: bool,
    include_lowercase: bool,
    include_digits: bool,
    include_symbols: bool,
    exclude_ambiguous: bool,
    exclude_custom_chars: str,
    custom_character_set: str = '',
    is_passphrase: bool = False,
    num_words: int = 0,
    require_min_char_types: bool = False,  # NEW: Parameter for AI prediction
    no_repeating_chars: bool = False,  # NEW: Parameter for AI prediction
    wordlist_name: str = "eff_long_wordlist.txt"
) -> int:  # NEW: Parameter for wordlist name
    """
    A simplified "AI" function to predict password strength based on characteristics.
    Returns a score from 0 (Very Weak) to 4 (Strong).

    This is a rule-based approximation. A real AI system would involve trained ML models.
    """
    score = 0
    entropy_score = 0  # Represents character set diversity or wordlist size

    if is_passphrase:
        # Passphrase specific logic
        if num_words >= 5:
            score += 1
        if num_words >= 8:
            score += 1  # Very strong passphrase

        # Load the specific wordlist to get its size for entropy calculation
        current_wordlist = load_wordlist(wordlist_name)
        wordlist_size = len(
            current_wordlist
        ) if current_wordlist else 1  # Avoid division by zero

        # Base character set for additional chars in passphrase (digits/symbols)
        base_chars_for_passphrase_extras = 0
        if include_digits:
            base_chars_for_passphrase_extras += 10
        if include_symbols:
            base_chars_for_passphrase_extras += 32  # Common symbols

        # Logarithmic calculation for entropy based on word length and wordlist size
        # This is a simplification; actual passphrase entropy is complex.
        # Entropy = log2(wordlist_size)^num_words + log2(base_chars_for_passphrase_extras) * (num_digits + num_symbols)
        # Simplified heuristic:
        if wordlist_size > 1:
            entropy_score = (num_words * math.log2(wordlist_size)) + (
                base_chars_for_passphrase_extras / 2)
        else:
            entropy_score = (num_words * 5) + (
                base_chars_for_passphrase_extras / 2
            )  # Fallback if wordlist is tiny/empty

        # Map entropy score to strength
        if entropy_score < 30:  # Example thresholds
            final_score = 0  # Very Weak
        elif entropy_score < 50:
            final_score = 1  # Weak
        elif entropy_score < 80:
            final_score = 2  # Fair
        elif entropy_score < 120:
            final_score = 3  # Good
        else:
            final_score = 4  # Strong

    else:
        # Character password specific logic
        char_set_size = 0
        if custom_character_set:
            char_set_size = len(set(custom_character_set))
        else:
            if include_uppercase:
                char_set_size += 26
            if include_lowercase:
                char_set_size += 26
            if include_digits:
                char_set_size += 10
            if include_symbols:
                char_set_size += 32  # Common symbols

        # Apply exclusions to character set size (approximation)
        if exclude_ambiguous:
            # Estimate reduction due to ambiguous chars (e.g., 10-15 chars)
            char_set_size = max(1, char_set_size - 10)
        if exclude_custom_chars:
            char_set_size = max(1,
                                char_set_size - len(set(exclude_custom_chars)))

        if char_set_size > 0:
            # Shannon entropy approximation: length * log2(charset_size)
            entropy_score = length * math.log2(char_set_size)
        else:
            entropy_score = 0  # Should ideally be caught by validation

        # Adjust score based on entropy
        if entropy_score < 40:  # Example thresholds (adjust as needed)
            score = 0  # Very Weak
        elif entropy_score < 60:
            score = 1  # Weak
        elif entropy_score < 80:
            score = 2  # Fair
        elif entropy_score < 100:
            score = 3  # Good
        else:
            score = 4  # Strong

        # NEW: Adjust score based on new password generation rules
        if require_min_char_types:
            # This makes the password more robust, so slightly increase perceived strength
            score = min(4, score + 0.5)  # Add half a point, cap at 4
        if no_repeating_chars:
            # Prevents simple patterns, increasing strength
            score = min(4, score + 0.5)  # Add half a point, cap at 4

        # Convert float score to int for final output
        final_score = int(score)

    # Ensure score is within bounds [0, 4]
    return max(0, min(4, final_score))


if __name__ == "__main__":
    print("--- AI Strength Predictions (Character Passwords) ---")
    print(
        f"Length 8, lower only: {predict_strength(8, False, True, False, False, False, '')}"
    )  # Expected: Low
    print(
        f"Length 12, all types: {predict_strength(12, True, True, True, True, False, '')}"
    )  # Expected: Medium-Good
    print(
        f"Length 16, all types: {predict_strength(16, True, True, True, True, False, '')}"
    )  # Expected: Good-Strong
    print(
        f"Length 20, all types, custom excluded 'a': {predict_strength(20, True, True, True, True, False, 'a')}"
    )  # Expected: Strong
    print(
        f"Length 12, all types, require min char types: {predict_strength(12, True, True, True, True, False, '', require_min_char_types=True)}"
    )  # Expected: Slightly higher
    print(
        f"Length 12, all types, no repeating: {predict_strength(12, True, True, True, True, False, '', no_repeating_chars=True)}"
    )  # Expected: Slightly higher
    print(
        f"Length 16, all types, no repeating, min char types: {predict_strength(16, True, True, True, True, False, '', require_min_char_types=True, no_repeating_chars=True)}"
    )  # Expected: Even higher

    print("\n--- AI Strength Predictions (Passphrases) ---")
    print(
        f"4 words, long wordlist: {predict_strength(0, False, False, False, False, False, '', is_passphrase=True, num_words=4, wordlist_name='eff_long_wordlist.txt')}"
    )  # Expected: Medium
    print(
        f"6 words, short wordlist, with digit/symbol: {predict_strength(0, False, False, False, False, False, '', is_passphrase=True, num_words=6, include_digits=True, include_symbols=True, wordlist_name='eff_short_wordlist.txt')}"
    )  # Expected: Good
    print(
        f"8 words, long wordlist, no digit/symbol: {predict_strength(0, False, False, False, False, False, '', is_passphrase=True, num_words=8, wordlist_name='eff_long_wordlist.txt')}"
    )  # Expected: Strong
