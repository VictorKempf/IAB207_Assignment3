document.addEventListener('DOMContentLoaded', function() {
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    const dropdownButton = document.getElementById('locationDropdown');
    
    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            // Update the dropdown button text
            const selectedValue = this.textContent.trim();
            dropdownButton.textContent = selectedValue;
        });
    });
});



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

// JavaScript to update dropdown button with selected value
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default link behavior
            const selectedValue = this.getAttribute('data-value');
            // Update the button text with the selected value for both dropdowns
            document.querySelectorAll('[id^=quantityDropdown]').forEach(button => {
                button.textContent = `${selectedValue}`;
            });
        });
    });
});

  