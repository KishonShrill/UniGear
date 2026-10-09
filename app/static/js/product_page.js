// product_page.js - Seller Product Management Interactions

// Global state for uploaded slides
let slidesData = [];
let slideIndex = 1;
const dataTransfer = new DataTransfer();

document.addEventListener("DOMContentLoaded", function () {
  // -------------------- 1. Size Selector Controls --------------------
  const sizeButtons = document.querySelectorAll(".size-btn, .size-pill-btn");
  const selectedSizesInput = document.getElementById("selectedSizes");
  const sizeFeedback = document.getElementById("sizeFeedback");

  function getSelectedSizeNames() {
    const activeBtns = Array.from(
      document.querySelectorAll(".size-btn.active, .size-pill-btn.active")
    );
    if (!activeBtns.length) return "None selected";
    return activeBtns
      .map((btn) => btn.getAttribute("data-size-name") || btn.textContent.trim())
      .join(", ");
  }

  function updateSelectedSizes() {
    const activeBtns = Array.from(
      document.querySelectorAll(".size-btn.active, .size-pill-btn.active")
    );
    const selectedSizes = activeBtns.map((button) => button.dataset.size);

    if (selectedSizesInput) {
      selectedSizesInput.value = selectedSizes.join(",");
    }

    if (sizeFeedback) {
      if (selectedSizes.length > 0) {
        sizeFeedback.textContent = `Selected: ${getSelectedSizeNames()}`;
        sizeFeedback.classList.add("has-selection");
      } else {
        sizeFeedback.textContent = "Click sizes to select";
        sizeFeedback.classList.remove("has-selection");
      }
    }

    const sizeErrorNotice = document.getElementById("sizeErrorNotice");
    if (sizeErrorNotice && selectedSizes.length > 0) {
      sizeErrorNotice.style.display = "none";
    }
  }

  sizeButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      button.classList.toggle("active");
      updateSelectedSizes();
    });
  });

  // Initial update for pre-selected sizes (e.g. edit mode)
  updateSelectedSizes();

  // -------------------- 2. Tab Navigation --------------------
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetTabId = button.getAttribute("data-tab");

      tabButtons.forEach((btn) => {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
      });
      tabPanes.forEach((pane) => pane.classList.remove("active"));

      button.classList.add("active");
      button.setAttribute("aria-selected", "true");

      const targetPane = document.getElementById(targetTabId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });

  // -------------------- 3. Description Character Counter --------------------
  const descTextarea = document.getElementById("description");
  const descCounterEl = document.getElementById("descCharCount");

  if (descTextarea && descCounterEl) {
    const updateDescCounter = () => {
      const len = descTextarea.value.trim().length;
      descCounterEl.innerHTML = `<span>${len}</span> / 100 min characters`;
      if (len >= 100) {
        descCounterEl.classList.add("valid");
        descCounterEl.classList.remove("invalid");
      } else {
        descCounterEl.classList.add("invalid");
        descCounterEl.classList.remove("valid");
      }
    };

    descTextarea.addEventListener("input", updateDescCounter);
    updateDescCounter();
  }

  // -------------------- 4. Image Upload Handling --------------------
  const pictureUploadInput = document.getElementById("pictureUpload");
  const selectedImagesInput = document.getElementById("picture_urls");

  if (pictureUploadInput) {
    pictureUploadInput.addEventListener("change", function () {
      const files = Array.from(this.files);
      if (!files.length) return;

      const validExtensions = [".jpg", ".jpeg", ".png", ".webp"];
      for (const file of files) {
        const fileName = file.name.toLowerCase();
        const isValid = validExtensions.some((ext) => fileName.endsWith(ext));
        if (!isValid) {
          alert("Only image files (.jpg, .jpeg, .png, .webp) are allowed.");
          this.value = "";
          return;
        }
      }

      if (slidesData.length + files.length > 3) {
        alert("You can only have up to 3 photos in total.");
        this.value = "";
        return;
      }

      let loadedCount = 0;
      files.forEach((file) => {
        dataTransfer.items.add(file);

        const reader = new FileReader();
        reader.onload = function (e) {
          slidesData.push({ src: e.target.result, filename: file.name });
          loadedCount++;
          if (loadedCount === files.length) {
            slideIndex = slidesData.length;
            renderSlides();
          }
        };
        reader.readAsDataURL(file);
      });

      if (selectedImagesInput) {
        selectedImagesInput.files = dataTransfer.files;
      }
    });
  }

  // -------------------- 5. Modal Dialog & Summary Population --------------------
  const openModalBtn = document.querySelector("[data-open-modal]");
  const closeModalBtns = document.querySelectorAll("[data-close-modal]");
  const modal = document.querySelector("[data-modal]");
  const confirmBtn = document.getElementById("confirmSubmitBtn");

  if (openModalBtn && modal) {
    openModalBtn.addEventListener("click", () => {
      // Validate form basics before modal opens
      const nameVal = document.getElementById("name")?.value.trim() || "";
      const priceVal = document.getElementById("price")?.value.trim() || "";
      const descVal = document.getElementById("description")?.value.trim() || "";
      const typeSelect = document.getElementById("type");
      const typeVal = typeSelect ? typeSelect.options[typeSelect.selectedIndex]?.text : "";
      const preorderSelect = document.getElementById("preorder");
      const preorderVal = preorderSelect ? preorderSelect.options[preorderSelect.selectedIndex]?.text : "";
      const selectedSizes = selectedSizesInput?.value || "";

      // Quick visual field validation notice
      if (!nameVal) {
        alert("Please enter a product name.");
        document.getElementById("name")?.focus();
        return;
      }
      if (!priceVal || isNaN(priceVal) || parseInt(priceVal) <= 0) {
        alert("Please enter a valid price.");
        document.getElementById("price")?.focus();
        return;
      }
      if (descVal.length < 10) {
        alert("Please enter a product description (minimum 100 characters recommended).");
        document.getElementById("description")?.focus();
        return;
      }
      if (!selectedSizes) {
        const sizeError = document.getElementById("sizeErrorNotice");
        if (sizeError) sizeError.style.display = "flex";
        alert("Please select at least one available size.");
        return;
      }

      // Populate modal summary fields
      const modalName = document.getElementById("modal-name-preview");
      const modalPrice = document.getElementById("modal-price-preview");
      const modalType = document.getElementById("modal-type-preview");
      const modalSizes = document.getElementById("modal-sizes-preview");
      const modalModel = document.getElementById("modal-model-preview");

      if (modalName) modalName.textContent = nameVal;
      if (modalPrice) modalPrice.textContent = `₱${parseFloat(priceVal).toFixed(2)}`;
      if (modalType) modalType.textContent = typeVal || "Not specified";
      if (modalSizes) modalSizes.textContent = getSelectedSizeNames();
      if (modalModel) modalModel.textContent = preorderVal || "Goal Based";

      modal.showModal();
    });
  }

  closeModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (modal) modal.close();
    });
  });

  if (confirmBtn) {
    confirmBtn.addEventListener("click", function () {
      // Sync slides_data for edit mode if present
      const slidesDataInput = document.getElementById("slides_data");
      if (slidesDataInput) {
        const existingCloudinaryUrls = slidesData
          .map((s) => (typeof s === "string" ? s : s.src))
          .filter((url) => url && url.startsWith("https://res.cloudinary.com"));
        slidesDataInput.value = existingCloudinaryUrls.join(",");
      }

      // Sync time-based date if active
      const preorderSelect = document.getElementById("preorder");
      if (preorderSelect && preorderSelect.value === "1") {
        const dateInput = document.getElementById("preorderDate");
        const submitDate = document.getElementById("submitPreorderDate");
        if (dateInput && submitDate) {
          submitDate.value = dateInput.value;
        }
      }

      const form = document.getElementById("product-form");
      if (form) {
        form.submit();
      }
    });
  }
});

// -------------------- 6. Gallery Slide Rendering and Navigation --------------------
function renderSlides() {
  const slidesContainer = document.getElementById("slides-container");
  const thumbnailsContainer = document.getElementById("thumbnails");
  const currentSlideNum = document.getElementById("currentSlideNum");
  const totalSlidesNum = document.getElementById("totalSlidesNum");
  const uploadDropzone = document.getElementById("upload-dropzone");
  const uploadBtn = document.getElementById("upload-button");
  const deleteBtn = document.getElementById("delete-image-button");
  const prevBtn = document.querySelector(".gallery-nav-btn.prev-btn");
  const nextBtn = document.querySelector(".gallery-nav-btn.next-btn");

  if (!slidesContainer) return;

  slidesContainer.innerHTML = "";
  if (thumbnailsContainer) thumbnailsContainer.innerHTML = "";

  if (slidesData.length === 0) {
    if (uploadDropzone) uploadDropzone.style.display = "flex";
    if (uploadBtn) uploadBtn.style.display = "none";
    if (deleteBtn) deleteBtn.style.display = "none";
    if (prevBtn) prevBtn.style.display = "none";
    if (nextBtn) nextBtn.style.display = "none";
    if (currentSlideNum) currentSlideNum.textContent = "0";
    if (totalSlidesNum) totalSlidesNum.textContent = "0";
    return;
  }

  if (uploadDropzone) uploadDropzone.style.display = "none";
  if (uploadBtn) uploadBtn.style.display = "flex";
  if (deleteBtn) deleteBtn.style.display = "flex";
  if (prevBtn) prevBtn.style.display = slidesData.length > 1 ? "flex" : "none";
  if (nextBtn) nextBtn.style.display = slidesData.length > 1 ? "flex" : "none";

  if (slideIndex > slidesData.length) slideIndex = slidesData.length;
  if (slideIndex < 1) slideIndex = 1;

  slidesData.forEach((slide, index) => {
    const slideDiv = document.createElement("div");
    slideDiv.className = "mySlides fade";
    slideDiv.style.display = index + 1 === slideIndex ? "flex" : "none";

    const imgSrc = typeof slide === "string" ? slide : slide.src || slide;
    const img = document.createElement("img");
    img.src = imgSrc;
    img.alt = `Product photo ${index + 1}`;
    img.className = "mySlides__image";
    slideDiv.appendChild(img);

    slidesContainer.appendChild(slideDiv);

    if (thumbnailsContainer) {
      const thumbBtn = document.createElement("button");
      thumbBtn.type = "button";
      thumbBtn.className = `thumb-item-btn ${index + 1 === slideIndex ? "active" : ""}`;
      thumbBtn.setAttribute("aria-label", `View photo ${index + 1}`);
      thumbBtn.onclick = () => currentSlide(index + 1);

      const thumbImg = document.createElement("img");
      thumbImg.src = imgSrc;
      thumbImg.alt = `Thumbnail ${index + 1}`;
      thumbImg.className = "thumb-img";
      thumbBtn.appendChild(thumbImg);
      thumbnailsContainer.appendChild(thumbBtn);
    }
  });

  if (currentSlideNum) currentSlideNum.textContent = slideIndex;
  if (totalSlidesNum) totalSlidesNum.textContent = slidesData.length;
}

function plusSlides(n) {
  if (!slidesData.length) return;
  slideIndex += n;
  if (slideIndex > slidesData.length) slideIndex = 1;
  if (slideIndex < 1) slideIndex = slidesData.length;
  showSlides(slideIndex);
}

function currentSlide(n) {
  if (!slidesData.length) return;
  slideIndex = n;
  showSlides(slideIndex);
}

function showSlides(n) {
  const slides = document.querySelectorAll(".mySlides");
  const dots = document.querySelectorAll(".thumb-item-btn");
  const currentSlideNum = document.getElementById("currentSlideNum");

  if (!slides.length) return;
  if (n > slides.length) slideIndex = 1;
  if (n < 1) slideIndex = slides.length;

  slides.forEach((s) => (s.style.display = "none"));
  dots.forEach((d) => d.classList.remove("active"));

  if (slides[slideIndex - 1]) {
    slides[slideIndex - 1].style.display = "flex";
  }
  if (dots[slideIndex - 1]) {
    dots[slideIndex - 1].classList.add("active");
  }
  if (currentSlideNum) {
    currentSlideNum.textContent = slideIndex;
  }
}

function deleteCurrentSlide() {
  if (slidesData.length === 0) {
    alert("No photos to delete.");
    return;
  }

  const removed = slidesData[slideIndex - 1];
  if (removed && removed.filename) {
    for (let i = 0; i < dataTransfer.items.length; i++) {
      const file = dataTransfer.items[i].getAsFile();
      if (file && file.name === removed.filename) {
        dataTransfer.items.remove(i);
        break;
      }
    }
    const selectedImagesInput = document.getElementById("picture_urls");
    if (selectedImagesInput) {
      selectedImagesInput.files = dataTransfer.files;
    }
  }

  slidesData.splice(slideIndex - 1, 1);

  if (slideIndex > slidesData.length) {
    slideIndex = slidesData.length || 1;
  }

  renderSlides();
}
