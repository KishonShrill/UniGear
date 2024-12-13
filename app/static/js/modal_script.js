// const openButton = document.querySelector("[data-open-modal]")
const closeButton = document.querySelector("[data-close-modal]")
const modal = document.querySelector("[data-modal]")

// openButton.addEventListener("click", () => {
//   modal.showModal()
// })

closeButton.addEventListener("click", () => {
  modal.close()
})

function openModal(orderValue) {
  const modal = document.querySelector("dialog[data-modal]");
  modal.querySelector("div").textContent = `Order: ${orderValue}`; // Example usage of the order value
  modal.showModal(); // Open the dialog
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