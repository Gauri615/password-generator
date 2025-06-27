// script.js
document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const copyBtn = document.getElementById('copyBtn');
    const generatedPasswordInput = document.getElementById('generatedPassword');
    const errorMessageDisplay = document.getElementById('errorMessage');

    // Generation Type Selection
    const typePasswordRadio = document.getElementById('typePassword');
    const typePassphraseRadio = document.getElementById('typePassphrase');
    const passwordOptionsDiv = document.getElementById('passwordOptions');
    const passphraseOptionsDiv = document.getElementById('passphraseOptions');

    // Password specific inputs
    const passwordLengthInput = document.getElementById('passwordLength');
    const includeUppercaseInput = document.getElementById('includeUppercase');
    const includeLowercaseInput = document.getElementById('includeLowercase');
    const includeDigitsInput = document.getElementById('includeDigits');
    const includeSymbolsInput = document.getElementById('includeSymbols');
    const excludeAmbiguousInput = document.getElementById('excludeAmbiguous');
    const excludeCustomCharsInput = document.getElementById('excludeCustomChars');
    const customCharacterSetInput = document.getElementById('customCharacterSet');

    // Passphrase specific inputs
    const numWordsInput = document.getElementById('numWords');
    const wordSeparatorInput = document.getElementById('wordSeparator');
    const passphraseIncludeDigitInput = document.getElementById('passphraseIncludeDigit');
    const passphraseIncludeSymbolInput = document.getElementById('passphraseIncludeSymbol');

    // Generate Another Button
    const generateAnotherBtn = document.getElementById('generateAnotherBtn');

    // Theme Toggle Element
    const darkModeToggle = document.getElementById('darkModeToggle');

    // Strength Indicator Elements
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    const charsetRecommendationText = document.getElementById('charsetRecommendationText'); // NEW: Element for charset recommendation

    // ALL inputs that can change generated output
    const allConfigInputs = document.querySelectorAll(
        '#passwordLength, #includeUppercase, #includeLowercase, #includeDigits, #includeSymbols, ' +
        '#excludeAmbiguous, #excludeCustomChars, #customCharacterSet, ' +
        '#numWords, #wordSeparator, #passphraseIncludeDigit, #passphraseIncludeSymbol'
    );

    const BACKEND_URL = 'http://127.0.0.1:5000/generate';

    // Function to toggle options display based on generation type (password/passphrase)
    function toggleOptionsDisplay() {
        if (typePasswordRadio.checked) {
            passwordOptionsDiv.classList.remove('hidden');
            passphraseOptionsDiv.classList.add('hidden');
        } else { // typePassphraseRadio.checked
            passwordOptionsDiv.classList.add('hidden');
            passphraseOptionsDiv.classList.remove('hidden');
        }
        predictStrengthAndCharsetFromBackend();
    }

    // Function to disable/enable standard include checkboxes based on customCharacterSet
    function toggleIncludeCheckboxes() {
        const isCustomCharsProvided = customCharacterSetInput.value.trim().length > 0;
        includeUppercaseInput.disabled = isCustomCharsProvided;
        includeLowercaseInput.disabled = isCustomCharsProvided;
        includeDigitsInput.disabled = isCustomCharsProvided;
        includeSymbolsInput.disabled = isCustomCharsProvided;

        if (isCustomCharsProvided) {
            includeUppercaseInput.checked = false;
            includeLowercaseInput.checked = false;
            includeDigitsInput.checked = false;
            includeSymbolsInput.checked = false;
        }
    }


    // NEW: Function to send current configuration to backend and get ALL AI predictions
    async function predictStrengthAndCharsetFromBackend() {
        errorMessageDisplay.textContent = ''; // Clear previous errors
        charsetRecommendationText.textContent = ''; // NEW: Clear previous recommendation

        let requestBody = {};
        let currentGenerationType = typePasswordRadio.checked ? 'password' : 'passphrase';
        requestBody.type = currentGenerationType;

        if (currentGenerationType === 'password') {
            const length = parseInt(passwordLengthInput.value);
            const customCharsToInclude = customCharacterSetInput.value.trim();
            const excludeAmbiguous = excludeAmbiguousInput.checked;
            const excludeCustomChars = excludeCustomCharsInput.value;

            // Basic client-side validation to avoid unnecessary backend calls
            if (length < 6 || length > 30) {
                strengthText.textContent = 'Invalid Length';
                strengthBar.style.width = '0%';
                strengthBar.className = 'strength-bar';
                return;
            }
             if (!customCharsToInclude && !(includeUppercaseInput.checked || includeLowercaseInput.checked || includeDigitsInput.checked || includeSymbolsInput.checked)) {
                strengthText.textContent = 'No Char Type Selected';
                strengthBar.style.width = '0%';
                strengthBar.className = 'strength-bar';
                return;
            }


            if (customCharsToInclude) {
                requestBody.custom_character_set = customCharsToInclude;
                requestBody.include_uppercase = false;
                requestBody.include_lowercase = false;
                requestBody.include_digits = false;
                requestBody.include_symbols = false;
            } else {
                requestBody.include_uppercase = includeUppercaseInput.checked;
                requestBody.include_lowercase = includeLowercaseInput.checked;
                requestBody.include_digits = includeDigitsInput.checked;
                requestBody.include_symbols = includeSymbolsInput.checked;
            }

            requestBody.length = length;
            requestBody.exclude_ambiguous = excludeAmbiguous;
            requestBody.exclude_custom_chars = excludeCustomChars;

        } else { // currentGenerationType === 'passphrase'
            const numWords = parseInt(numWordsInput.value);
            const separator = wordSeparatorInput.value;
            const includeDigit = passphraseIncludeDigitInput.checked;
            const includeSymbol = passphraseIncludeSymbolInput.checked;

            if (numWords < 2 || numWords > 10) {
                strengthText.textContent = 'Invalid Word Count';
                strengthBar.style.width = '0%';
                strengthBar.className = 'strength-bar';
                return;
            }

            requestBody.num_words = numWords;
            requestBody.separator = separator;
            requestBody.include_digit = includeDigit;
            requestBody.include_symbol = includeSymbol;
        }

        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (response.ok && data.ai_strength_score !== undefined) {
                const aiScore = data.ai_strength_score;
                strengthBar.className = 'strength-bar';
                strengthBar.classList.add(`score-${aiScore}`);
                strengthBar.style.width = ((aiScore + 1) / 5) * 100 + '%';

                const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
                strengthText.className = 'strength-text';
                strengthText.classList.add(`score-${aiScore}`);
                strengthText.textContent = `AI Prediction: ${strengthLabels[aiScore]}`;

                // NEW: Display charset recommendation
                if (data.charset_recommendation) {
                    charsetRecommendationText.textContent = data.charset_recommendation;
                    charsetRecommendationText.style.color = data.charset_recommendation.includes("Good") ? 'green' : 'orange'; // Basic coloring
                }
            } else {
                strengthText.textContent = 'Could not get AI strength.';
                strengthBar.style.width = '0%';
                strengthBar.className = 'strength-bar';
                errorMessageDisplay.textContent = data.error || 'Failed to get AI strength prediction.';
                charsetRecommendationText.textContent = ''; // Clear if error
            }
        } catch (error) {
            strengthText.textContent = 'Backend Error';
            strengthBar.style.width = '0%';
            strengthBar.className = 'strength-bar';
            errorMessageDisplay.textContent = 'Error connecting to the backend for strength prediction.';
            charsetRecommendationText.textContent = ''; // Clear if error
            console.error('Fetch error for strength prediction:', error);
        }
    }


    // Attach event listeners to all relevant inputs to update strength dynamically
    allConfigInputs.forEach(input => {
        input.addEventListener('input', predictStrengthAndCharsetFromBackend);
        input.addEventListener('change', predictStrengthAndCharsetFromBackend);
    });

    // Event listeners for generation type radio buttons
    typePasswordRadio.addEventListener('change', toggleOptionsDisplay);
    typePassphraseRadio.addEventListener('change', toggleOptionsDisplay);
    customCharacterSetInput.addEventListener('input', toggleIncludeCheckboxes); // NEW: Listen for custom character set changes


    // Initial setup calls on page load
    toggleOptionsDisplay();
    toggleIncludeCheckboxes();


    // Theme Toggle Logic
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener('change', () => {
        if (darkModeToggle.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });


    // Main Generate Button Listener (remains largely the same)
    generateBtn.addEventListener('click', async () => {
        errorMessageDisplay.textContent = '';

        let requestBody = {};
        let currentGenerationType = typePasswordRadio.checked ? 'password' : 'passphrase';
        requestBody.type = currentGenerationType;

        if (currentGenerationType === 'password') {
            const length = parseInt(passwordLengthInput.value);
            const customCharsToInclude = customCharacterSetInput.value.trim();
            const excludeAmbiguous = excludeAmbiguousInput.checked;
            const excludeCustomChars = excludeCustomCharsInput.value;

            if (length < 6 || length > 30) {
                errorMessageDisplay.textContent = 'Password length must be between 6 and 30 characters.';
                return;
            }
            if (!customCharsToInclude && !(includeUppercaseInput.checked || includeLowercaseInput.checked || includeDigitsInput.checked || includeSymbolsInput.checked)) {
                errorMessageDisplay.textContent = 'At least one character type must be selected (or provide custom characters).';
                return;
            }


            if (customCharsToInclude) {
                requestBody.custom_character_set = customCharsToInclude;
                requestBody.include_uppercase = false;
                requestBody.include_lowercase = false;
                requestBody.include_digits = false;
                requestBody.include_symbols = false;
            } else {
                requestBody.include_uppercase = includeUppercaseInput.checked;
                requestBody.include_lowercase = includeLowercaseInput.checked;
                requestBody.include_digits = includeDigitsInput.checked;
                requestBody.include_symbols = includeSymbolsInput.checked;
            }

            requestBody.length = length;
            requestBody.exclude_ambiguous = excludeAmbiguous;
            requestBody.exclude_custom_chars = excludeCustomChars;

        } else { // currentGenerationType === 'passphrase'
            const numWords = parseInt(numWordsInput.value);
            const separator = wordSeparatorInput.value;
            const includeDigit = passphraseIncludeDigitInput.checked;
            const includeSymbol = passphraseIncludeSymbolInput.checked;

            if (numWords < 2 || numWords > 10) {
                errorMessageDisplay.textContent = 'Number of words must be between 2 and 10.';
                return;
            }

            requestBody.num_words = numWords;
            requestBody.separator = separator;
            requestBody.include_digit = includeDigit;
            requestBody.include_symbol = includeSymbol;
        }

        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (response.ok) {
                generatedPasswordInput.value = data.password;
            } else {
                errorMessageDisplay.textContent = data.error || 'Failed to generate password.';
                generatedPasswordInput.value = '';
            }
        } catch (error) {
            errorMessageDisplay.textContent = 'Error connecting to the backend. Is the Flask server running?';
            console.error('Fetch error:', error);
            generatedPasswordInput.value = '';
        }
    });

    // Generate Another Button Listener - triggers the main generate button's click event
    generateAnotherBtn.addEventListener('click', () => {
        generateBtn.click();
    });


    // Enhanced Clipboard Integration
    copyBtn.addEventListener('click', () => {
        generatedPasswordInput.select();
        generatedPasswordInput.setSelectionRange(0, 99999);
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(generatedPasswordInput.value).then(() => {
                showCopiedFeedback();
            }).catch(err => {
                console.error('Failed to copy text using clipboard API: ', err);
                document.execCommand('copy');
                showCopiedFeedback();
            });
        } else {
            document.execCommand('copy');
            showCopiedFeedback();
        }
    });

    function showCopiedFeedback() {
        const originalButtonText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.classList.add('copied');

        setTimeout(() => {
            copyBtn.textContent = originalButtonText;
            copyBtn.classList.remove('copied');
        }, 1500);
    }
});