document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Advanced Intersection Observer with threshold mapping
    const revealElements = document.querySelectorAll(".reveal");
    const observerOptions = {
        root: null,
        rootMargin: "0px 0px -120px 0px",
        threshold: 0.15
    };

    const revealCallback = function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                
                // Trigger counter animation precisely when stats are visible
                if(entry.target.classList.contains('stats-section')) {
                    startCounters();
                }
                // Unobserve for performance after animation
                observer.unobserve(entry.target);
            }
        });
    };

    const scrollObserver = new IntersectionObserver(revealCallback, observerOptions);
    revealElements.forEach(el => {
        scrollObserver.observe(el);
    });

    // 2. High-Performance Number Counter Animation
    let countersStarted = false;
    function startCounters() {
        if (countersStarted) return;
        countersStarted = true;
        
        const counters = document.querySelectorAll('.stat-number');
        // Different speeds for different visual impacts
        const speed = 120; 
        
        counters.forEach(counter => {
            const updateCount = () => {
                const target = parseFloat(counter.getAttribute('data-target'));
                const count = parseFloat(counter.innerText);
                // Calculate increment dynamically
                const inc = target / speed;
                
                if (count < target) {
                    // Check if it's a decimal number (like 99.8)
                    if(target % 1 !== 0) {
                        counter.innerText = (count + inc).toFixed(1);
                    } else {
                        counter.innerText = Math.ceil(count + inc);
                    }
                    // Request animation frame is smoother than setTimeout
                    requestAnimationFrame(updateCount);
                } else {
                    counter.innerText = target;
                }
            };
            updateCount();
        });
    }

    // 3. Smooth FAQ Accordion Logic
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const answer = question.nextElementSibling;
            
            // Close all other open answers smoothly
            document.querySelectorAll('.faq-answer').forEach(ans => {
                if(ans !== answer && ans.style.maxHeight) {
                    ans.style.maxHeight = null;
                    ans.previousElementSibling.classList.remove('active');
                }
            });

            // Toggle current answer
            question.classList.toggle('active');
            if (answer.style.maxHeight) {
                answer.style.maxHeight = null;
            } else {
                // Calculate exact height needed for smooth CSS transition
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });
    });

    // 4. Parallax Effect on Hero Image based on mouse movement
    const heroSection = document.querySelector('.hero-section');
    const heroImage = document.querySelector('.hero-image img');
    
    if(heroSection && heroImage) {
        heroSection.addEventListener('mousemove', (e) => {
            const xAxis = (window.innerWidth / 2 - e.pageX) / 40;
            const yAxis = (window.innerHeight / 2 - e.pageY) / 40;
            heroImage.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
        });

        // Reset transform on mouse leave
        heroSection.addEventListener('mouseleave', () => {
            heroImage.style.transform = `rotateY(-10deg) rotateX(5deg)`;
        });
    }
});
