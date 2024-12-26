const deleteOneBtn = document.querySelector("#deleteOne");
const closeButton = document.querySelector("[data-close-modal]");
const modal = document.querySelector("dialog[data-modal]");
const modal_btns = document.getElementById("modal-btns")
const toggleStatusBtn = document.createElement("button");  

closeButton.addEventListener("click", () => {
  modal.close();
});

function openModal(orderId, orderValue, imgSource, currentStatus) {
  modal.querySelector("#modal-text").textContent = "Are you sure you want to mark as Paid?";
  modal.querySelector("#order_number").textContent = `Order: ${orderValue}`;
  modal.querySelector("img").src = `${imgSource}`;
  
  console.log("Source: " + imgSource)
  if (imgSource != 'None') {
    toggleStatusBtn.setAttribute('data-order-id', orderId);  
    toggleStatusBtn.classList.add("btn");
    toggleStatusBtn.classList.add("confirmBtn");
    if (currentStatus === 1) {
      toggleStatusBtn.textContent = "Mark as Unpaid";  
    } else {
      toggleStatusBtn.textContent = "Mark as Paid";  
    }
    console.log("YAHOO")
  }
  
  const existingConfirmButton = modal.querySelector("button[data-confirm]");
  if (existingConfirmButton) {
    existingConfirmButton.remove();
  }
  toggleStatusBtn.setAttribute("data-confirm", "true");
  
  if (imgSource != 'None') {modal_btns.appendChild(toggleStatusBtn);}
  modal.showModal();
}

toggleStatusBtn.addEventListener("click", () => {
  const orderId = toggleStatusBtn.getAttribute('data-order-id'); 

  toggleOrderStatus(orderId);  
  modal.close();  
});


function toggleOrderStatus(orderId) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  fetch('/toggle_order_status', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ order_id: orderId }) 
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      const row = document.querySelector(`tr[data-order-id="${orderId}"]`);
      const statusCell = row.querySelector('td:nth-child(9)'); 

      if (data.new_status === 1) {
        statusCell.innerHTML = '<b>Paid</b>';
        statusCell.style.color = 'green';
      } else {
        statusCell.innerHTML = '<b>Pending</b>';
        statusCell.style.color = "#d3d300";
      }

      toggleStatusBtn.textContent = data.new_status === 1 ? "Mark as Unpaid" : "Mark as Paid";
    } else {
      alert('Failed to update status.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('An error occurred while updating the status.');
  });
}


// Delete order functionality
deleteOneBtn.addEventListener("click", () => {
  modal.querySelector("#modal-text").textContent = `Are you sure you want to cancel your order?`;
  modal.querySelector("#order_number").textContent = `Order: ${deleteOneBtn.value}`;
  let confirmButton = document.createElement("button");

  if (deleteOneBtn.status == 0) {
    confirmButton.textContent = "Confirm";
    confirmButton.classList.add("btn");
    confirmButton.classList.add("confirmBtn");
    confirmButton.setAttribute("onclick", `deleteOrder(${deleteOneBtn.value})`);
    modal_btns.appendChild(confirmButton);
  }

  // Remove any existing confirm button to avoid duplicates
  const existingConfirmButton = modal.querySelector("button[data-confirm]");
  if (existingConfirmButton) {
    existingConfirmButton.remove();
  }
  
  // Add the confirm button to the modal
  confirmButton.setAttribute("data-confirm", "true");
  modal.showModal();
});

// Set delete button value when clicking on a row
function setDeleteBtn(orderValue, imgSource, paymentStatus) {
  deleteOneBtn.value = orderValue;
  console.log("Status: " + deleteOneBtn.value)
  deleteOneBtn.data = imgSource;
  console.log("Status: " + deleteOneBtn.data)
  deleteOneBtn.status = paymentStatus;
  console.log("Status: " + deleteOneBtn.status)
}
