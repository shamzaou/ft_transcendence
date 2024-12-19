document.getElementById('sign-in').addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', data.access);  // Store the JWT
            localStorage.setItem('refresh_token', data.refresh); // Store refresh token
            alert('Login successful!');
            window.location.href = "{% url 'homepage' %}";  // Redirect to homepage using URL tag
        } else {
            alert('Login failed: ' + data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login. Please try again.');
    }
});

document.getElementById('register').addEventListener('click', () => {
    window.location.href = "{% url 'register' %}";
});


// function submitForm(event) {
//     event.preventDefault(); // Prevent default action

//     const form = event.target.closest('form'); // Get the closest form element
//     const username = document.getElementById('username').value;
//     const password = document.getElementById('password').value;
//     const usernameError = document.getElementById('usernameError');
//     const passwordError = document.getElementById('passwordError');

//     let valid = true;

//     // Reset error messages
//     usernameError.textContent = '';
//     passwordError.textContent = '';

//     // Username validation
//     if (username.trim() === '') {
//         usernameError.textContent = 'Username is required.';
//         usernameError.style.display = 'block';
//         valid = false;
//     }

//     // Password validation
//     if (password.trim() === '') {
//         passwordError.textContent = 'Password is required.';
//         passwordError.style.display = 'block';
//         valid = false;
//     }

//     if (valid) {
//         // Prepare data to send
//         const data = {
//             username: username,
//             password: password
//         };

//         fetch('https://localhost/api/login/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(data)
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.message === 'Login successful') {
//                 sessionStorage.setItem('token', data.token);
//                 if (data.otp_required) {
//                     const otp = prompt("Enter the OTP sent to your email: Functionality for email is commented in development, the otp will be stored in a file in backend/djangoback/otp_temp.txt you can verify from there");
//                     fetch('https://localhost/api/verify_otp/', {
//                         method: 'POST',
//                         headers: {
//                             'Content-Type': 'application/json',
//                             'Authorization': `Bearer ${data.token}`
//                         },
//                         body: JSON.stringify({ username: username, otp: otp })
//                     })
//                     .then(response => response.json())
//                     .then(data => {
//                         if (data.message === 'OTP verified, 2FA enabled') {
//                             window.location.href = '/home';
//                             sessionStorage.setItem("username", username);
//                         } else {
//                             alert('Invalid OTP.');
//                         }
//                     })
//                     .catch(error => console.error('Error:', error));
//                 } else {
//                     window.location.href = '/home';
//                     sessionStorage.setItem("username", username);
//                 }
//             } else {
//                 alert(data.message);
//             }
//         })
//         .catch(error => console.error('Error:', error));
//     }
// }



// async function intra_auth() {
//     try {
//         const response = await fetch('https://localhost/api/redirect_uri/', {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//             },
//         });
//         if (response.ok) {
//             const result = await response.json();
//             window.location.href = result.oauth_link;
//         } else {
//             console.error('Response was not ok:', response);
//         }
//     } catch (error) {
//         console.error('Fetch error:', error);
//     }
// }


// // Example of using session storage data
// window.onload = function() {
//     const username = sessionStorage.getItem('username');
//     const token = sessionStorage.getItem('token');

//     if (username && token) {
//         document.getElementById('username-display').textContent = username;
//         // Use token for fetching protected resources, etc.
//     } else {
//         // Redirect to login if token is missing
//         window.location.href = '/login';
//     }
// };


// // login.js
// window.onload = function() {
//     const urlParams = new URLSearchParams(window.location.search);
//     const token = urlParams.get('token');
//     if (token) {
//         sessionStorage.setItem('token', token);
//         fetchUserDetails(token);
//     }
// };

// async function fetchUserDetails(token) {
//     try {
//         const response = await fetch('https://localhost/api/get_user_info/', {
//             method: "GET",
//             headers: {
//                 "Content-Type": "application/json",
//                 "Authorization": `Bearer ${token}`
//             },
//         });
//         if (response.ok) {
//             const data = await response.json();
//             sessionStorage.setItem('username', data.username);
//             document.getElementById('username-display').textContent = data.username;
//             document.getElementById('match-count').textContent = data.match_count;
//         } else {
//             console.error('Failed to fetch user info:', response);
//         }
//     } catch (error) {
//         console.error('Fetch error:', error);
//     }
// }




// sessionStorage.removeItem("username");

// document.getElementById('username').addEventListener('keydown', function (event) {
//     if (event.key === 'Enter') {
//         event.preventDefault();
//         document.getElementById('password').focus();
//     }
// });

// document.getElementById('password').addEventListener('keydown', function (event) {
//     if (event.key === 'Enter') {
//         submitForm(event);
//     }
// });