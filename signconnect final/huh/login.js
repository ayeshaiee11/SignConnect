// Switch between Login and Signup forms
function switchToSignup() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
}

function switchToLogin() {
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}


// Toggle password visibility
function togglePassword(inputId) {

    const input = document.getElementById(inputId);

    if (input.type === "password") {
        input.type = "text";
    } 
    else {
        input.type = "password";
    }
}


// Create animated bubbles
function createBubbles() {

    const container = document.getElementById('bubbles-container');

    const pastelColors = [
        'rgba(255, 182, 193, 0.4)',
        'rgba(173, 216, 230, 0.4)',
        'rgba(221, 160, 221, 0.4)',
        'rgba(255, 218, 185, 0.4)',
        'rgba(176, 224, 230, 0.4)',
        'rgba(255, 192, 203, 0.4)',
        'rgba(216, 191, 216, 0.4)',
        'rgba(152, 251, 152, 0.4)',
        'rgba(255, 228, 181, 0.4)',
        'rgba(230, 230, 250, 0.4)'
    ];

    for (let i = 0; i < 15; i++) {

        const bubble = document.createElement('div');
        bubble.className = 'bubble';

        const size = Math.random() * 80 + 40;
        const left = Math.random() * 100;
        const duration = Math.random() * 10 + 15;
        const delay = Math.random() * 5;

        const color = pastelColors[Math.floor(Math.random() * pastelColors.length)];
        const highlightColor = color.replace('0.4', '0.6');

        bubble.style.width = size + 'px';
        bubble.style.height = size + 'px';
        bubble.style.left = left + '%';
        bubble.style.bottom = '-120px';

        bubble.style.background = `radial-gradient(circle at 30% 30%, ${highlightColor}, ${color})`;

        bubble.style.animationDuration = duration + 's';
        bubble.style.animationDelay = delay + 's';

        container.appendChild(bubble);
    }
}


// Run when page loads
document.addEventListener("DOMContentLoaded", () => {

    createBubbles();

    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");


    // LOGIN
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const username = loginForm.username.value.trim();
        const password = loginForm.password.value;

        if (!username || !password) {
            alert("Please enter your username and password.");
            return;
        }

        // Check if user exists in localStorage (registered via signup)
        const stored = localStorage.getItem('sc_user_' + username);
        if (stored) {
            const user = JSON.parse(stored);
            if (user.password !== password) {
                alert("Incorrect password. Please try again.");
                return;
            }
        }
        // If no account found, allow login anyway (first-time / demo mode)

        localStorage.setItem('sc_logged_in', 'true');
        localStorage.setItem('sc_username', username);
        window.location.href = 'index.html';
    });


    // SIGNUP
    signupForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const username = signupForm.username.value.trim();
        const email = signupForm.email.value.trim();
        const password = signupForm.password.value;
        const confirmPassword = signupForm.confirmPassword.value;

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        if (!username || !email || !password) {
            alert("Please fill in all fields.");
            return;
        }

        // Save user to localStorage
        localStorage.setItem('sc_user_' + username, JSON.stringify({ username, email, password }));
        localStorage.setItem('sc_logged_in', 'true');
        localStorage.setItem('sc_username', username);

        alert("Signup successful! Welcome to Sign Connect.");
        window.location.href = 'index.html';
    });

});