document.addEventListener("DOMContentLoaded", function() {
    
    // 1. INTERSECTION OBSERVER FOR SCROLL ANIMATIONS
    const revealElements = document.querySelectorAll(".reveal");
    const observerOptions = {
        root: null,
        rootMargin: "0px 0px -150px 0px",
        threshold: 0.1
    };

    const revealCallback = function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                
                // Trigger counter animation if stats section is revealed
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

    // 2. NUMBER COUNTER ANIMATION LOGIC
    let countersStarted = false;
    function startCounters() {
        if (countersStarted) return;
        countersStarted = true;
        
        const counters = document.querySelectorAll('.stat-number');
        const speed = 200; // Lower is faster
        
        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText;
                const inc = target / speed;
                
                if (count < target) {
                    counter.innerText = Math.ceil(count + inc);
                    setTimeout(updateCount, 10);
                } else {
                    counter.innerText = target;
                }
            };
            updateCount();
        });
    }

    // 3. FAQ ACCORDION LOGIC
    const faqQuestions = document.querySelectorAll('.faq-question');
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const answer = question.nextElementSibling;
            
            // Close all other open answers
            document.querySelectorAll('.faq-answer').forEach(ans => {
                if(ans !== answer) {
                    ans.style.maxHeight = null;
                    ans.previousElementSibling.classList.remove('active');
                }
            });

            // Toggle current answer
            question.classList.toggle('active');
            if (answer.style.maxHeight) {
                answer.style.maxHeight = null;
            } else {
                // Set max height dynamically based on scrollHeight for smooth transition
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });
    });
});
