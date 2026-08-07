// =========================================
// CodeGuardian AI Registration
// =========================================


// =========================================
// API Endpoint
// =========================================

// Change this if your Django URL is different.
// Example:
// path("api/auth/register/", RegisterView.as_view(), name="register")

const API_URL = "/api/auth/register/";


// =========================================
// Get CSRF Token (Required for Django)
// =========================================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            // Check whether this cookie begins with the name we want
            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}

// Store CSRF token
const csrftoken = getCookie("csrftoken");


// =========================================
// HTML Elements
// =========================================

const form = document.getElementById("registerForm");

const username = document.getElementById("username");
const email = document.getElementById("email");
const password = document.getElementById("password");
const password2 = document.getElementById("password2");

const usernameError = document.getElementById("usernameError");
const emailError = document.getElementById("emailError");
const passwordError = document.getElementById("passwordError");

const message = document.getElementById("message");

const btnText = document.getElementById("btnText");
const loader = document.getElementById("loader");

const strengthBar = document.getElementById("strengthBar");
const strengthText = document.getElementById("strengthText");


// =========================================
// Toggle Password Visibility
// =========================================

document
    .getElementById("togglePassword")
    .addEventListener("click", function () {

        password.type =
            password.type === "password"
                ? "text"
                : "password";

    });


document
    .getElementById("togglePassword2")
    .addEventListener("click", function () {

        password2.type =
            password2.type === "password"
                ? "text"
                : "password";

    });


// =========================================
// Password Strength Indicator
// =========================================

password.addEventListener("input", function () {

    let score = 0;

    const value = password.value;

    if (value.length >= 8) score++;
    if (/[A-Z]/.test(value)) score++;
    if (/[a-z]/.test(value)) score++;
    if (/[0-9]/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;

    switch (score) {

        case 0:
        case 1:

            strengthBar.style.width = "20%";
            strengthBar.style.background = "#ff4d4d";
            strengthText.innerHTML = "Weak Password";

            break;

        case 2:

            strengthBar.style.width = "40%";
            strengthBar.style.background = "#ff9933";
            strengthText.innerHTML = "Fair Password";

            break;

        case 3:

            strengthBar.style.width = "60%";
            strengthBar.style.background = "#ffd633";
            strengthText.innerHTML = "Good Password";

            break;

        case 4:

            strengthBar.style.width = "80%";
            strengthBar.style.background = "#33cc66";
            strengthText.innerHTML = "Strong Password";

            break;

        case 5:

            strengthBar.style.width = "100%";
            strengthBar.style.background = "#00cc99";
            strengthText.innerHTML = "Very Strong Password";

            break;

    }

});


// =========================================
// Client-side Validation
// =========================================

function validate() {

    usernameError.innerHTML = "";
    emailError.innerHTML = "";
    passwordError.innerHTML = "";

    let valid = true;

    // Username length
    if (username.value.trim().length < 3) {

        usernameError.innerHTML =
            "Username must be at least 3 characters.";

        valid = false;
    }

    // Email format
    const emailRegex =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email.value)) {

        emailError.innerHTML =
            "Enter a valid email.";

        valid = false;
    }

    // Password length
    if (password.value.length < 8) {

        passwordError.innerHTML =
            "Password must contain at least 8 characters.";

        valid = false;
    }

    // Password match
    if (password.value !== password2.value) {

        passwordError.innerHTML =
            "Passwords do not match.";

        valid = false;
    }

    return valid;

}


// =========================================
// Loading Functions
// =========================================

function startLoading() {

    loader.style.display = "inline-block";

    btnText.innerHTML = "Creating Account...";

    form.querySelector("button").disabled = true;

}

function stopLoading() {

    loader.style.display = "none";

    btnText.innerHTML = "Create Account";

    form.querySelector("button").disabled = false;

}


// =========================================
// Success / Error Message
// =========================================

function showMessage(text, type) {

    message.style.display = "block";

    message.className = "message " + type;

    message.innerHTML = text;

}


// =========================================
// Submit Form
// =========================================

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    message.style.display = "none";

    if (!validate()) return;

    startLoading();

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {

                // Tell Django we're sending JSON
                "Content-Type": "application/json",

                // Required for Django CSRF protection
                "X-CSRFToken": csrftoken

            },

            body: JSON.stringify({

                username: username.value.trim(),

                email: email.value.trim(),

                password: password.value

            })

        });

        const data = await response.json();

        stopLoading();

        // ==========================
        // Registration Success
        // ==========================

        if (response.ok) {

            // Save tokens only if the API returns them

            if (data.access) {

                localStorage.setItem(
                    "access",
                    data.access
                );

            }

            if (data.refresh) {

                localStorage.setItem(
                    "refresh",
                    data.refresh
                );

            }

            showMessage(
                "Registration successful! Redirecting to login...",
                "success"
            );

            setTimeout(function () {

                window.location.href = "/login/";

            }, 1500);

        }

        // ==========================
        // Validation Errors
        // ==========================

        else {

            usernameError.innerHTML = "";
            emailError.innerHTML = "";
            passwordError.innerHTML = "";

            if (data.username) {

                usernameError.innerHTML =
                    data.username.join("<br>");

            }

            if (data.email) {

                emailError.innerHTML =
                    data.email.join("<br>");

            }

            if (data.password) {

                passwordError.innerHTML =
                    data.password.join("<br>");

            }

            // Handle DRF "detail" errors
            if (data.detail) {

                showMessage(
                    data.detail,
                    "error"
                );

            }

            // Handle non_field_errors
            else if (data.non_field_errors) {

                showMessage(
                    data.non_field_errors.join("<br>"),
                    "error"
                );

            }

            else {

                showMessage(
                    "Registration failed. Please correct the highlighted errors.",
                    "error"
                );

            }

        }

    }

    catch (error) {

        stopLoading();

        console.error(error);

        showMessage(
            "Unable to connect to the server.",
            "error"
        );

    }

});