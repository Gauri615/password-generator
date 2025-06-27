# ai_charset_analyzer.py

def analyze_charset_definition(
    include_uppercase: bool,
    include_lowercase: bool,
    include_digits: bool,
    include_symbols: bool,
    exclude_ambiguous: bool,
    exclude_custom_chars: str,
    custom_character_set: str = ''
) -> str:
    """
    A simplified "AI" function to analyze the user's character set definition.
    Provides a recommendation/warning based on common security practices.
    """
    recommendations = []

    if custom_character_set:
        # Analyze custom character set
        unique_chars_in_custom_set = len(set(custom_character_set))
        if unique_chars_in_custom_set < 20:
            recommendations.append("Consider a larger custom character set for better entropy.")
        if any(char.isspace() for char in custom_character_set):
            recommendations.append("Avoid spaces in custom character set as they can be problematic.")
        if len(set(custom_character_set.lower())) == 1 and unique_chars_in_custom_set > 1:
            recommendations.append("Custom set contains only one type of character (e.g., 'aaaaa' or '11111'). Diversify!")

    else:
        # Analyze standard character type selections
        selected_types_count = 0
        if include_uppercase: selected_types_count += 1
        if include_lowercase: selected_types_count += 1
        if include_digits: selected_types_count += 1
        if include_symbols: selected_types_count += 1

        if selected_types_count < 3:
            recommendations.append("For stronger passwords, include at least 3-4 character types (uppercase, lowercase, digits, symbols).")
        if not include_digits and not include_symbols:
            recommendations.append("Adding digits and symbols significantly increases password strength.")
        if not include_uppercase and not include_lowercase:
            recommendations.append("Include both uppercase and lowercase letters for higher entropy.")


    # Analyze exclusions
    if exclude_ambiguous:
        pass # This is often a good practice, so no negative recommendation here
    
    if exclude_custom_chars:
        # Count number of excluded characters that significantly reduce the character set
        # This is a very rough heuristic
        num_excluded = len(set(exclude_custom_chars))
        if num_excluded > 5: # If too many characters are excluded
            recommendations.append(f"Excluding {num_excluded} custom characters might reduce entropy. Use sparingly.")
        # Check if common crucial characters are excluded
        if 'a' in exclude_custom_chars.lower() or 'e' in exclude_custom_chars.lower():
            recommendations.append("Excluding common letters like 'a' or 'e' is unusual and could slightly reduce character space.")
        if '1' in exclude_custom_chars or '0' in exclude_custom_chars:
             recommendations.append("Excluding common digits like '0' or '1' is unusual and could slightly reduce character space.")


    if not recommendations:
        return "Character set definition looks good!"
    else:
        # Join recommendations into a single string
        return "Recommendations: " + " ".join(recommendations)

if __name__ == "__main__":
    print("--- Charset Analyzer Test Cases ---")
    print("Case 1 (Default):", analyze_charset_definition(True, True, True, True, False, ''))
    print("Case 2 (Only lowercase):", analyze_charset_definition(False, True, False, False, False, ''))
    print("Case 3 (Custom set 'abc123'):", analyze_charset_definition(False, False, False, False, False, '', 'abc123'))
    print("Case 4 (Exclude too many):", analyze_charset_definition(True, True, True, True, False, 'abcdefg'))
    print("Case 5 (No digits/symbols):", analyze_charset_definition(True, True, False, False, False, ''))