# password_generator.py
import random
import string

# Function to load wordlist
def load_wordlist(filepath="eff_long_wordlist.txt"):
    try:
        with open(filepath, 'r') as f:
            words = [line.strip() for line in f if line.strip()]
        if not words:
            raise ValueError(f"Wordlist file '{filepath}' is empty or could not be read.")
        return words
    except FileNotFoundError:
        # Create a dummy wordlist if not found for demonstration purposes
        print(f"Warning: Wordlist file not found at: {filepath}. Using a dummy wordlist for passphrases.")
        return ["apple", "banana", "cherry", "date", "elephant", "flower", "garden", "happiness"]
    except Exception as e:
        raise IOError(f"Error loading wordlist: {e}")

# Load wordlist globally once
try:
    WORDLIST = load_wordlist()
except (FileNotFoundError, ValueError, IOError) as e:
    print(f"Warning: Could not load wordlist for passphrase generation. Passphrase option might not work: {e}")
    WORDLIST = []


def generate_password(length=12, include_uppercase=True, include_lowercase=True,
                      include_digits=True, include_symbols=True,
                      exclude_ambiguous=False, exclude_custom_chars='', # existing
                      custom_character_set=''): # NEW: Add custom_character_set
    characters = ""

    # NEW: Prioritize custom_character_set if provided
    if custom_character_set:
        characters = custom_character_set
    else:
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_digits:
            characters += string.digits
        if include_symbols:
            characters += string.punctuation # string.punctuation includes most common symbols

    if not characters:
        raise ValueError("No character types selected for password generation or custom character set is empty.")

    # Apply exclusions
    if exclude_ambiguous:
        ambiguous_chars = 'l1IO0'
        characters = ''.join([char for char in characters if char not in ambiguous_chars])

    if exclude_custom_chars:
        # Create a set for faster lookup of excluded characters
        exclude_set = set(exclude_custom_chars)
        characters = ''.join([char for char in characters if char not in exclude_set])

    if not characters:
        raise ValueError("All possible characters were excluded. Cannot generate password.")

    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_passphrase(num_words=4, separator='-', include_digit=True, include_symbol=True):
    if not WORDLIST:
        raise FileNotFoundError("Wordlist is not loaded. Cannot generate passphrase.")
    if num_words <= 0:
        raise ValueError("Number of words must be positive.")

    passphrase_words = random.sample(WORDLIST, num_words) # sample ensures unique words

    passphrase_parts = passphrase_words[:]

    if include_digit:
        digit = str(random.randint(0, 9))
        insert_pos = random.randint(0, len(passphrase_parts))
        if insert_pos == len(passphrase_parts):
            passphrase_parts.append(digit)
        else:
            passphrase_parts.insert(insert_pos, digit)

    if include_symbol:
        # Common symbols that are generally safe and readable
        symbols = '!@#$%^&*()_+-='
        symbol = random.choice(symbols)
        insert_pos = random.randint(0, len(passphrase_parts))
        if insert_pos == len(passphrase_parts):
            passphrase_parts.append(symbol)
        else:
            passphrase_parts.insert(insert_pos, symbol)

    passphrase = separator.join(passphrase_parts)
    return passphrase

if __name__ == "__main__":
    print("--- Character Passwords ---")
    print("Generated Password (ambiguous excluded):", generate_password(exclude_ambiguous=True))
    print("Generated Password (custom excluded: 'abc'):", generate_password(exclude_custom_chars='abc'))
    print("Generated Password (ambiguous & custom excluded: 'l0!'):", generate_password(exclude_ambiguous=True, exclude_custom_chars='l0!'))
    print("Generated Password (16 chars, no symbols, ambiguous excluded):", generate_password(length=16, include_symbols=False, exclude_ambiguous=True))
    print("Generated Password (8 chars, only lowercase and digits, ambiguous excluded):", generate_password(length=8, include_uppercase=False, include_symbols=False, exclude_ambiguous=True))
    print("Generated Password (10 chars, custom set 'abcABC123'):", generate_password(length=10, custom_character_set='abcABC123'))


    print("\n--- Passphrases ---")
    if WORDLIST:
        print("Generated Passphrase (4 words):", generate_passphrase())
        print("Generated Passphrase (5 words, space sep):", generate_passphrase(num_words=5, separator=' '))
        print("Generated Passphrase (3 words, no digit, no symbol):", generate_passphrase(num_words=3, include_digit=False, include_symbol=False))
    else:
        print("Wordlist not available, cannot generate passphrases.")