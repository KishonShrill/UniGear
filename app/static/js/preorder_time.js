// preorder_time.js - Dynamic Preorder Time and Date Calculations

document.addEventListener("DOMContentLoaded", function () {
  const preorderSelect = document.getElementById("preorder");
  const quantity = document.getElementById("product__quantity");
  const quantitySubtitle = document.getElementById("product__quantity-subtitle");
  const numberOfDays = document.getElementById("number_of_days");
  const timeBasedDateGroup = document.getElementById("timeBasedDateGroup");
  const preorderDateInput = document.getElementById("preorderDate");
  const submitPreorderDate = document.getElementById("submitPreorderDate");

  function calculateDays(targetDateStr) {
    if (!targetDateStr) return 0;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const target = new Date(targetDateStr);
    target.setHours(0, 0, 0, 0);
    const diffMs = target.getTime() - today.getTime();
    return Math.max(1, Math.round(diffMs / (1000 * 60 * 60 * 24)));
  }

  function handlePreorderChange() {
    if (!preorderSelect) return;
    const selectedVal = preorderSelect.value;

    if (selectedVal === "1") {
      if (timeBasedDateGroup) {
        timeBasedDateGroup.style.display = "block";
      }

      if (preorderDateInput && !preorderDateInput.value) {
        const today = new Date();
        const oneWeekFromToday = new Date(today);
        oneWeekFromToday.setDate(today.getDate() + 8);
        const formattedDate = oneWeekFromToday.toISOString().split("T")[0];
        preorderDateInput.value = formattedDate;
      }

      if (preorderDateInput && preorderDateInput.value) {
        const days = calculateDays(preorderDateInput.value);
        if (quantity) quantity.innerText = days;
        if (numberOfDays) numberOfDays.value = days;
        if (submitPreorderDate) submitPreorderDate.value = preorderDateInput.value;
      }

      if (quantitySubtitle) {
        quantitySubtitle.innerText = "Days to go";
      }
    } else {
      if (timeBasedDateGroup) {
        timeBasedDateGroup.style.display = "none";
      }
      if (quantity) {
        const origData = quantity.getAttribute("data") || "0";
        quantity.innerText = origData;
      }
      if (quantitySubtitle) {
        quantitySubtitle.innerText = selectedVal === "0" ? "Goal Based" : "Preorders";
      }
      if (numberOfDays) numberOfDays.value = "";
      if (submitPreorderDate) submitPreorderDate.value = "";
    }
  }

  if (preorderSelect) {
    preorderSelect.addEventListener("change", handlePreorderChange);
    // Initial check on load (for edit mode)
    if (preorderSelect.value === "1") {
      handlePreorderChange();
    }
  }

  if (preorderDateInput) {
    preorderDateInput.addEventListener("change", function () {
      logDate(this);
    });
  }
});

function logDate(input) {
  if (!input || !input.value) return;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const releaseDate = new Date(input.value);
  releaseDate.setHours(0, 0, 0, 0);

  const diffMs = releaseDate.getTime() - today.getTime();
  const diffDays = Math.max(1, Math.round(diffMs / (1000 * 60 * 60 * 24)));

  const quantity = document.getElementById("product__quantity");
  const numberOfDays = document.getElementById("number_of_days");
  const submitPreorderDate = document.getElementById("submitPreorderDate");

  if (quantity) quantity.innerText = diffDays;
  if (numberOfDays) numberOfDays.value = diffDays;
  if (submitPreorderDate) submitPreorderDate.value = input.value;
}
