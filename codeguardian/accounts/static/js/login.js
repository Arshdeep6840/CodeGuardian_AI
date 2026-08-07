// =============================================
// CodeGuardian AI Login
// =============================================

const LOGIN_URL = "/api/auth/login/";      // SimpleJWT TokenObtainPairView
const PROFILE_URL = "/api/profile/";  // Optional

// =============================================
// Elements
// =============================================

const form = document.getElementById("loginForm");

const username = document.getElementById("username");
const password = document.getElementById("password");

const usernameError = document.getElementById("usernameError");
const passwordError = document.getElementById("passwordError");

const message = document.getElementById("message");

const btnText = document.getElementById("btnText");
const loader = document.getElementById("loader");

// =============================================
// Toggle Password
// =============================================

document
.getElementById("togglePassword")
.addEventListener("click", function () {

    password.type =
        password.type === "password"
            ? "text"
            : "password";

});

// =============================================
// Validation
// =============================================

function validate() {

    usernameError.innerHTML = "";
    passwordError.innerHTML = "";

    let valid = true;

    if (username.value.trim() === "") {

        usernameError.innerHTML =
            "Username is required.";

        valid = false;

    }

    if (password.value.trim() === "") {

        passwordError.innerHTML =
            "Password is required.";

        valid = false;

    }

    return valid;

}

// =============================================
// Loading
// =============================================

function startLoading() {

    loader.style.display = "inline-block";

    btnText.innerHTML = "Signing In...";

    form.querySelector("button").disabled = true;

}

function stopLoading() {

    loader.style.display = "none";

    btnText.innerHTML = "Sign In";

    form.querySelector("button").disabled = false;

}

// =============================================
// Message
// =============================================

function showMessage(text, type) {

    message.style.display = "block";

    message.className = "message " + type;

    message.innerHTML = text;

}

// =============================================
// Login
// =============================================

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    message.style.display = "none";

    if (!validate()) return;

    startLoading();

    try {

        const response = await fetch(LOGIN_URL, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                username: username.value,
                password: password.value

            })

        });

        const data = await response.json();

        stopLoading();

        if (response.ok) {

            // Save Tokens

            localStorage.setItem(
                "access",
                data.access
            );

            localStorage.setItem(
                "refresh",
                data.refresh
            );

            // Optional: Remember Me

            if (document.getElementById("remember").checked) {

                localStorage.setItem(
                    "remember",
                    "true"
                );

            }

            showMessage(
                "Login successful.",
                "success"
            );

            // Redirect

            setTimeout(function () {

                window.location.href = "/dashboard/";

            }, 1000);

        }

        else {

            if (data.detail) {

                showMessage(
                    data.detail,
                    "error"
                );

            } else {

                showMessage(
                    "Invalid username or password.",
                    "error"
                );

            }

        }

    }

    catch (error) {

        stopLoading();

        console.error(error);

        showMessage(
            "Unable to connect to server.",
            "error"
        );

    }

});