   document.querySelectorAll('.dropbtn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const menu = this.nextElementSibling;
      menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
    });
  });
  // Show modal on page load
document.addEventListener("DOMContentLoaded", function() {
    if(modal){
        const span = modal.querySelector(".close");
        modal.style.display = "block";
        span.onclick = function() {
            modal.style.display = "none";
        }
        window.onclick = function(event) {
            if(event.target == modal){
                modal.style.display = "none";
            }
        }
    }
});
console.log("Aarogyam_ScanAI Network Loaded");
document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('menu-button');
    const navMenu = document.getElementById('nav-menu');
    const body = document.body;
    
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
    
    // Optional: Close menu when a link is clicked
    const navLinks = navMenu.querySelectorAll('a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (navMenu.classList.contains('show')) {
                navMenu.classList.remove('show');
       const span = modal.querySelector(".close");

  modal.style.display = "block"; // Show modal
         overlay.classList.remove('show');
            }
        });
    });
});
