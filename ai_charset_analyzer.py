# ai_charset_analyzer.py
import string

# Expanded ambiguous characters list (consistent with password_generator.py)
AMBIGUOUS_CHARS = 'Il1Lo0O|[]{}()/\'"`~,.;:<> '

def analyze_charset_definition(
    include_uppercase: bool,
    include_lowercase: bool,
    include_digits: bool,
    include_symbols: bool,
    exclude_ambiguous: bool,
    exclude_custom_chars: str,
    custom_character_set: str = '',
    no_repeating_chars: bool = False
) -> str:
    """
    A simplified "AI" function to analyze the user's character set definition.
    Provides a recommendation/warning based on common security practices.
    """
    recommendations = []

    # Calculate the effective character set size
    effective_charset_size = 0
    if custom_character_set:
        effective_charset_size = len(set(custom_character_set))
    else:
        if include_uppercase: effective_charset_size += 26
        if include_lowercase: effective_charset_size += 26
        if include_digits: effective_charset_size += 10
        if include_symbols: effective_charset_size += 32 # Common symbols

        # Apply exclusions to the calculated size (approximation)
        if exclude_ambiguous:
            effective_charset_size = max(1, effective_charset_size - len(set(AMBIGUOUS_CHARS)))
        if exclude_custom_chars:
            effective_charset_size = max(1, effective_charset_size - len(set(exclude_custom_chars)))

    if custom_character_set:
        # Analyze custom character set
        if effective_charset_size < 20:
            recommendations.append("Consider a larger custom character set for better entropy.")
        if any(char.isspace() for char in custom_character_set):
            recommendations.append("Avoid spaces in custom character set as they can be problematic.")
        if len(set(custom_character_set.lower())) == 1 and effective_charset_size > 1:
            recommendations.append("Custom set contains only one type of character (e.g., 'aaaaa' or '11111'). Diversify!")

    else:
        # Analyze standard character type selections
        selected_types_count = 0
        if include_uppercase: selected_types_count += 1
        if include_lowercase: selected_types_count += 1
        if include_digits: selected_types_count += 1
        if include_symbols: selected_types_count += 1

        if selected_types_count < 2:
            recommendations.append("Consider including more character types (e.g., uppercase, lowercase, digits, symbols) for better diversity.")
        if selected_types_count == 0:
            recommendations.append("No character types selected. Password generation will fail.")

        # Check for exclusions
        if exclude_ambiguous:
            recommendations.append("Excluding ambiguous characters is good for usability, but slightly reduces character space.")
        if exclude_custom_chars:
            num_excluded = len(set(exclude_custom_chars))
            if num_excluded > 5: # If too many characters are excluded
                recommendations.append(f"Excluding {num_excluded} custom characters might reduce entropy. Use sparingly.")
            # Check if common crucial characters are excluded
            if 'a' in exclude_custom_chars.lower() or 'e' in exclude_custom_chars.lower():
                recommendations.append("Excluding common letters like 'a' or 'e' is unusual and could slightly reduce character space.")
            if '1' in exclude_custom_chars or '0' in exclude_custom_chars:
                 recommendations.append("Excluding common digits like '0' or '1' is unusual and could slightly reduce character space.")

    # Recommendation based on no_repeating_chars and charset size
    if not no_repeating_chars and effective_charset_size > 1 and effective_charset_size < 30:
        recommendations.append("For smaller character sets, consider enabling 'No immediate repeating characters' for added security.")
    elif no_repeating_chars and effective_charset_size < 2:
        recommendations.append("Cannot prevent repeating characters with a character set of less than 2 unique characters.")


    if not recommendations:
        return "Character set definition looks good!"
    else:
        return "Recommendations: " + " ".join(recommendations)

if __name__ == "__main__":
    print("--- Charset Analyzer Test Cases ---")
    print("Case 1 (Default):", analyze_charset_definition(True, True, True, True, False, ''))
    print("Case 2 (Only lowercase):", analyze_charset_definition(False, True, False, False, False, ''))
    print("Case 3 (Custom set 'abc123'):", analyze_charset_definition(False, False, False, False, False, '', 'abc123'))
    print("Case 4 (Exclude too many):", analyze_charset_definition(True, True, True, True, False, 'abcdefg'))
    print("Case 5 (Small charset, no repeating off):", analyze_charset_definition(False, True, False, False, False, '', custom_character_set='abc', no_repeating_chars=False))
    print("Case 6 (Small charset, no repeating on):", analyze_charset_definition(False, True, False, False, False, '', custom_character_set='ab', no_repeating_chars=True))
    print("Case 7 (Default, no repeating off):", analyze_charset_definition(True, True, True, True, False, '', no_repeating_chars=False))
