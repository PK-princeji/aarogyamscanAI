document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Scroll Reveal Animations
    const revealElements = document.querySelectorAll(".reveal");
    const observerOptions = { root: null, rootMargin: "0px 0px -100px 0px", threshold: 0.1 };
    const revealCallback = function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                observer.unobserve(entry.target);
            }
        });
    };
    const scrollObserver = new IntersectionObserver(revealCallback, observerOptions);
    revealElements.forEach(el => scrollObserver.observe(el));

    // 2. TRUE 3D Tilt Effect on Team Cards
    const cards = document.querySelectorAll('.team-member-card');
    
    // Only apply on fine-pointer devices (desktop) for performance
    if (window.matchMedia("(pointer: fine)").matches) {
        cards.forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                // Tilt logic: max 8 degrees
                const rotateX = ((y - centerY) / centerY) * -8;
                const rotateY = ((x - centerX) / centerX) * 8;
                
                // Apply rotation and Z-translation for depth
                card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
            });

            // Reset on mouseleave
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'rotateX(0) rotateY(0) translateZ(0)';
            });
        });
    }

    // 3. Optional: Background Particle Effect
    const particleContainer = document.getElementById('particle-container');
    if (particleContainer && window.matchMedia("(pointer: fine)").matches) {
        // Simple particle system without canvas
        for (let i = 0; i < 40; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4}px;
                height: ${Math.random() * 4}px;
                background: rgba(0, 240, 255, ${Math.random() * 0.3 + 0.1});
                left: ${Math.random() * 100}vw;
                top: ${Math.random() * 200}vh;
                border-radius: 50%;
                z-index: -1;
                pointer-events: none;
                animation: float-up ${Math.random() * 10 + 10}s linear infinite;
            `;
            particleContainer.appendChild(particle);
        }
    }
});

// Particle floating animation defined globally
const style = document.createElement('style');
style.innerHTML = `
    @keyframes float-up {
        0% { transform: translateY(0); opacity: 0; }
        10% { opacity: 0.5; }
        90% { opacity: 0.5; }
        100% { transform: translateY(-500px); opacity: 0; }
    }
`;
document.head.appendChild(style);
