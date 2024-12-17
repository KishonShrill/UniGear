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

function setDeleteBtn(orderValue) {
  deleteOneBtn.value = orderValue
}

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