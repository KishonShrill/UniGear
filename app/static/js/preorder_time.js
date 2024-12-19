// Select the preorder select element
const preorderSelect = document.getElementById('preorder');
const quantity = document.getElementById('product__quantity');
const quantity_subtitle = document.getElementById('product__quantity-subtitle');
const number_of_days = document.getElementById('number_of_days')

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

        // Calculate one week from today
        const today = new Date();
        const oneWeekFromToday = new Date(today);
        oneWeekFromToday.setDate(today.getDate() + 8); // Add 7 days to the current date
        const formattedDate = oneWeekFromToday.toISOString().split('T')[0]; // Format date as YYYY-MM-DD

        // Set the default value to one week from today
        dateInput.value = formattedDate;

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
        dateInputSubmit.value = formattedDate;

        form.appendChild(dateInputSubmit);
        
        const releaseDate = new Date(formattedDate)
        const differenceInMillis = releaseDate - today;
        const differenceInDays = Math.round(differenceInMillis / (1000 * 60 * 60 * 24));
        quantity.innerText = differenceInDays;
    }
  } else {
    console.log("PANGET KO")

    // Remove the date input if it exists and the selected value is not 1
    const existingDateInput = inputBox.querySelector('#preorderDate');
    const existingDateInputSubmit = inputBox.querySelector('#preorderDate');
    if (existingDateInput) {existingDateInput.remove();}
    if (existingDateInputSubmit) {existingDateInputSubmit.remove();}
    quantity_subtitle.innerText = 'preorder count'
    quantity.innerText = quantity.getAttribute("data");
  }
});

const create_product = document.getElementById("create_product");
create_product.addEventListener("click", () => {
  const selectedPreorderType = document.getElementById('preorder')

  if (selectedPreorderType.value == 1) {
    const submitDate = document.getElementById("submitPreorderDate");
    console.log(submitDate.value);
    submitDate.value = document.getElementById("preorderDate").value;
  }
  
  const slides_data = document.getElementById("slides_data");
  slides_data.value = slidesData;
  console.log(slides_data.value);
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
  number_of_days.value = differenceInDays;
}