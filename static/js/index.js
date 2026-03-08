document.addEventListener("DOMContentLoaded", function() {
    
    // Select all elements that need the fade-in effect
    const fadeElements = document.querySelectorAll('.js-scroll-fade');
    
    // Check if IntersectionObserver is supported by the browser
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    // Stop observing once the animation is complete
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        fadeElements.forEach(el => observer.observe(el));
    } else {
        // Fallback for older browsers: show elements immediately
        fadeElements.forEach(el => el.classList.add('is-visible'));
    }
});
