// script.js
const buttons = document.querySelectorAll('.size-btn');
const selectedSizesInput = document.getElementById('selectedSizes');
const selectedImagesInput = document.getElementById('picture_urls');
const usedImagesInput = document.getElementById("pictureUpload");

buttons.forEach(button => {
  button.addEventListener('click', () => {
    // Toggle active class
    button.classList.toggle('active');
    
    // Update the hidden input with the selected sizes
    updateSelectedSizes();
  });
});

function updateSelectedSizes() {
  // Gather all active buttons
  const selectedSizes = Array.from(document.querySelectorAll('.size-btn.active'))
    .map(button => button.dataset.size);

  // Join the sizes into a comma-separated string and update the hidden input
  selectedSizesInput.value = selectedSizes.join(',');
}


let slideIndex = 1;
let slidesData = [];
const dataTransfer = new DataTransfer();

// Function to copy files from one input to another
function updateSelectedImages(sourceInput, targetInput) {
  // Get files from the source input
  const files = sourceInput.files;

  // Append each file to the DataTransfer object
  for (let i = 0; i < files.length; i++) {
    dataTransfer.items.add(files[i]);
  }

  console.log(dataTransfer)

  // Assign the new FileList to the target input
  targetInput.files = dataTransfer.files;
}

// Image Gallery Functions
document.getElementById("pictureUpload").addEventListener("change", function() {
  const files = this.files;

  // Check if exactly 3 images are selected
  if (files.length > 3) {
    alert("You must select exactly 3 images.");
    this.value = '';  // Clear the input field if not exactly 3 images
    return;
  }

  // Check if all selected files have valid image extensions
  const validExtensions = ['.jpg', '.jpeg', '.png', '.webp'];
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const fileName = file.name.toLowerCase();

    // Check if file extension is valid
    const isValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
    if (!isValidExtension) {
      alert("Only image files with extensions .jpg, .jpeg, .png, or .webp are allowed.");
      this.value = '';  // Clear the input field
      return;
    }
  }

  // Check if there are already 3 images uploaded
  if (slidesData.length >= 3) {
    alert("You can only upload a maximum of 3 images.");
    this.value = '';  // Clear the file input to prevent further selection
    return;
  }

  // Check if the combined total of picked and uploaded is bigger than 3
  if (files.length + slidesData.length > 3) {
    alert("You must only have 3 uploaded images.");
    this.value = '';  // Clear the file input to prevent further selection
    return;
  }

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const fileName = file.name;  // Get the raw filename

    const reader = new FileReader();
    reader.onload = function(e) {
      const imageSrc = e.target.result;
      slidesData.push({ src: imageSrc, filename: fileName });
      renderSlides();
    };
    reader.readAsDataURL(files[i]);
  }
  // Change the top of the upload button after images are uploaded
  document.querySelector(".product__image-wrapper").style.alignItems = "end";
  document.querySelector(".product__image-wrapper").style.justifyItems = "start";
  document.querySelector("#upload-button").style.transform = "scale(0.4)";
  document.querySelector("#upload-button__description").style.display = "none";
  document.querySelector("#delete-image-button").style.display = "grid";

  updateSelectedImages(usedImagesInput, selectedImagesInput);
});

// Function to render slides and thumbnails
function renderSlides() {
  const slidesContainer = document.getElementById("slides-container");
  const thumbnailsContainer = document.getElementById("thumbnails");

  slidesContainer.innerHTML = '';
  thumbnailsContainer.innerHTML = '';

  slidesData.forEach((slide, index) => {
    // Create slide
    const slideDiv = document.createElement("div");
    slideDiv.className = "mySlides";
    if (index + 1 === slideIndex) slideDiv.style.display = "flex"; // Show current slide

    const numberText = document.createElement("div");
    numberText.className = "numbertext";
    numberText.textContent = `${index + 1} / ${slidesData.length}`;
    slideDiv.appendChild(numberText);

    const img = document.createElement("img");
    img.src = slide.src;
    img.className = "mySlides__image";  // Added new class here
    slideDiv.appendChild(img);

    slidesContainer.appendChild(slideDiv);

    // Create thumbnail
    const thumbDiv = document.createElement("div");
    thumbDiv.className = "column";
    const thumbImg = document.createElement("img");
    thumbImg.src = slide.src;
    thumbImg.className = "demo cursor";
    thumbImg.onclick = () => currentSlide(index + 1);
    thumbDiv.appendChild(thumbImg);
    thumbnailsContainer.appendChild(thumbDiv);
  });

  showSlides(slideIndex);
}

// Navigate to the next or previous slide
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Set the current slide
function currentSlide(n) {
  slideIndex = n;
  showSlides(slideIndex);
}

// Show the current slide
function showSlides(n) {
  const slides = document.getElementsByClassName("mySlides");
  const dots = document.getElementsByClassName("demo");

  if (n > slidesData.length) slideIndex = 1;
  if (n < 1) slideIndex = slidesData.length;

  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (let i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  if (slides[slideIndex - 1]) slides[slideIndex - 1].style.display = "flex";
  if (dots[slideIndex - 1]) dots[slideIndex - 1].className += " active";
}

function removeFileFromDataTransfer(dataTransfer, filenameToRemove) {
  // Loop through the DataTransfer items
  for (let i = 0; i < dataTransfer.items.length; i++) {
    const file = dataTransfer.items[i].getAsFile();

    // Check if the filename matches the one to remove
    if (file.name === filenameToRemove) {
      // Remove the file from the DataTransfer object
      dataTransfer.items.remove(i);
      break; // Exit the loop after removing the file
    }
  }
}

// Delete the current slide
function deleteCurrentSlide() {
  if (slidesData.length > 0) {
    // Get the filename of the current slide
    const currentFilename = slidesData[slideIndex - 1].filename;
    
    // Remove the current slide from slidesData
    slidesData.splice(slideIndex - 1, 1);  // Remove the current image data
    
    // Adjust the slideIndex if necessary
    if (slideIndex > slidesData.length) {
      slideIndex = slidesData.length;  // If we're at the end, go back to the last slide
    }

    removeFileFromDataTransfer(dataTransfer, currentFilename);

    // Re-render the slides
    renderSlides();

    // If there are no slides left
    if (slidesData.length === 0) {
      // Reset the upload button style
      document.querySelector(".product__image-wrapper").style.alignItems = "center";
      document.querySelector(".product__image-wrapper").style.justifyItems = "center";
      document.querySelector("#upload-button").style.transform = "scale(1)";
      document.querySelector("#upload-button__description").style.display = "block";
      document.querySelector("#delete-image-button").style.display = "none";
    }
  } else {
    alert("No more images to delete.");
  }
}