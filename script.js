// script.js
document.addEventListener("DOMContentLoaded", () => {
    const generateBtn = document.getElementById("generateBtn");
    const copyBtn = document.getElementById("copyBtn");
    const generatedPasswordInput = document.getElementById("generatedPassword");
    const errorMessageDisplay = document.getElementById("errorMessage");

    // Generation Type Selection
    const typePasswordRadio = document.getElementById("typePassword");
    const typePassphraseRadio = document.getElementById("typePassphrase");
    const passwordOptionsDiv = document.getElementById("passwordOptions");
    const passphraseOptionsDiv = document.getElementById("passphraseOptions");

    // Password specific inputs
    const passwordLengthInput = document.getElementById("passwordLength");
    const includeUppercaseInput = document.getElementById("includeUppercase");
    const includeLowercaseInput = document.getElementById("includeLowercase");
    const includeDigitsInput = document.getElementById("includeDigits");
    const includeSymbolsInput = document.getElementById("includeSymbols");
    const excludeAmbiguousInput = document.getElementById("excludeAmbiguous");
    const excludeCustomCharsInput =
        document.getElementById("excludeCustomChars");
    const customCharacterSetInput =
        document.getElementById("customCharacterSet");

    // Password Advanced Options
    const requireMinCharTypesInput = document.getElementById(
        "requireMinCharTypes",
    );
    const noRepeatingCharsInput = document.getElementById("noRepeatingChars");

    // Passphrase specific inputs
    const numWordsInput = document.getElementById("numWords");
    const wordSeparatorInput = document.getElementById("wordSeparator");
    const passphraseIncludeDigitInput = document.getElementById(
        "passphraseIncludeDigit",
    );
    const passphraseIncludeSymbolInput = document.getElementById(
        "passphraseIncludeSymbol",
    );

    // Passphrase Advanced Options
    const wordlistSelect = document.getElementById("wordlistSelect");
    // NEW: Passphrase Capitalization and Placement
    const passphraseCapitalizationRadios = document.querySelectorAll(
        'input[name="passphraseCapitalization"]',
    );
    const placementSelect = document.getElementById("placementSelect");

    // Generate Another Button
    const generateAnotherBtn = document.getElementById("generateAnotherBtn");

    // Theme Toggle Element
    const darkModeToggle = document.getElementById("darkModeToggle");

    // Strength Indicator Elements
    const strengthBar = document.getElementById("strengthBar");
    const strengthText = document.getElementById("strengthText");
    const charsetRecommendationText = document.getElementById(
        "charsetRecommendationText",
    );

    // NEW UI Elements
    const loadingIndicator = document.getElementById("loadingIndicator");
    const passwordHistoryList = document.getElementById("passwordHistoryList");

    // ALL inputs that can change generated output
    const allConfigInputs = document.querySelectorAll(
        "#passwordLength, #includeUppercase, #includeLowercase, #includeDigits, #includeSymbols, " +
            "#excludeAmbiguous, #excludeCustomChars, #customCharacterSet, " +
            "#requireMinCharTypes, #noRepeatingChars, " +
            "#numWords, #wordSeparator, #passphraseIncludeDigit, #passphraseIncludeSymbol, " +
            "#wordlistSelect, " +
            'input[name="passphraseCapitalization"], #placementSelect', // NEW: Add new passphrase inputs
    );

    const BACKEND_URL = "https://my-password-generator-api.onrender.com/generate";

    // Function to toggle options display based on generation type (password/passphrase)
    function toggleOptionsDisplay() {
        if (typePasswordRadio.checked) {
            passwordOptionsDiv.classList.remove("hidden");
            passphraseOptionsDiv.classList.add("hidden");
        } else {
            // typePassphraseRadio.checked
            passwordOptionsDiv.classList.add("hidden");
            passphraseOptionsDiv.classList.remove("hidden");
        }
        predictStrengthAndCharsetFromBackend();
    }

    // Function to disable/enable standard include checkboxes based on customCharacterSet
    function toggleIncludeCheckboxes() {
        const isCustomCharsProvided =
            customCharacterSetInput.value.trim().length > 0;
        includeUppercaseInput.disabled = isCustomCharsProvided;
        includeLowercaseInput.disabled = isCustomCharsProvided;
        includeDigitsInput.disabled = isCustomCharsProvided;
        includeSymbolsInput.disabled = isCustomCharsProvided;
        requireMinCharTypesInput.disabled = isCustomCharsProvided;

        if (isCustomCharsProvided) {
            includeUppercaseInput.checked = false;
            includeLowercaseInput.checked = false;
            includeDigitsInput.checked = false;
            includeSymbolsInput.checked = false;
            requireMinCharTypesInput.checked = false;
        }
    }

    // Function to show/hide loading indicator
    function showLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.classList.remove("hidden");
            generateBtn.disabled = true;
            generateAnotherBtn.disabled = true;
        } else {
            loadingIndicator.classList.add("hidden");
            generateBtn.disabled = false;
            generateAnotherBtn.disabled = false;
        }
    }

    // Function to display error messages more clearly
    function displayError(message) {
        errorMessageDisplay.textContent = message;
        errorMessageDisplay.classList.remove("hidden");
        setTimeout(() => {
            errorMessageDisplay.classList.add("hidden");
        }, 5000);
    }

    // Function to add password to history
    function addPasswordToHistory(password) {
        let history = JSON.parse(localStorage.getItem("passwordHistory")) || [];
        history.unshift(password);
        if (history.length > 5) {
            history = history.slice(0, 5);
        }
        localStorage.setItem("passwordHistory", JSON.stringify(history));
        renderPasswordHistory();
    }

    // Function to render password history from localStorage
    function renderPasswordHistory() {
        const history =
            JSON.parse(localStorage.getItem("passwordHistory")) || [];
        passwordHistoryList.innerHTML = "";

        if (history.length === 0) {
            const li = document.createElement("li");
            li.textContent = "No history yet.";
            li.classList.add("history-placeholder");
            passwordHistoryList.appendChild(li);
            return;
        }

        history.forEach((password) => {
            const li = document.createElement("li");
            li.classList.add("history-item");

            const passwordText = document.createElement("span");
            passwordText.textContent = password;
            passwordText.classList.add("history-password-text");

            const copyHistoryBtn = document.createElement("button");
            copyHistoryBtn.textContent = "Copy";
            copyHistoryBtn.classList.add("copy-history-btn");
            copyHistoryBtn.addEventListener("click", () => {
                copyToClipboard(password, copyHistoryBtn);
            });

            li.appendChild(passwordText);
            li.appendChild(copyHistoryBtn);
            passwordHistoryList.appendChild(li);
        });
    }

    // Generic copy to clipboard function with feedback
    function copyToClipboard(text, buttonElement) {
        generatedPasswordInput.value = text;
        generatedPasswordInput.select();
        generatedPasswordInput.setSelectionRange(0, 99999);

        let copiedSuccessfully = false;
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard
                .writeText(text)
                .then(() => {
                    copiedSuccessfully = true;
                    showCopiedFeedback(buttonElement);
                })
                .catch((err) => {
                    console.error(
                        "Failed to copy text using clipboard API: ",
                        err,
                    );
                    try {
                        document.execCommand("copy");
                        copiedSuccessfully = true;
                        showCopiedFeedback(buttonElement);
                    } catch (execErr) {
                        console.error(
                            "Failed to copy text using execCommand: ",
                            execErr,
                        );
                        displayError("Failed to copy password to clipboard.");
                    }
                });
        } else {
            try {
                document.execCommand("copy");
                copiedSuccessfully = true;
                showCopiedFeedback(buttonElement);
            } catch (execErr) {
                console.error(
                    "Failed to copy text using execCommand: ",
                    execErr,
                );
                displayError("Failed to copy password to clipboard.");
            }
        }
        if (buttonElement !== copyBtn) {
            generatedPasswordInput.value = "";
        }
    }

    function showCopiedFeedback(buttonElement) {
        const originalButtonText = buttonElement.textContent;
        buttonElement.textContent = "Copied!";
        buttonElement.classList.add("copied");

        setTimeout(() => {
            buttonElement.textContent = originalButtonText;
            buttonElement.classList.remove("copied");
        }, 1500);
    }

    // Function to send current configuration to backend and get ALL AI predictions
    async function predictStrengthAndCharsetFromBackend() {
        errorMessageDisplay.textContent = "";
        charsetRecommendationText.textContent = "";

        let requestBody = {};
        let currentGenerationType = typePasswordRadio.checked
            ? "password"
            : "passphrase";
        requestBody.type = currentGenerationType;

        if (currentGenerationType === "password") {
            const length = parseInt(passwordLengthInput.value);
            const customCharsToInclude = customCharacterSetInput.value.trim();
            const excludeAmbiguous = excludeAmbiguousInput.checked;
            const excludeCustomChars = excludeCustomCharsInput.value;
            const requireMinCharTypes = requireMinCharTypesInput.checked;
            const noRepeatingChars = noRepeatingCharsInput.checked;

            if (isNaN(length) || length < 6 || length > 30) {
                strengthText.textContent = "Invalid Length (6-30)";
                strengthBar.style.width = "0%";
                strengthBar.className = "strength-bar";
                return;
            }
            if (
                !customCharsToInclude &&
                !(
                    includeUppercaseInput.checked ||
                    includeLowercaseInput.checked ||
                    includeDigitsInput.checked ||
                    includeSymbolsInput.checked
                )
            ) {
                strengthText.textContent = "Select Char Types";
                strengthBar.style.width = "0%";
                strengthBar.className = "strength-bar";
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
            requestBody.require_min_char_types = requireMinCharTypes;
            requestBody.no_repeating_chars = noRepeatingChars;
        } else {
            // currentGenerationType === 'passphrase'
            const numWords = parseInt(numWordsInput.value);
            const separator = wordSeparatorInput.value;
            const includeDigit = passphraseIncludeDigitInput.checked;
            const includeSymbol = passphraseIncludeSymbolInput.checked;
            const selectedWordlist = wordlistSelect.value;
            // NEW: Get selected capitalization and placement
            const capitalization = document.querySelector(
                'input[name="passphraseCapitalization"]:checked',
            ).value;
            const placement = placementSelect.value;

            if (isNaN(numWords) || numWords < 2 || numWords > 10) {
                strengthText.textContent = "Invalid Word Count (2-10)";
                strengthBar.style.width = "0%";
                strengthBar.className = "strength-bar";
                return;
            }

            requestBody.num_words = numWords;
            requestBody.separator = separator;
            requestBody.include_digit = includeDigit;
            requestBody.include_symbol = includeSymbol;
            requestBody.wordlist_name = selectedWordlist;
            requestBody.capitalization = capitalization; // NEW: Send to backend
            requestBody.placement = placement; // NEW: Send to backend
        }

        showLoading(true);

        try {
            const response = await fetch(BACKEND_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok && data.ai_strength_score !== undefined) {
                const aiScore = data.ai_strength_score;
                strengthBar.className = "strength-bar";
                strengthBar.classList.add(`score-${aiScore}`);
                strengthBar.style.width = ((aiScore + 1) / 5) * 100 + "%";

                const strengthLabels = [
                    "Very Weak",
                    "Weak",
                    "Fair",
                    "Good",
                    "Strong",
                ];
                strengthText.className = "strength-text";
                strengthText.classList.add(`score-${aiScore}`);
                strengthText.textContent = `AI Prediction: ${strengthLabels[aiScore]}`;

                if (data.charset_recommendation) {
                    charsetRecommendationText.textContent =
                        data.charset_recommendation;
                    charsetRecommendationText.style.color =
                        data.charset_recommendation.includes("Good")
                            ? "green"
                            : "orange";
                }
            } else {
                strengthText.textContent = "Could not get AI strength.";
                strengthBar.style.width = "0%";
                strengthBar.className = "strength-bar";
                displayError(
                    data.error || "Failed to get AI strength prediction.",
                );
                charsetRecommendationText.textContent = "";
            }
        } catch (error) {
            strengthText.textContent = "Backend Error";
            strengthBar.style.width = "0%";
            strengthBar.className = "strength-bar";
            displayError(
                "Error connecting to the backend for strength prediction. Is the Flask server running?",
            );
            charsetRecommendationText.textContent = "";
            console.error("Fetch error for strength prediction:", error);
        } finally {
            showLoading(false);
        }
    }

    // Attach event listeners to all relevant inputs to update strength dynamically
    allConfigInputs.forEach((input) => {
        input.addEventListener("input", predictStrengthAndCharsetFromBackend);
        input.addEventListener("change", predictStrengthAndCharsetFromBackend);
    });

    // Event listeners for generation type radio buttons
    typePasswordRadio.addEventListener("change", toggleOptionsDisplay);
    typePassphraseRadio.addEventListener("change", toggleOptionsDisplay);
    customCharacterSetInput.addEventListener("input", toggleIncludeCheckboxes);

    // Initial setup calls on page load
    toggleOptionsDisplay();
    toggleIncludeCheckboxes();
    renderPasswordHistory();

    // Theme Toggle Logic
    const currentTheme = localStorage.getItem("theme");
    if (currentTheme === "dark") {
        document.body.classList.add("dark-mode");
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener("change", () => {
        if (darkModeToggle.checked) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light"); // Corrected key
        }
    });

    // Main Generate Button Listener
    generateBtn.addEventListener("click", async () => {
        errorMessageDisplay.textContent = "";
        errorMessageDisplay.classList.add("hidden");

        let requestBody = {};
        let currentGenerationType = typePasswordRadio.checked
            ? "password"
            : "passphrase";
        requestBody.type = currentGenerationType;

        if (currentGenerationType === "password") {
            const length = parseInt(passwordLengthInput.value);
            const customCharsToInclude = customCharacterSetInput.value.trim();
            const excludeAmbiguous = excludeAmbiguousInput.checked;
            const excludeCustomChars = excludeCustomCharsInput.value;
            const requireMinCharTypes = requireMinCharTypesInput.checked;
            const noRepeatingChars = noRepeatingCharsInput.checked;

            if (isNaN(length) || length < 6 || length > 30) {
                displayError(
                    "Password length must be between 6 and 30 characters.",
                );
                return;
            }
            if (
                !customCharsToInclude &&
                !(
                    includeUppercaseInput.checked ||
                    includeLowercaseInput.checked ||
                    includeDigitsInput.checked ||
                    includeSymbolsInput.checked
                )
            ) {
                displayError(
                    "At least one character type must be selected (or provide custom characters).",
                );
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
            requestBody.require_min_char_types = requireMinCharTypes;
            requestBody.no_repeating_chars = noRepeatingChars;
        } else {
            // currentGenerationType === 'passphrase'
            const numWords = parseInt(numWordsInput.value);
            const separator = wordSeparatorInput.value;
            const includeDigit = passphraseIncludeDigitInput.checked;
            const includeSymbol = passphraseIncludeSymbolInput.checked;
            const selectedWordlist = wordlistSelect.value;
            // NEW: Get selected capitalization and placement
            const capitalization = document.querySelector(
                'input[name="passphraseCapitalization"]:checked',
            ).value;
            const placement = placementSelect.value;

            if (isNaN(numWords) || numWords < 2 || numWords > 10) {
                displayError("Number of words must be between 2 and 10.");
                return;
            }

            requestBody.num_words = numWords;
            requestBody.separator = separator;
            requestBody.include_digit = includeDigit;
            requestBody.include_symbol = includeSymbol;
            requestBody.wordlist_name = selectedWordlist;
            requestBody.capitalization = capitalization; // NEW: Send to backend
            requestBody.placement = placement; // NEW: Send to backend
        }

        showLoading(true);

        try {
            const response = await fetch(BACKEND_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok) {
                generatedPasswordInput.value = data.password;
                addPasswordToHistory(data.password);
            } else {
                displayError(data.error || "Failed to generate password.");
                generatedPasswordInput.value = "";
            }
        } catch (error) {
            displayError(
                "Error connecting to the backend. Is the Flask server running?",
            );
            console.error("Fetch error:", error);
            generatedPasswordInput.value = "";
        } finally {
            showLoading(false);
        }
    });

    // Generate Another Button Listener - triggers the main generate button's click event
    generateAnotherBtn.addEventListener("click", () => {
        generateBtn.click();
    });

    // Main Copy Button Listener (now uses generic copyToClipboard)
    copyBtn.addEventListener("click", () => {
        copyToClipboard(generatedPasswordInput.value, copyBtn);
    });

    // Fix for dark mode local storage key (ensure it's consistent on initial load)
    // This block runs after initial renderPasswordHistory, so it's fine.
    if (darkModeToggle.checked) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.setItem("theme", "light");
    }
});
