// Get references to the password input field and the toggle button
const passwordInput = document.querySelector('#password');
const toggleButton = document.querySelector('.toggle-password');

// Add a click event listener to the toggle button
toggleButton.addEventListener("click", function () {
  // If the password input field is currently of type "password", change it to type "text" (show the password)
  if (passwordInput.type === "password") {
    passwordInput.type = "text";
  // If the password input field is currently of type "text", change it to type "password" (hide the password)
  } else {
    passwordInput.type = "password";
  }
});