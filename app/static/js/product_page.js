// script.js
const buttons = document.querySelectorAll('.size-btn');
const selectedSizesInput = document.getElementById('selectedSizes');

buttons.forEach(button => {
  button.addEventListener('click', () => {
    // Toggle active class
    button.classList.toggle('active');
    
    // Update the hidden input with the selected sizes
    updateSelectedSizes();
  });
});

function updateSelectedSizes() {
  // Gather all active buttons
  const selectedSizes = Array.from(document.querySelectorAll('.size-btn.active'))
    .map(button => button.dataset.size);

  // Join the sizes into a comma-separated string and update the hidden input
  selectedSizesInput.value = selectedSizes.join(',');
}

function previewImage(event) {
  const img = document.getElementById('previewImage');
  const file = event.target.files[0];
  
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      img.src = e.target.result; // Set the image source to the uploaded file
      img.style.display = 'block'; // Show the image
    }
    reader.readAsDataURL(file);
  }
}
