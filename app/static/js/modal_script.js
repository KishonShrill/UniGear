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