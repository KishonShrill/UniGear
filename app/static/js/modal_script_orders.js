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
  
  toggleStatusBtn.setAttribute('data-order-id', orderId);  
  toggleStatusBtn.classList.add("btn");
  toggleStatusBtn.classList.add("confirmBtn");
  if (currentStatus === 1) {
    toggleStatusBtn.textContent = "Mark as Unpaid";  
  } else {
    toggleStatusBtn.textContent = "Mark as Paid";  
  }
  const existingConfirmButton = modal.querySelector("button[data-confirm]");
  if (existingConfirmButton) {
    existingConfirmButton.remove();
  }
  toggleStatusBtn.setAttribute("data-confirm", "true");
  
  modal_btns.appendChild(toggleStatusBtn);
  
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


// document.querySelectorAll("table tbody tr").forEach(row => {
//   row.addEventListener("dblclick", () => {
//     const orderId = row.dataset.orderId;  
//     const orderValue = row.children[1].textContent;  
//     const currentStatus = row.querySelector('td:nth-child(9)').textContent === "Paid" ? 1 : 0;  

//     openModal(orderId, orderValue, currentStatus);
//   });
// });

// Delete order functionality
deleteOneBtn.addEventListener("click", () => {
  modal.querySelector("#modal-text").textContent = `Are you sure you want to cancel your order?`;
  modal.querySelector("#order_number").textContent = `Order: ${deleteOneBtn.value}`;

  let confirmButton = document.createElement("button");
  confirmButton.textContent = "Confirm";
  confirmButton.classList.add("btn");
  confirmButton.classList.add("confirmBtn");
  confirmButton.setAttribute("onclick", `deleteOrder(${deleteOneBtn.value})`);

  // Remove any existing confirm button to avoid duplicates
  const existingConfirmButton = modal.querySelector("button[data-confirm]");
  if (existingConfirmButton) {
    existingConfirmButton.remove();
  }

  // Add the confirm button to the modal
  confirmButton.setAttribute("data-confirm", "true");
  modal_btns.appendChild(confirmButton);
  modal.showModal();
});

// Set delete button value when clicking on a row
function setDeleteBtn(orderValue) {
  deleteOneBtn.value = orderValue;
}

// // Function to open modal for product details
// function openProductModal(productImageURL, productName) {
//   const modal = document.querySelector("dialog[data-modal]");

//   const imageSrc = productImageURL ? productImageURL : '/static/images/placeholder.jpg';

//   modal.querySelector("div").textContent = productName; 
//   modal.querySelector("img").src = imageSrc; 
//   modal.querySelector("img").alt = `${productName} image`; 

//   modal.showModal();
// }
