# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from password_generator import generate_password, generate_passphrase  # load_wordlist is now handled internally by password_generator
from ai_strength_model import predict_strength
from ai_charset_analyzer import analyze_charset_definition
import os

app = Flask(__name__)
CORS(app)

# Define the directory where your static files (HTML, CSS, JS) are located
STATIC_DIR = os.path.abspath(os.path.dirname(__file__))


# Route to serve the main HTML file
@app.route('/')
def serve_index():
    return send_from_directory(STATIC_DIR, 'index.html')


# Route to serve static files like CSS and JS
@app.route('/<path:filename>')
def serve_static(filename):
    # Prevent serving app.py or other sensitive files
    if filename in [
            'app.py', 'password_generator.py', 'ai_strength_model.py',
            'ai_charset_analyzer.py', 'eff_long_wordlist.txt',
            'eff_short_wordlist.txt', '.replit', 'pyproject.toml'
    ]:
        return "Access Denied", 403
    return send_from_directory(STATIC_DIR, filename)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        generation_type = data.get('type', 'password')

        ai_strength_score = 0
        charset_recommendation = ""

        if generation_type == 'password':
            length = data.get('length', 12)
            include_uppercase = data.get('include_uppercase', True)
            include_lowercase = data.get('include_lowercase', True)
            include_digits = data.get('include_digits', True)
            include_symbols = data.get('include_symbols', True)
            exclude_ambiguous = data.get('exclude_ambiguous', False)
            exclude_custom_chars = data.get('exclude_custom_chars', '')
            custom_character_set = data.get('custom_character_set', '')
            require_min_char_types = data.get('require_min_char_types', False)
            no_repeating_chars = data.get('no_repeating_chars', False)

            # Client-side validation for password generation
            if length < 6 or length > 30:
                raise ValueError(
                    'Password length must be between 6 and 30 characters.')

            # Check if any character type is selected if no custom set
            if not custom_character_set and not (
                    include_uppercase or include_lowercase or include_digits
                    or include_symbols):
                raise ValueError(
                    'At least one character type must be selected if no custom character set is provided.'
                )

            password = generate_password(
                length=length,
                include_uppercase=include_uppercase,
                include_lowercase=include_lowercase,
                include_digits=include_digits,
                include_symbols=include_symbols,
                exclude_ambiguous=exclude_ambiguous,
                exclude_custom_chars=exclude_custom_chars,
                custom_character_set=custom_character_set,
                require_min_char_types=require_min_char_types,
                no_repeating_chars=no_repeating_chars)

            # Predict strength using our simple AI model
            ai_strength_score = predict_strength(
                length=length,
                include_uppercase=include_uppercase,
                include_lowercase=include_lowercase,
                include_digits=include_digits,
                include_symbols=include_symbols,
                exclude_ambiguous=exclude_ambiguous,
                exclude_custom_chars=exclude_custom_chars,
                custom_character_set=custom_character_set,
                is_passphrase=False,
                require_min_char_types=
                require_min_char_types,  # Pass to AI for better prediction
                no_repeating_chars=
                no_repeating_chars  # Pass to AI for better prediction
            )

            # Analyze character set definition using our new AI system
            charset_recommendation = analyze_charset_definition(
                include_uppercase=include_uppercase,
                include_lowercase=include_lowercase,
                include_digits=include_digits,
                include_symbols=include_symbols,
                exclude_ambiguous=exclude_ambiguous,
                exclude_custom_chars=exclude_custom_chars,
                custom_character_set=custom_character_set,
                no_repeating_chars=
                no_repeating_chars  # Pass to AI for better prediction
            )

            return jsonify({
                'password': password,
                'ai_strength_score': ai_strength_score,
                'charset_recommendation': charset_recommendation
            })

        elif generation_type == 'passphrase':
            num_words = data.get('num_words', 4)
            separator = data.get('separator', '-')
            include_digit = data.get('include_digit', True)
            include_symbol = data.get('include_symbol', True)
            wordlist_name = data.get('wordlist_name', 'eff_long_wordlist.txt')
            # NEW: Get capitalization and placement from frontend
            capitalization = data.get('capitalization', 'none')
            placement = data.get('placement', 'random')

            # Client-side validation for passphrase generation
            if num_words < 2 or num_words > 10:
                raise ValueError('Number of words must be between 2 and 10.')

            passphrase = generate_passphrase(
                num_words=num_words,
                separator=separator,
                include_digit=include_digit,
                include_symbol=include_symbol,
                wordlist_name=wordlist_name,
                capitalization=capitalization,  # NEW: Pass to generator
                placement=placement  # NEW: Pass to generator
            )

            # Predict strength for passphrase using our simple AI model
            ai_strength_score = predict_strength(
                length=0,
                include_uppercase=False,
                include_lowercase=False,
                include_digits=include_digit,
                include_symbols=include_symbol,
                exclude_ambiguous=False,
                exclude_custom_chars='',
                is_passphrase=True,
                num_words=num_words,
                wordlist_name=wordlist_name  # Pass to AI for better prediction
            )

            # For passphrase, a simpler recommendation
            if not include_digit and not include_symbol and num_words < 5:
                charset_recommendation = "Consider adding digits/symbols or more words for a stronger passphrase."
            else:
                charset_recommendation = "Passphrase configuration looks good!"

            return jsonify({
                'password': passphrase,
                'ai_strength_score': ai_strength_score,
                'charset_recommendation': charset_recommendation
            })

        else:
            return jsonify({'error':
                            'Invalid generation type specified.'}), 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'error': 'Backend error: ' + str(e)}), 500
    except Exception as e:
        return jsonify({'error':
                        'An unexpected error occurred: ' + str(e)}), 500


# IMPORTANT: Ensure Flask runs on port 8080 for Replit deployment
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
