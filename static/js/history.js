document.addEventListener("DOMContentLoaded", function() {
    const toasts = document.querySelectorAll('.toast-message');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.transition = "opacity 0.5s ease";
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    });

    window.onclick = function(event) {
        const modal = document.getElementById("reportModal");
        if (event.target == modal) {
            closeReportModal();
        }
    }
});

function filterByMonth() {
    const selectedMonth = document.getElementById("monthFilter").value;
    const cards = document.querySelectorAll(".history-card");
    const noResultsMsg = document.getElementById("noResultsMessage");
    let visibleCards = 0;

    cards.forEach(card => {
        const dateString = card.getAttribute("data-date");
        if (selectedMonth === "all") {
            card.style.display = "flex";
            visibleCards++;
        } else {
            const dateObj = new Date(dateString);
            if (!isNaN(dateObj)) {
                if (dateObj.getMonth() == parseInt(selectedMonth)) {
                    card.style.display = "flex";
                    visibleCards++;
                } else {
                    card.style.display = "none";
                }
            } else {
                card.style.display = "flex";
                visibleCards++;
            }
        }
    });

    if (visibleCards === 0 && cards.length > 0) {
        noResultsMsg.style.display = "block";
    } else {
        noResultsMsg.style.display = "none";
    }
}

function shareRecord(aiResult, dateStr) {
    const shareData = {
        title: 'AarogyamScanAI Diagnostic Result',
        text: `Medical Scan Report:\nDate: ${dateStr}\nDiagnosis: ${aiResult}\n\nGenerated via Code_X_Elite AI.`,
    };

    if (navigator.share) {
        navigator.share(shareData).catch((error) => console.log('Error sharing', error));
    } else {
        navigator.clipboard.writeText(shareData.text).then(() => {
            alert("Result details copied to clipboard!");
        }).catch((err) => {
            alert("Failed to copy text: " + err);
        });
    }
}

// =========================================
// 3. FULL REPORT MODAL LOGIC (FIXED)
// =========================================
function openReportModal(imgSrc, patientName, uploadDate, result) {
    // BUG WAS HERE: ID is 'modalImage', not 'modalImg'
    document.getElementById("modalImage").src = imgSrc;
    
    document.getElementById("modalPatientName").textContent = patientName && patientName !== 'None' ? patientName : "Anonymous Patient";
    document.getElementById("modalDate").textContent = uploadDate;
    
    const resultElement = document.getElementById("modalResult");
    resultElement.textContent = result;
    
    if(result.toLowerCase().includes("normal") || result.toLowerCase().includes("low")) {
        resultElement.style.color = "#059669"; 
        resultElement.style.backgroundColor = "#dcfce7";
    } else {
        resultElement.style.color = "#dc2626"; 
        resultElement.style.backgroundColor = "#fee2e2";
    }

    document.getElementById("reportModal").style.display = "flex";
}

function closeReportModal() {
    document.getElementById("reportModal").style.display = "none";
}

function printModalReport() {
    window.print();
}
