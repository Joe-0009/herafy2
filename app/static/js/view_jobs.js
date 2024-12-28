// Function to open job modal
function openJobModal(jobId) {
    fetch(`/job/job_details/${jobId}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        document.getElementById('jobModalContent').innerHTML = html;
        $('#jobModal').modal('show');
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('jobModalContent').innerHTML = `
            <div class="alert alert-danger" role="alert">
                An error occurred while loading job details. Please try again later.
                <br>Error details: ${error.message}
            </div>`;
        $('#jobModal').modal('show');
    });
}

// Function to show image modal
function showImageModal(imageSrc) {
    document.getElementById('modalImage').src = imageSrc;
    $('#imageModal').modal('show');
}

// Event listener for search form submission
document.getElementById('search-job-form').addEventListener('submit', () => {
    document.getElementById('loading-spinner').style.display = 'block';
});

// Background image rotation
const backgrounds = [
    'url("/static/images/job_search.jpg")',
    'url("/static/images/job_search1.jpg")',
    'url("/static/images/job_search2.jpg")',
    'url("/static/images/job_search3.jpg")'
];
let currentBg = 0;

function changeBackground() {
    currentBg = (currentBg + 1) % backgrounds.length;
    document.querySelector('.search-job-container').style.backgroundImage = backgrounds[currentBg];
    document.querySelectorAll('.indicator').forEach((indicator, index) => {
        indicator.classList.toggle('active', index === currentBg);
    });
}

setInterval(changeBackground, 5000);

// Initialize tooltips and popovers if using Bootstrap
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
});