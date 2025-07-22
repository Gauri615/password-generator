# password_generator.py
import random
import string

# Global variable to store loaded wordlists to avoid re-loading
_WORDLISTS = {}


# Function to load wordlist
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
            f"Warning: Wordlist file not found at: {filepath}. Using a dummy wordlist."
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
        raise IOError(f"Error loading wordlist: {e}")


# Load default wordlist globally once (if not already loaded by a specific request)
try:
    if "eff_long_wordlist.txt" not in _WORDLISTS:
        _WORDLISTS["eff_long_wordlist.txt"] = load_wordlist(
            "eff_long_wordlist.txt")
except (FileNotFoundError, ValueError, IOError) as e:
    print(
        f"Initial warning: Could not load default wordlist for passphrase generation. Passphrase option might use dummy data: {e}"
    )

# Expanded ambiguous characters list
AMBIGUOUS_CHARS = 'Il1Lo0O|[]{}()/\'"`~,.;:<> '


def generate_password(length=12,
                      include_uppercase=True,
                      include_lowercase=True,
                      include_digits=True,
                      include_symbols=True,
                      exclude_ambiguous=False,
                      exclude_custom_chars='',
                      custom_character_set='',
                      require_min_char_types=False,
                      no_repeating_chars=False):

    characters = ""
    if custom_character_set:
        characters = custom_character_set
    else:
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_digits:
            characters += string.digits
        if include_symbols:
            characters += string.punctuation

    if not characters:
        raise ValueError(
            "No character types selected for password generation.")

    # Apply exclusions
    if exclude_ambiguous:
        for char in AMBIGUOUS_CHARS:
            characters = characters.replace(char, '')
    if exclude_custom_chars:
        for char in exclude_custom_chars:
            characters = characters.replace(char, '')

    if not characters:
        raise ValueError(
            "Character set became empty after exclusions. Please adjust your criteria."
        )

    password_list = []
    required_chars = []  # To hold at least one of each required type

    # Implement require_min_char_types logic
    if require_min_char_types and not custom_character_set:
        if include_uppercase:
            required_chars.append(random.choice(string.ascii_uppercase))
        if include_lowercase:
            required_chars.append(random.choice(string.ascii_lowercase))
        if include_digits:
            required_chars.append(random.choice(string.digits))
        if include_symbols:
            required_chars.append(random.choice(string.punctuation))

        # Ensure password length is sufficient for required chars
        if length < len(required_chars):
            raise ValueError(
                "Password length is too short to include at least one of each selected character type."
            )

        # Add required characters to the password list and shuffle them
        password_list.extend(required_chars)
        random.shuffle(password_list)  # Shuffle to randomize positions

    last_char = ''  # For no_repeating_chars logic

    # Fill the rest of the password length
    while len(password_list) < length:
        char = random.choice(characters)
        # Implement no_repeating_chars logic
        if no_repeating_chars:
            attempts = 0
            while char == last_char and len(characters) > 1 and attempts < 10:
                char = random.choice(characters)
                attempts += 1

        password_list.append(char)
        last_char = char

    password = "".join(password_list[:length])

    if require_min_char_types:
        password = "".join(random.sample(password, len(password)))

    return password


def generate_passphrase(
    num_words=4,
    separator='-',
    include_digit=True,
    include_symbol=True,
    wordlist_name="eff_long_wordlist.txt",  # Existing
    capitalization="none",  # NEW: Capitalization option (none, first, all, random)
    placement="random"):  # NEW: Placement option (random, start, end)

    WORDLIST = load_wordlist(wordlist_name)

    if not WORDLIST:
        raise ValueError("Wordlist not loaded. Cannot generate passphrase.")
    if num_words <= 0:
        raise ValueError("Number of words must be positive.")

    passphrase_parts = [random.choice(WORDLIST) for _ in range(num_words)]

    # NEW: Apply capitalization rules
    processed_words = []
    for word in passphrase_parts:
        if capitalization == "first":
            processed_words.append(word.capitalize())
        elif capitalization == "all":
            processed_words.append(word.upper())
        elif capitalization == "random":
            # Randomly capitalize first letter or keep as is
            if random.choice([True, False]):
                processed_words.append(word.capitalize())
            else:
                processed_words.append(
                    word.lower())  # Ensure lowercase if not capitalized
        else:  # "none" or any other value
            processed_words.append(
                word.lower())  # Ensure all lowercase by default

    passphrase_elements = list(
        processed_words)  # Convert to list for mutable operations

    # NEW: Handle digit and symbol insertion based on placement
    digit_to_insert = str(random.randint(0, 9)) if include_digit else None
    symbol_to_insert = random.choice(
        '!@#$%^&*()-_=+') if include_symbol else None

    # Determine insertion positions
    digit_pos = -1
    symbol_pos = -1

    if placement == "start":
        if digit_to_insert:
            passphrase_elements.insert(0, digit_to_insert)
            digit_pos = 0
        if symbol_to_insert:
            # If digit was inserted at start, symbol goes after it
            passphrase_elements.insert(1 if digit_to_insert else 0,
                                       symbol_to_insert)
            symbol_pos = 1 if digit_to_insert else 0
    elif placement == "end":
        if symbol_to_insert:  # Symbol first, so digit can go before it if both exist
            passphrase_elements.append(symbol_to_insert)
            symbol_pos = len(passphrase_elements) - 1
        if digit_to_insert:
            passphrase_elements.append(digit_to_insert)
            digit_pos = len(passphrase_elements) - 1
    else:  # "random"
        if digit_to_insert:
            # Insert digit at a random position within the current elements
            insert_pos = random.randint(0, len(passphrase_elements))
            passphrase_elements.insert(insert_pos, digit_to_insert)
            digit_pos = insert_pos

        if symbol_to_insert:
            # Insert symbol at a random position, avoiding the digit's position if possible
            # and ensuring it's within the new bounds
            attempts = 0
            while attempts < 10:  # Try a few times to get a different spot
                insert_pos = random.randint(0, len(passphrase_elements))
                if insert_pos != digit_pos or not digit_to_insert:  # If not same as digit, or no digit
                    passphrase_elements.insert(insert_pos, symbol_to_insert)
                    symbol_pos = insert_pos
                    break
                attempts += 1
            if attempts == 10:  # If couldn't find a different spot after attempts, just insert
                passphrase_elements.insert(
                    random.randint(0, len(passphrase_elements)),
                    symbol_to_insert)

    passphrase = separator.join(passphrase_elements)
    return passphrase


if __name__ == "__main__":
    print("--- Character Passwords (Advanced Features) ---")
    print("Length 12, all types, no repeating:",
          generate_password(length=12, no_repeating_chars=True))
    print("Length 12, all types, min char types:",
          generate_password(length=12, require_min_char_types=True))
    print(
        "Length 16, all types, no repeating, min char types:",
        generate_password(length=16,
                          no_repeating_chars=True,
                          require_min_char_types=True))
    print(
        "Length 10, custom set 'abcABC123', no repeating:",
        generate_password(length=10,
                          custom_character_set='abcABC123',
                          no_repeating_chars=True))
    print("Length 12, all types, ambiguous excluded:",
          generate_password(exclude_ambiguous=True))
    print(
        "Length 8, lower only:",
        generate_password(length=8,
                          include_uppercase=False,
                          include_digits=False,
                          include_symbols=False))

    print("\n--- Passphrases (Wordlist, Capitalization, Placement) ---")
    print(
        "4 words, long wordlist, none cap, random placement:",
        generate_passphrase(num_words=4,
                            wordlist_name="eff_long_wordlist.txt",
                            capitalization="none",
                            placement="random"))
    print(
        "5 words, short wordlist, first cap, start placement:",
        generate_passphrase(num_words=5,
                            include_digit=True,
                            include_symbol=True,
                            wordlist_name="eff_short_wordlist.txt",
                            capitalization="first",
                            placement="start"))
    print(
        "6 words, long wordlist, all cap, end placement:",
        generate_passphrase(num_words=6,
                            include_digit=True,
                            wordlist_name="eff_long_wordlist.txt",
                            capitalization="all",
                            placement="end"))
    print(
        "7 words, short wordlist, random cap, random placement:",
        generate_passphrase(num_words=7,
                            include_symbol=True,
                            wordlist_name="eff_short_wordlist.txt",
                            capitalization="random",
                            placement="random"))
    print(
        "3 words, custom separator '_', long wordlist, none cap:",
        generate_passphrase(num_words=3,
                            separator='_',
                            wordlist_name="eff_long_wordlist.txt",
                            capitalization="none"))
    print(
        "4 words, short wordlist, all cap, start, digit+symbol:",
        generate_passphrase(num_words=4,
                            include_digit=True,
                            include_symbol=True,
                            wordlist_name="eff_short_wordlist.txt",
                            capitalization="all",
                            placement="start"))
