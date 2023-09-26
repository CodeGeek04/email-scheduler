document.getElementById("registerBtn").addEventListener("click", function() {
    console.log("Register button clicked");
    window.location.href = "http://127.0.0.1:5000/"; // Redirect to the Flask backend authentication route
});
