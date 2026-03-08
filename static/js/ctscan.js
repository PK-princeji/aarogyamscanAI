document.addEventListener("DOMContentLoaded", function() {
    
    // Intersection Observer for Scroll Animations
    const revealElements = document.querySelectorAll(".reveal");
    const observerOptions = {
        root: null,
        rootMargin: "0px 0px -100px 0px",
        threshold: 0.1
    };

    const revealCallback = function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                if(entry.target.classList.contains('stats-section')) {
                    startCounters();
                }
                observer.unobserve(entry.target);
            }
        });
    };

    const scrollObserver = new IntersectionObserver(revealCallback, observerOptions);
    revealElements.forEach(el => {
        scrollObserver.observe(el);
    });

    // Number Counter Animation Logic
    let countersStarted = false;
    function startCounters() {
        if (countersStarted) return;
        countersStarted = true;
        
        const counters = document.querySelectorAll('.stat-number');
        const speed = 150; 
        
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText;
                const inc = target / speed;
                
                if (count < target) {
                    counter.innerText = Math.ceil(count + inc);
                    setTimeout(updateCount, 15);
                } else {
                    counter.innerText = target;
                }
            };
            updateCount();
        });
    }
});
