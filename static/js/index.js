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
let currentIdx = 0;
const slides = document.querySelectorAll('.vvi-slide');
const dots = document.querySelectorAll('.dot');

function showSlide(idx) {
    slides.forEach((slide, i) => {
        slide.classList.remove('active', 'exit');
        if (i < idx) {
            slide.classList.add('exit'); // Previous slides exit to the right
        }
        dots[i].classList.remove('active');
    });
    
    slides[idx].classList.add('active');
    dots[idx].classList.add('active');
}

function nextSlide() {
    currentIdx = (currentIdx + 1) % slides.length;
    showSlide(currentIdx);
}

function currentSlide(idx) {
    currentIdx = idx;
    showSlide(currentIdx);
}

// 6 Seconds auto-slide
setInterval(nextSlide, 6000);
