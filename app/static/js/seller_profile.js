// seller_profile.js

// File input and button handling
document.getElementById('uploadButton').addEventListener('click', function () {
    document.getElementById('fileInput').click(); // Trigger file input click
  });
  
  // Preview the uploaded file
  document.getElementById('fileInput').addEventListener('change', function (event) {
    const file = event.target.files[0];
    
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        // Display the selected image in the profile picture preview
        document.getElementById('profilePicturePreview').src = e.target.result;
      };
      reader.readAsDataURL(file);
  
      // Optional: Upload the file to Cloudinary
      myWidget.open(); // Opens the Cloudinary widget
    }
  });
  
  // Cloudinary Upload Widget
  var myWidget = cloudinary.createUploadWidget(
    {
      cloudName: 'YOUR_CLOUD_NAME',  // replace with your cloud name
      uploadPreset: 'YOUR_UPLOAD_PRESET',  // replace with your upload preset
      sources: ['local', 'camera'],
      multiple: false,
      cropping: true,
      croppingAspectRatio: 1,
      clientAllowedFormats: ['jpg', 'png', 'gif']
    },
    function (error, result) {
      if (!error && result && result.event === 'success') {
        // Update profile picture after successful upload
        document.getElementById('profilePicturePreview').src = result.info.secure_url;
      }
    }
  );
  