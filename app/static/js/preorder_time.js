// Select the preorder select element
const preorderSelect = document.getElementById('preorder');
const quantity = document.getElementById('product__quantity');
const quantity_subtitle = document.getElementById('product__quantity-subtitle');

// Listen for change event on the preorder select element
preorderSelect.addEventListener('change', function() {
  // Get the selected value
  const selectedValue = preorderSelect.value;

  // Find the parent div.input-box of the select element
  const inputBox = preorderSelect.closest('.input-box');

  // Check if the selected value is 1 (Time Based)
  if (selectedValue === '1') {
    console.log("GWAPO KO")

    // Check if the date input already exists to avoid duplication
    if (!inputBox.querySelector('input[type="date"]')) {
      // Create a new date input
        const dateInput = document.createElement('input');
        dateInput.type = 'date';
        dateInput.id = 'preorderDate'; // You can give it a specific ID
        dateInput.name = 'preorderDate'; // Set the name for the input (used for form submission)
        dateInput.required = true; // Make the input required
        dateInput.placeholder = 'Select preorder end date...'; // Placeholder text
        quantity_subtitle.innerText = 'Days to go...'

        // Add the onchange attribute inline
        dateInput.setAttribute('onchange', 'logDate(this)');

        // Insert the date input into the inputBox
        inputBox.appendChild(dateInput);

        // Now, append inputBox to the form
        const form = document.getElementById("product-form");
        const dateInputSubmit = document.createElement('input');
        dateInputSubmit.type = 'date';
        dateInputSubmit.id = 'submitPreorderDate';
        dateInputSubmit.name = 'preorderDate'; // Set the name for the input (used for form submission)
        dateInputSubmit.required = true; // Make the input required
        dateInputSubmit.placeholder = 'Select preorder end date...'; // Placeholder text
        dateInputSubmit.hidden = true;
        
        form.appendChild(dateInputSubmit);
    }
  } else {
    console.log("PANGET KO")

    // Remove the date input if it exists and the selected value is not 1
    const existingDateInput = inputBox.querySelector('#preorderDate');
    const existingDateInputSubmit = inputBox.querySelector('#preorderDate');
    if (existingDateInput) {existingDateInput.remove();}
    if (existingDateInputSubmit) {existingDateInputSubmit.remove();}
    quantity_subtitle.innerText = 'preorder count'
    quantity.innerText = 0;
  }
});

const create_product = document.getElementById("create_product");
create_product.addEventListener("click", () => {
  const submitDate = document.getElementById("submitPreorderDate")
  submitDate.value = document.getElementById("preorderDate").value
  console.log(submitDate.value)
})


// Function to log the selected date
function logDate(input) {
  const today = new Date();
  const releaseDate = new Date(input.value)
  const formattedDate = today.toISOString().split('T')[0];
  const formattedReleaseDate = releaseDate.toISOString().split('T')[0];
  
  console.log("Today's Date: ",formattedDate); // Logs the date in 'YYYY-MM-DD' format
  console.log("Selected: ",formattedReleaseDate);

  // Get the difference in milliseconds
  const differenceInMillis = releaseDate - today;

  // Convert the difference from milliseconds to days
  const differenceInDays = Math.round(differenceInMillis / (1000 * 60 * 60 * 24));

  console.log(differenceInDays); // Logs the difference in days

  quantity.innerText = differenceInDays;
}