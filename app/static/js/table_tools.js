// JavaScript for row click highlight and checkbox toggle
const rows = document.querySelectorAll("table tbody tr");
const checkAll = document.getElementById("checkAll");
const table_tools = document.querySelector("#deleteAll")
const deleteOne = document.querySelector("#deleteOne")

// Collect values of all checked rows
function getCheckedRows() {
  const checkedRows = []; // Array to store selected row values

  // Select all rows in the table body
  const tableRows = document.querySelectorAll("table tbody tr");

  tableRows.forEach(row => {
    const checkbox = row.querySelector("input[type='checkbox']"); // Find the checkbox in the row
    
    if (checkbox.checked) {
      // Extract the Order ID or any other values from the row
      const orderId = row.getAttribute("value"); // Order# column
      checkedRows.push(orderId); // Add the orderId to the array
    }
  });

  return checkedRows; // Return the array of checked values
}

// Example Usage: Attach to a button click
table_tools.addEventListener("click", () => {
  const selectedOrders = getCheckedRows(); // Get all checked rows
  
  if (selectedOrders.length > 0) {
    console.log("Selected Orders:", selectedOrders); // Log the selected orders
    // Call your deleteOrder function here with the collected order IDs
    selectedOrders.forEach(orderId => deleteOrder(orderId));
  } else {
    console.log("No orders selected.");
  }

  checkAll.checked = false
});

// Function to delete checked rows
function deleteCheckedRows() {
  const tableRows = document.querySelectorAll("table tbody tr"); // Select all table rows
  
  tableRows.forEach(row => {
    const checkbox = row.querySelector("input[type='checkbox']"); // Find the checkbox in the row
    
    if (checkbox.checked) {
      row.remove(); // Remove the row from the DOM
    }
  });
}

// Helper function to toggle `table_tools` visibility
function toggleTableToolsVisibility() {
  const checkedCount = document.querySelectorAll("table tbody input[type='checkbox']:checked").length;
  table_tools.style.display = checkedCount > 1 ? "block" : "none";
  table_tools.style.visibility = checkedCount > 1 ? "visible" : "hidden";
  deleteOne.style.visibility = ((checkedCount > 0) && (checkedCount < 2)) ? "visible" : "hidden";
  if (window.location.pathname !== '/seller/my-orders') {
    editOneBtn.style.visibility = ((checkedCount > 0) && (checkedCount < 2)) ? "visible" : "hidden";
  }
}

let lastClickedRow = null;
let clickCount = 0;

rows.forEach(row => {
  const checkbox = row.querySelector("input[type='checkbox']"); 

  row.addEventListener("click", (e) => {
    if (e.target !== checkbox && !e.target.closest("input[type='checkbox']")) {
      const orderValue = row.getAttribute("value"); // Get the 'value' attribute from the <tr>

      // Check if the same row was clicked twice consecutively
      if (lastClickedRow === row) {
        clickCount++;
        if (clickCount === 2) {
          openModal(orderValue); // Open modal on the second click
          clickCount = 0; // Reset click count after opening the modal
        }
      } else {
        // Reset the click count and set the new last clicked row
        lastClickedRow = row;
        clickCount = 1;
        setDeleteBtn(orderValue);
        if (window.location.pathname !== '/seller/my-orders') {
          setEditBtn(orderValue)
        }
        
        

        // Reset all other rows
        rows.forEach(r => {
          r.classList.remove("highlight");
          r.querySelector("input[type='checkbox']").checked = false;
        });

        // Highlight the clicked row and check its checkbox
        row.classList.add("highlight");
        checkbox.checked = true;

        checkAll.checked = false;
        toggleTableToolsVisibility(); // Check visibility after changing selection
      }
    }
  });

  checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
      row.classList.add("highlight");
    } else {
      row.classList.remove("highlight");
    }
    toggleTableToolsVisibility(); // Check visibility after changing selection
  });
});

// Check All functionality
checkAll.addEventListener("change", () => {
  const isChecked = checkAll.checked;

  rows.forEach(row => {
    const checkbox = row.querySelector("input[type='checkbox']");
    checkbox.checked = isChecked; 
    if (isChecked) {
      row.classList.add("highlight"); 
      toggleTableToolsVisibility(); // Check visibility after changing selection

    } else {
      row.classList.remove("highlight"); 
      toggleTableToolsVisibility(); // Check visibility after changing selection
    }
  });
});
