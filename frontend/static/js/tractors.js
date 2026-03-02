// Fetch tractors and handle tractor view logic

document.addEventListener('DOMContentLoaded', () => {
    const tractorGrid = document.querySelector('.tractor-grid');
    const searchForm = document.querySelector('.search-bar');

    if (!tractorGrid) return; // Only run on tractorview page

    // Initial fetch
    fetchTractors();

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(searchForm);
            const params = new URLSearchParams(formData).toString();
            fetchTractors(params);
        });
    }
});

async function fetchTractors(queryParams = '') {
    const url = queryParams ? `/api/tractors?${queryParams}` : '/api/tractors';
    const grid = document.querySelector('.tractor-grid');

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.tractors.length > 0) {
            renderTractors(data.tractors, grid);
        } else {
            grid.innerHTML = `<div class="empty-msg">No tractors found.</div>`;
        }
    } catch (error) {
        console.error('Error fetching tractors:', error);
        grid.innerHTML = `<div class="empty-msg">Failed to load tractors.</div>`;
    }
}

function renderTractors(tractors, container) {
    container.innerHTML = tractors.map(tractor => `
        <div class="tractor-card">
            <img src="${tractor.photo ? `/static/uploads/${tractor.photo}` : 'https://via.placeholder.com/400x200?text=No+Image'}" alt="Tractor Image">
            <div class="tractor-info">
                <h3>${tractor.tractor_model}</h3>
                <p><strong>Owner:</strong> ${tractor.email}</p>
                <p><strong>Location:</strong> ${tractor.location}</p>
                <p><strong>Price:</strong> ₹${tractor.price}/day</p>
                
                ${tractor.available
            ? `<a href="/book/${tractor.tractor_id}" class="book-btn">Book Now</a>`
            : `<span class="book-btn disabled">Booked</span>`}
            </div>
        </div>
    `).join('');
}
