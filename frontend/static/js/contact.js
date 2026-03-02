/**
 * contact.js - Handles contact form submission via /api/contact
 */

document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contact-form');
    const successMessage = document.querySelector('.success-message');

    if (!contactForm) return;

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData.entries());

        const submitBtn = contactForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        }

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();

            if (result.success) {
                if (successMessage) {
                    successMessage.textContent = result.message || 'Message sent! We\'ll get back to you soon.';
                    successMessage.style.display = 'block';
                }
                contactForm.reset();
                setTimeout(() => {
                    if (successMessage) successMessage.style.display = 'none';
                }, 5000);
            } else {
                alert(result.message || 'Failed to send message. Please try again.');
            }
        } catch (error) {
            console.error('Error submitting contact form:', error);
            alert('An error occurred. Please try again later.');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
            }
        }
    });
});
