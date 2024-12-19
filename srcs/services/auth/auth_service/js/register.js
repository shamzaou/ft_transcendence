document.getElementById('register-button').addEventListener('click', async () => {
    console.log('Submit button clicked!');  // Debug message to ensure script is running

    const username = document.getElementById('id_username').value;
    const email = document.getElementById('id_email').value;
    const password1 = document.getElementById('id_password1').value;
    const password2 = document.getElementById('id_password2').value;

    // Validate that passwords match
    if (password1 !== password2) {
        alert("Passwords do not match");
        return;
    }

    // Prepare the data to send to the server
    const formData = {
        username: username,
        email: email,
        password: password1,
    };

    try {
        // Send the form data to the server
        const response = await fetch('/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        // Parse the JSON response
        const data = await response.json();

        if (response.ok) {
            alert('Registration successful!');
            window.location.href = '/login/';  // Redirect to the login page
        } else {
            alert('Registration failed: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});


// function registerForm(event) {
//     event.preventDefault(); // Prevent default action

//     const form = event.target.closest('form'); // Get the closest form element
//     const username = document.getElementById('username').value;
//     const password = document.getElementById('password').value;
//     const confirmpassword = document.getElementById('confirmpassword').value;
//     const usernameError = document.getElementById('usernameError');
//     const passwordError = document.getElementById('passwordError');
//     const confirmPasswordError = document.getElementById('confirmPasswordError');

//     let valid = true;

//     // Reset error messages
//     usernameError.textContent = '';
//     passwordError.textContent = '';
//     confirmPasswordError.textContent = '';

//     // Username validation
//     if (username.trim() === '') {
//         usernameError.textContent = 'Username is required.';
// 		usernameError.style.display = 'block';
//         valid = false;
//     }

//     // Password validation
//     if (password.trim() === '') {
//         passwordError.textContent = 'Password is required.';
// 		passwordError.style.display = 'block';
//         valid = false;
//     }

//     if (confirmpassword.trim() === '') {
//         confirmPasswordError.textContent = 'Password is required.';
// 		confirmPasswordError.style.display = 'block';
//         valid = false;
//     }
//     else if (password !== confirmpassword) {
//         confirmPasswordError.textContent = 'Passwords do not match.';
//         confirmPasswordError.style.display = 'block';
//         valid = false;
//     }

//     if (valid) {
//         // Prepare data to send
//         const formData = new FormData();
//         formData.append('username', username);
//         formData.append('password', password);

//         fetch('https://localhost/api/register/', {
//             method: 'POST',
//             body: formData
//         })
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error('Network response was not ok');
//             }
//             return response.json();
//         })
//         .then(data => {
//             console.log('Success:', data);
// 			window.location.href = '/login'; 
//             // Handle successful login, e.g., redirect to another page
//         })
//         .catch(error => {
//             console.error('Error:', error);
// 			alert('Invalid username or password.');
//             // Handle errors, e.g., display a message to the user
//         });
//     }
// }

// document.getElementById('username').addEventListener('keydown', function (event) {
//     if (event.key === 'Enter') {
//         event.preventDefault();
//         document.getElementById('password').focus();
//     }
// });

// document.getElementById('password').addEventListener('keydown', function (event) {
//     if (event.key === 'Enter') {
//         event.preventDefault();
//         document.getElementById('confirmpassword').focus();
//     }
// });

// document.getElementById('confirmpassword').addEventListener('keydown', function (event) {
//     if (event.key === 'Enter') {
//         registerForm(event);
//     }
// });

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