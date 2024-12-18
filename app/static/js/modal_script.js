const deleteOneBtn = document.querySelector("#deleteOne")
const closeButton = document.querySelector("[data-close-modal]")
const modal = document.querySelector("dialog[data-modal]")


closeButton.addEventListener("click", () => {
  modal.close()
})

function openModal(orderValue) {
  const modal = document.querySelector("dialog[data-modal]");
  modal.querySelector("div").textContent = `Order: ${orderValue}`; // Example usage of the order value
  modal.showModal(); // Open the dialog
}

deleteOneBtn.addEventListener("click", () => {
  modal.querySelector("div").textContent = `Are you sure you want to cancel order #${deleteOneBtn.value}`;

  let confirmButton = document.createElement("button");
  confirmButton.textContent = "Confirm";
  confirmButton.setAttribute("onclick", `deleteOrder(${deleteOneBtn.value})`);

  // Remove any existing confirm button to avoid duplicates
  const existingConfirmButton = modal.querySelector("button[data-confirm]");
  if (existingConfirmButton) {
    existingConfirmButton.remove();
  }

  // Add the confirm button to the modal
  confirmButton.setAttribute("data-confirm", "true");
  modal.appendChild(confirmButton);
  modal.showModal()
})

function setDeleteBtn(orderValue) {deleteOneBtn.value = orderValue}

// Function to open modal with product details
function openProductModal(productImageURL, productName) {
  const modal = document.querySelector("dialog[data-modal]");

  // Check if imageURL is valid, if not, use the placeholder
  const imageSrc = productImageURL ? productImageURL : '/static/images/placeholder.jpg';

  // Set the modal content dynamically
  modal.querySelector("div").textContent = productName; // Set the product name
  modal.querySelector("img").src = imageSrc; // Set the product image URL or placeholder
  modal.querySelector("img").alt = `${productName} image`; // Set alt text for the image

  modal.showModal(); // Open the dialog
}

// Add event listener to the product table rows for double-click
document.querySelectorAll("table tbody tr").forEach(row => {
  row.addEventListener("dblclick", () => {
    // Extract product details from the row
    const productImageURL = row.dataset.imageUrl || ''; // Assuming the image URL is stored as a data attribute

    // Open the modal with the product details
    openProductModal(productImageURL);
  });
});

// Get references to the new modal elements
const paymentModal = document.getElementById("proofPaymentModal");
const paymentModalContent = document.getElementById("paymentModalContent");
const paymentModalImage = document.getElementById("paymentModalImage");
const paymentCancelBtn = document.getElementById("paymentCancelBtn");
const paymentConfirmBtn = document.getElementById("paymentConfirmBtn");

// Add event listeners to all file input fields
document.querySelectorAll('input[type="file"]').forEach(input => {
  input.addEventListener("change", (event) => {
    const file = event.target.files[0]; // Get the selected file
    if (file) {
      const reader = new FileReader();

      // Preview the file in the modal
      reader.onload = function (e) {
        paymentModalContent.textContent = "Preview your Proof of Payment:";
        paymentModalImage.src = e.target.result; // Set the image preview
        paymentModalImage.style.display = "block"; // Show the image

        // Open the modal
        paymentModal.showModal();
      };

      // Read the file only if it's an image
      if (file.type.startsWith("image/")) {
        reader.readAsDataURL(file);
      } else {
        alert("Only image files are supported for preview.");
        event.target.value = ""; // Clear invalid files
      }
    }
  });
});

// Cancel button logic
paymentCancelBtn.addEventListener("click", () => {
  // Reset the file input
  document.querySelectorAll('input[type="file"]').forEach(input => {
    if (input.files.length > 0) {
      input.value = ""; // Clear file input
    }
  });

  // Close the modal
  paymentModal.close();
});

// Confirm button logic
paymentConfirmBtn.addEventListener("click", () => {
  console.log("File upload confirmed."); // Placeholder for actual upload logic
  
  paymentModal.close(); // Close the modal
});

function handleFileUpload(event, orderId) {
  const file = event.target.files[0]; // Get the selected file
  if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
          // Open the preview modal
          const paymentModalContent = document.getElementById('paymentModalContent');
          const paymentModalImage = document.getElementById('paymentModalImage');
          const paymentModal = document.getElementById('proofPaymentModal');
          const paymentConfirmBtn = document.getElementById('paymentConfirmBtn');

          paymentModalContent.textContent = "Preview your Proof of Payment:";  // Set content
          paymentModalImage.src = e.target.result;  // Set the image preview
          paymentModalImage.style.display = "block";  // Show the image
          paymentModal.showModal();  // Open the modal

          // Add Confirm button behavior
          paymentConfirmBtn.onclick = function () {
              // Create FormData object to send the file to the backend
              const formData = new FormData();
              formData.append('file', file);
              

              // Send the file to the server for upload
              fetch('/user/my-orders/upload', {  // Ensure this matches your Flask route
                  method: 'POST',
                  headers: {
                    
                  }
                  body: formData
              })
              .then(response => response.json())
              .then(data => {
                  const cloudinaryUrl = data.url; // Get Cloudinary URL from response
                  console.log(cloudinaryUrl)
                  // Update the UI and save the URL to the database
                  const proofCell = document.getElementById(`proofCell_${orderId}`);
                  proofCell.innerHTML = `
                      <button onclick="viewUploadedProof('${cloudinaryUrl}', ${orderId})">
                          View Proof
                      </button>
                  `;

                  paymentModal.close();  // Close the modal after successful upload
              })
              .catch(error => {
                  console.error('Error uploading the file:', error);
                  alert('Failed to upload the file, please try again.');
              });
          };
      };

      // Check if the file is an image and display it
      if (file.type.startsWith("image/")) {
          reader.readAsDataURL(file);  // For image files
      } else {
          alert("Only image files are supported for preview.");
          event.target.value = "";  // Clear invalid files
      }
  }
}

function viewUploadedProof(imageURL, orderId) {
  const viewModal = document.getElementById("proofPaymentViewModal");
  const viewModalImage = document.getElementById("viewModalImage");

  // Set the modal content with the uploaded proof
  viewModalImage.src = imageURL; // Set the image preview
  viewModal.showModal(); // Open the modal

  // Close button behavior
  const viewCloseBtn = document.getElementById("viewCloseBtn");
  viewCloseBtn.onclick = function () {
    viewModal.close(); // Close the modal
  };

  // Change button behavior
  const viewChangeBtn = document.getElementById("viewChangeBtn");
  viewChangeBtn.onclick = function () {
    const proofCell = document.getElementById(`proofCell_${orderId}`);
    
    // Show the original file input
    const fileInput = document.getElementById(`paymentProof_${orderId}`);
    if (fileInput) {
      fileInput.style.display = "block"; // Show input field again
    }
  
    // Remove the "View Proof" button
    proofCell.querySelector('button').remove();
    
    viewModal.close(); // Close the modal
  };  
}
