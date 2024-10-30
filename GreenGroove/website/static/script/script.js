
/* To preview image when creating event */
function previewImage(event) {
    var imagePreview = document.getElementById('imagePreview');
    var file = event.target.files[0];
    
    if (file) {
      var reader = new FileReader();
      reader.onload = function(e) {
        imagePreview.innerHTML = '<img src="' + e.target.result + '" alt="Image preview" style="max-width: 100%; max-height: 100%; border-radius: 8px;">';
      }
      reader.readAsDataURL(file); // Convert image to base64 string
    } else {
      imagePreview.innerHTML = '<span>No image selected</span>';
    }
  }


  