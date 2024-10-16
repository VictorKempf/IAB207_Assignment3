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
/* Picking date for event */
  $(document).ready(function() {
          // Initialize datepicker
          $('#date').datepicker({
              format: 'dd/mm/yyyy',
              autoclose: true,
              todayHighlight: true
          });

          // Open datepicker when calendar icon is clicked
          $('#calendarIcon').on('click', function() {
              $('#date').datepicker('show');
          });
    });



   document.addEventListener('DOMContentLoaded', function() {
    const modal = new bootstrap.Modal(document.getElementById('quickViewModal'));

    // Add event listener to all "Quick View" buttons
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(button => {
      button.addEventListener('click', function() {
        const eventId = this.getAttribute('data-event-id');
        loadEventDetails(eventId);
      });
    });

    // Function to load event details into the modal
    function loadEventDetails(eventId) {
      const eventDetails = {
        1: {
          name: "Event Name",
          description: "Full description of the event.",
          date: "2024-09-15",
          time: "20:00",
          venue: "Event Venue",
          price: "$50"
        }
      };

      const details = eventDetails[eventId];
      if (details) {
        document.getElementById('modalEventDetails').innerHTML = `
          <h6>Name: ${details.name}</h6>
          <p>Description: ${details.description}</p>
          <p>Date: ${details.date}</p>
          <p>Time: ${details.time}</p>
          <p>Venue: ${details.venue}</p>
          <p>Price: ${details.price}</p>
        `;
      }
    }

    // Handle booking form submission
    document.getElementById('bookingForm').addEventListener('submit', function(event) {
      event.preventDefault();
      const numTickets = document.getElementById('numTickets').value;
      alert(`Booked ${numTickets} tickets!`);
      // Add actual booking logic here
    });
  });

  

 // Sample data for 8 events (same data for both containers)
const events = [
    { id: 1, title: "BrisBeats Festival", dateTime: "Sat, 14 Sept, 7:00PM", venue: "Brisbane Parklands", price: "$59", image: "static/img/aranxa-esteve-pOXHU0UEDcg-unsplash.jpg", status: "Available" },
    { id: 2, title: "Synthwave Spectacular", dateTime: "Sun, 15 Sept, 8:00PM", venue: "Main Hall", price: "$75", image: "static/img/hanny-naibaho-aWXVxy8BSzc-unsplash.jpg", status: "Sold Out" },
    { id: 3, title: "Outdoors Symphony", dateTime: "Mon, 16 Sept, 6:00PM", venue: "Outdoor Arena", price: "$45", image: "static/img/martin-robles-EKpByvjvioU-unsplash.jpg", status: "Available" },
    { id: 4, title: "Jazz Night Extravaganza", dateTime: "Tue, 17 Sept, 9:00PM", venue: "Main Hall", price: "$80", image: "static/img/jens-thekkeveettil-dBWvUqBoOU8-unsplash.jpg", status: "Sold Out" },
    { id: 5, title: "Classical Music Showcase", dateTime: "Wed, 18 Sept, 5:00PM", venue: "Expo Center", price: "$60", image: "static/img/manuel-nageli-NsgsQjHA1mM-unsplash.jpg", status: "Available" },
    { id: 6, title: "Electronic Beats Festival", dateTime: "Thu, 19 Sept, 8:00PM", venue: "Open Air Theater", price: "$55", image: "static/img/antoine-j-nCQLFziJ3Bk-unsplash.jpg", status: "Sold Out" },
    { id: 7, title: "Indie Music Showcase", dateTime: "Fri, 20 Sept, 7:00PM", venue: "City Hall", price: "$70", image: "static/img/old-youth-PBIqpZ4gD48-unsplash.jpg", status: "Available" },
    { id: 8, title: "Rock Legends Live", dateTime: "Sat, 21 Sept, 9:00PM", venue: "Art Center", price: "$85", image: "static/img/rocco-dipoppa-_uDj_lyPVpA-unsplash.jpg", status: "Sold Out" },
];

// Function to generate event cards for a specific container
function generateEventCards(containerId, eventSubset) {
    const container = document.getElementById(containerId);
    let htmlContent = '';

    // Loop through the subset of events
    eventSubset.forEach(event => {
        htmlContent += `
            <div class="col-md-3 mb-3">
                <div class="rectangle">
                    <div class="card-img-container">
                        <img src="${event.image}" alt="Event Image">
                        <button type="button" class="quick-view-btn" data-bs-toggle="modal" data-bs-target="#quickViewModal" data-event-id="${event.id}">
                            Quick View
                        </button>
                    </div>
                </div>
                <div class="row align-items-center">
                    <div class="col-6 text-start">
                        <h4 class="mb-0"><a href="eventDetails.html" style="text-decoration: none; color: #333">${event.title}</a></h4>
                    </div>
                    <div class="col-6 d-flex justify-content-end">
                        <button class="status-button">${event.status}</button>
                    </div>
                </div>
                <div class="popular-events-container row align-items-center">
                    <div class="col-10 text-start">
                        <p class="mb-0">${event.dateTime}</p>
                    </div>
                    <div class="col-10 text-start">
                        <p class="mb-0" style="font-style: italic;">${event.venue}</p>
                    </div>
                    <div class="col-10 text-start">
                        <p class="mb-0">${event.price}</p>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = htmlContent;
}

// Call the function to generate the event cards for both containers
generateEventCards('eventsContainer', events.slice(0, 4)); // First 4 events
generateEventCards('eventsContainer2', events.slice(4, 8)); // Last 4 events

// Update modal content when "Quick View" button is clicked for both modals
document.addEventListener('click', function(event) {
    if (event.target.matches('.quick-view-btn')) {
        const eventId = event.target.getAttribute('data-event-id');
        const selectedEvent = events.find(e => e.id == eventId);

        // Determine which modal to update based on the button clicked
        const modalId = event.target.closest('.modal').id;
        const prefix = modalId === 'quickViewModal' ? '' : '2';

        // Update modal with the selected event details
        document.getElementById(`eventName${prefix}`).textContent = selectedEvent.title;
        document.getElementById(`eventStatus${prefix}`).textContent = selectedEvent.status;
        document.getElementById(`eventVenue${prefix}`).textContent = selectedEvent.venue;
        document.getElementById(`eventDateTime${prefix}`).textContent = selectedEvent.dateTime;
        document.getElementById(`eventPrice${prefix}`).textContent = selectedEvent.price;
        document.getElementById(`eventImage${prefix}`).setAttribute('src', selectedEvent.image);
        document.getElementById(`eventDescription${prefix}`).textContent = "This is a brief description of " + selectedEvent.title;
    }
});

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

  