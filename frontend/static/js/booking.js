// Booking logic

document.addEventListener('DOMContentLoaded', () => {
    const bookForm = document.getElementById('booking-form');
    if (!bookForm) return;

    bookForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(bookForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.success) {
                alert('Booking successful!');
                window.location.href = '/history';
            } else {
                alert(result.message || 'Failed to book tractor.');
            }
        } catch (error) {
            console.error('Error booking tractor:', error);
            alert('An error occurred during booking.');
        }
    });
});
