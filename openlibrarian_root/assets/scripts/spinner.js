// Check if spinnerBox and form exist
if (!document.getElementById('spinnerBox') || !document.querySelector('form')) {
  // Do nothing
  console.log("Spinner not found");
} else {
  console.log("Spinner found");
  // Get the elements
  var spinnerBox = document.getElementById('spinnerBox');
  var form = document.querySelector('form');

  // Add event listener to searchBooks button
  form.addEventListener('submit', function(){
    // Show spinnerBox and hide dataBox
    spinnerBox.classList.remove("not-visible");
  });
  
  // Listen for AJAX response
  document.addEventListener('ajax:complete', function(event){
    // Check if the request was a POST request (i.e. search form submission)
    if (event.detail.method === 'POST') {
      // Hide spinnerBox and show dataBox
      spinnerBox.classList.add("not-visible");
    }
  });
}