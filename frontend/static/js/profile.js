// Profile fetch and edit logic

document.addEventListener('DOMContentLoaded', () => {
    const profileContainer = document.getElementById('profile-container');
    const editForm = document.getElementById('edit-profile-form');
    const photoForm = document.getElementById('photo-upload-form');

    if (profileContainer || editForm) {
        fetchProfile();
        fetchIncomingRequests();
        fetchBookingStats();
    }

    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(editForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/api/profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();

                if (result.success) {
                    alert('Profile updated successfully!');
                    fetchProfile(); // Refresh Data
                } else {
                    alert(result.message || 'Failed to update profile.');
                }
            } catch (error) {
                console.error('Error updating profile:', error);
            }
        });
    }

    if (photoForm) {
        photoForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(photoForm);

            try {
                const response = await fetch('/api/upload_profile_photo', {
                    method: 'POST',
                    body: formData // DO NOT stringify or set content-type for FormData (browser handles boundaries)
                });
                const result = await response.json();

                if (result.success) {
                    alert('Photo uploaded successfully!');
                    fetchProfile(); // Refresh Data
                } else {
                    alert(result.message || 'Failed to upload photo.');
                }
            } catch (error) {
                console.error('Error uploading photo:', error);
            }
        });
    }
});

async function fetchProfile() {
    try {
        const response = await fetch('/api/profile');
        const data = await response.json();

        if (data.success) {
            populateProfile(data.user);
        } else {
            console.error('Failed to load profile.');
        }
    } catch (error) {
        console.error('Error fetching profile:', error);
    }
}

function populateProfile(user) {
    // Populate display fields if they exist
    const usernameEl = document.getElementById('display-username');
    const emailEl = document.getElementById('display-email');
    const addressEl = document.getElementById('display-address');
    const contactEl = document.getElementById('display-contact');
    const photoImg = document.getElementById('display-photo');

    if (usernameEl) usernameEl.textContent = user.username;
    // Also update sidebar username (profile.html uses display-username-2)
    const usernameEl2 = document.getElementById('display-username-2');
    if (usernameEl2) usernameEl2.textContent = user.username;
    if (emailEl) emailEl.textContent = user.email;

    if (user.profile) {
        if (addressEl) addressEl.textContent = user.profile.address || 'N/A';
        if (contactEl) contactEl.textContent = user.profile.contact_number || 'N/A';
        if (photoImg && user.profile.profile_photo) {
            photoImg.src = `/static/profile_photos/${user.profile.profile_photo}`;
        }
    }

    // Populate edit form fields if they exist
    const inputAddress = document.getElementById('input-address');
    const inputContact = document.getElementById('input-contact');

    if (user.profile) {
        if (inputAddress) inputAddress.value = user.profile.address || '';
        if (inputContact) inputContact.value = user.profile.contact_number || '';
    }
}

async function fetchIncomingRequests() {
    try {
        const response = await fetch('/api/owner/requests');
        const data = await response.json();
        const container = document.getElementById('incoming-requests-container');

        if (!container) return;

        if (data.success && data.requests.length > 0) {
            let html = '';
            data.requests.forEach(req => {
                html += `
                    <div class="request-item">
                        <p><strong>Tractor:</strong> ${req.tractor_model}</p>
                        <p><strong>Booker:</strong> ${req.booker_username}</p>
                        <p><strong>Address:</strong> ${req.booker_address}</p>
                        <p><strong>Proposed Dates:</strong> ${req.start_date} to ${req.end_date}</p>
                        <p><strong>Delivery Location:</strong> ${req.delivery_location}</p>
                        <div style="margin-top: 10px;">
                            <button class="action-btn btn-approve" onclick="respondToRequest('${req.booking_id}', 'approve')">Approve</button>
                            <button class="action-btn btn-reject" onclick="respondToRequest('${req.booking_id}', 'reject')">Reject</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p style="color: #777;">No pending requests at the moment.</p>';
        }
    } catch (error) {
        console.error('Error fetching requests:', error);
    }
}

async function fetchBookingStats() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        if (!data.success) return;

        const bookings = data.history;
        const today = new Date().toISOString().split('T')[0];

        const total = bookings.length;
        const active = bookings.filter(b => b.end_date >= today && b.status !== 'Rejected').length;
        const completed = bookings.filter(b => b.end_date < today).length;

        const totalEl = document.getElementById('total-bookings');
        const activeEl = document.getElementById('active-bookings');
        const completedEl = document.getElementById('completed-bookings');

        if (totalEl) totalEl.textContent = total;
        if (activeEl) activeEl.textContent = active;
        if (completedEl) completedEl.textContent = completed;
    } catch (error) {
        console.error('Error fetching booking stats:', error);
    }
}


async function respondToRequest(bookingId, action) {
    if (!confirm(`Are you sure you want to ${action} this request?`)) return;

    try {
        const response = await fetch(`/api/owner/respond/${bookingId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action })
        });
        const result = await response.json();

        alert(result.message);
        if (result.success) {
            fetchIncomingRequests(); // Refresh the requests list
            // If the user happens to have their own history table on the same page, refresh it
            if (typeof fetchHistory === 'function') {
                fetchHistory();
            }
        }
    } catch (error) {
        console.error('Error responding to request:', error);
        alert('An error occurred. Please try again.');
    }
}
