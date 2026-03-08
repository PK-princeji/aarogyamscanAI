document.addEventListener("DOMContentLoaded", function() {
    // Advanced Intersection Observer for Scroll Animations
    const revealElements = document.querySelectorAll(".reveal");
    
    const observerOptions = {
        root: null,
        rootMargin: "0px 0px -100px 0px", // triggers cleanly before entering view
        threshold: 0.1
    };

    const revealCallback = function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                // Stop observing once animated
                observer.unobserve(entry.target);
            }
        });
    };

    const scrollObserver = new IntersectionObserver(revealCallback, observerOptions);
    revealElements.forEach(el => {
        scrollObserver.observe(el);
    });
});
