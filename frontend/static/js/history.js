// History fetch and render logic

document.addEventListener('DOMContentLoaded', () => {
    const historyContainer = document.getElementById('history-container');
    if (!historyContainer) return;

    fetchHistory();
});

async function fetchHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        const container = document.getElementById('history-container');

        if (data.success && data.history.length > 0) {
            renderHistory(data.history, container);
        } else {
            container.innerHTML = `<div class="empty-msg">You have no booking history.</div>`;
        }
    } catch (error) {
        console.error('Error fetching history:', error);
        document.getElementById('history-container').innerHTML =
            `<div class="empty-msg">Failed to load booking history.</div>`;
    }
}

function renderHistory(bookings, container) {
    let html = `
    <table class="history-table">
        <thead>
            <tr>
                <th>Booking ID</th>
                <th>Tractor</th>
                <th>Location</th>
                <th>Duration</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
    `;

    bookings.forEach(booking => {
        html += `
            <tr>
                <td>#${booking.booking_id}</td>
                <td>${booking.tractor ? booking.tractor.tractor_model : 'Unknown'}</td>
                <td>${booking.delivery_location}</td>
                <td>${booking.start_date} to ${booking.end_date}</td>
                <td><span class="status-badge status-${booking.status ? booking.status.toLowerCase() : 'pending'}">${booking.status || 'Pending'}</span></td>
            </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}
