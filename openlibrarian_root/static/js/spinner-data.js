document.addEventListener("DOMContentLoaded", function(){
  // Get the elements
  var spinnerBox = document.getElementById('spinnerBox');
  var dataBox = document.getElementById('dataBox');
  var submit = document.getElementById('submit-search');
  // Add event listener to submit button
  submit.addEventListener('click', function(){
    // Show spinnerBox and hide dataBox
    spinnerBox.classList.remove("not-visible");
    dataBox.classList.add("not-visible");
  });

  // Listen for AJAX response
  document.addEventListener('ajax:complete', function(event){
    // Check if the request was a POST request (i.e. search form submission)
    if (event.detail.method === 'POST') {
      // Hide spinnerBox and show dataBox
      spinnerBox.classList.add("not-visible");
      dataBox.classList.remove("not-visible");
    }
  });
});