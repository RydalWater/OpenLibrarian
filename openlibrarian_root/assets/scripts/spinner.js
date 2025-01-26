// Check if spinnerBox and form exist
if (!document.getElementById('spinnerBox') || !document.querySelector('form')) {
  // Do nothing
} else {
  // Get dataBox if it exists
  let dataBox = null;
  if (document.getElementById('dataBox')) {
    dataBox = document.getElementById('dataBox');
  }

  // Get the elements
  var spinnerBox = document.getElementById('spinnerBox');
  var form = document.querySelector('form');

  // Add event listener to submit of a form
  form.addEventListener('submit', function(){
    // Show spinnerBox and hide dataBox
    spinnerBox.classList.remove("not-visible");
    if (dataBox) {
      dataBox.classList.add("not-visible");
    }
  });

  // Listen for specifc button click
  document.addEventListener('click', function(event) {
    if (event.target.id === 'login' || event.target.id === 'refresh' || event.target.id === 'submit-search' || event.target.id === 'refresh-simple') {
      // Show spinnerBox and hide dataBox
      spinnerBox.classList.remove("not-visible");
      if (dataBox) {
        dataBox.classList.add("not-visible");
      }
    }
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
}