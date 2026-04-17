console.log("Aarogyam_ScanAI Network Loaded");

document.addEventListener("DOMContentLoaded", function() {
    
    // ==========================================
    // 1. Dropdown Menu Logic
    // ==========================================
    document.querySelectorAll('.dropbtn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const menu = this.nextElementSibling;
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        });
    });

    // ==========================================
    // 2. Modal Logic (ERROR FIXED HERE)
    // ==========================================
    // यहाँ HTML से modal को सेलेक्ट किया गया है (अगर आपकी HTML में ID कुछ और है, तो 'myModal' को बदल लेना)
    const modal = document.getElementById("myModal"); 
    
    if(modal) {
        const span = modal.querySelector(".close");
        modal.style.display = "block"; // Show modal on page load
        
        if (span) {
            span.onclick = function() {
                modal.style.display = "none";
            }
        }
        
        window.onclick = function(event) {
            if(event.target == modal){
                modal.style.display = "none";
            }
        }
    }

    // ==========================================
    // 3. Mobile Nav Menu & Overlay Logic
    // ==========================================
    const menuButton = document.getElementById('menu-button');
    const navMenu = document.getElementById('nav-menu');
    const body = document.body;
    
    if (menuButton && navMenu) {
        // Create and append the overlay element to the body
        const overlay = document.createElement('div');
        overlay.classList.add('overlay');
        body.appendChild(overlay);

        menuButton.addEventListener('click', function() {
            navMenu.classList.toggle('show');
            overlay.classList.toggle('show');
        });

        overlay.addEventListener('click', function() {
            navMenu.classList.remove('show');
            overlay.classList.remove('show');
        });
        
        // Close menu when a link is clicked
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (navMenu.classList.contains('show')) {
                    navMenu.classList.remove('show');
                    overlay.classList.remove('show');
                }
            });
        });
    }
});