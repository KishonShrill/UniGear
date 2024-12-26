const deleteOneBtn = document.querySelector("#deleteOne")
const closeButton = document.querySelector("[data-close-modal]")
const modal = document.querySelector("dialog[data-modal]")


closeButton.addEventListener("click", () => {
  modal.close()
})

function openModal(orderValue, imgSource) {
  document.querySelector("#previewID").textContent = `Order: ${orderValue}`; // Example usage of the order value
  document.querySelector("#preview").src = imgSource; // Example usage of the order value
  modal.showModal(); // Open the dialog
}

deleteOneBtn.addEventListener("click", () => {
  const modal_btns = document.getElementById("modal-btns")
  let confirmButton = document.createElement("button");
  const existingConfirmButton = modal.querySelector("button[data-confirm]");
  modal.querySelector("div").textContent = `Are you sure you want to cancel order #${deleteOneBtn.value}`;

  // console.log("Status: " + deleteOneBtn.status + "\nSrc: " + deleteOneBtn.data)
  if (deleteOneBtn.status == 0 || (window.location.pathname == '/seller/my-products')) {
    confirmButton.textContent = "Confirm";
    confirmButton.classList.add("btn");
    confirmButton.classList.add("confirmBtn");
    confirmButton.textContent = "Confirm";
    confirmButton.setAttribute("onclick", `deleteOrder(${deleteOneBtn.value})`);

    modal_btns.appendChild(confirmButton);
  }
  
  // Remove any existing confirm button to avoid duplicates
  if (existingConfirmButton) {
    existingConfirmButton.remove();
  }
  confirmButton.setAttribute("data-confirm", "true");
  
  // Add image URL
  if (window.location.pathname !== '/seller/my-products') {
    document.getElementById("preview").src = deleteOneBtn.data;
  }

  // Add the confirm button to the modal
  modal.showModal()
})

function setDeleteBtn(orderValue, imgSource, paymentStatus) {
  deleteOneBtn.value = orderValue;
  console.log("Status: " + deleteOneBtn.value)
  deleteOneBtn.data = imgSource;
  console.log("Status: " + deleteOneBtn.data)
  deleteOneBtn.status = paymentStatus;
  console.log("Status: " + deleteOneBtn.status)
}