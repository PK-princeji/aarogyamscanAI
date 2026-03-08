import os

base_dir = r"D:\final_year_project\code_X_Elite\aarogyamScanAi"

# Files to update
files_to_delete = [
    os.path.join(base_dir, "templates", "history.html"),
    os.path.join(base_dir, "static", "css", "history.css"),
    os.path.join(base_dir, "static", "js", "history.js")
]

# ==========================================
# 1. HTML CODE (history.html)
# ==========================================
html_content = """{% extends "base.html" %}

{% block head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/history.css') }}">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
{% endblock %}

{% block content %}
<main class="history-dashboard">
    
    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <div class="toast-container" id="toast-container">
        {% for category, msg in messages %}
            <div class="toast-message {{ category }}">
                <i class="fas {% if category == 'error' %}fa-exclamation-triangle{% elif category == 'success' %}fa-check-circle{% else %}fa-info-circle{% endif %}"></i>
                <span>{{ msg }}</span>
                <button class="close-toast" onclick="this.parentElement.style.display='none';">&times;</button>
            </div>
        {% endfor %}
        </div>
    {% endif %}
    {% endwith %}

    <div class="history-header">
        <div class="header-title">
            <h2><i class="fas fa-folder-open"></i> Diagnostic History</h2>
            <p>Manage, share, and view full clinical reports of your past scans.</p>
        </div>
        
        <div class="filter-container">
            <label for="monthFilter"><i class="fas fa-filter"></i> Sort by Month:</label>
            <div class="custom-select">
                <select id="monthFilter" onchange="filterByMonth()">
                    <option value="all">All Months</option>
                    <option value="0">January</option>
                    <option value="1">February</option>
                    <option value="2">March</option>
                    <option value="3">April</option>
                    <option value="4">May</option>
                    <option value="5">June</option>
                    <option value="6">July</option>
                    <option value="7">August</option>
                    <option value="8">September</option>
                    <option value="9">October</option>
                    <option value="10">November</option>
                    <option value="11">December</option>
                </select>
                <i class="fas fa-chevron-down select-icon"></i>
            </div>
        </div>
    </div>

    {% if history %}
        <div class="history-grid" id="historyGrid">
            {% for scan in history %}
                <div class="history-card" data-date="{{ scan['upload_date']|e }}">
                    
                    <div class="card-image">
                        {% if scan['user_email'] and scan['filename'] %}
                            <img src="{{ url_for('static', filename='reports/' ~ scan['user_email'] ~ '/' ~ scan['filename']) }}" 
                                 alt="Medical Scan" 
                                 class="history-img" loading="lazy"
                                 onerror="this.onerror=null; this.src='https://via.placeholder.com/400x300?text=Image+Not+Found';">
                        {% else %}
                            <div class="img-placeholder">
                                <i class="fas fa-image-slash"></i>
                                <span>Image Data Missing</span>
                            </div>
                        {% endif %}
                    </div>

                    <div class="card-content">
                        <div class="scan-date">
                            <i class="fas fa-calendar-day"></i> {{ scan['upload_date']|e }}
                        </div>
                        
                        <div class="scan-result">
                            <strong>AI Diagnosis:</strong> 
                            <span class="ai-badge result-{{ scan['ai_result']|lower|replace(' ', '-')|replace('(', '')|replace(')', '')|replace('%', '')|e }}">
                                {{ scan['ai_result']|e }}
                            </span>
                        </div>
                        
                        <div class="card-actions">
                            <button type="button" class="btn-action btn-view" 
                                    onclick="openReportModal('{{ url_for('static', filename='reports/' ~ scan['user_email'] ~ '/' ~ scan['filename']) }}', '{{ scan['user_name']|e }}', '{{ scan['upload_date']|e }}', '{{ scan['ai_result']|e }}')">
                                <i class="fas fa-eye"></i> View
                            </button>

                            <button type="button" class="btn-action btn-share" 
                                    onclick="shareRecord('{{ scan['ai_result']|e }}', '{{ scan['upload_date']|e }}')">
                                <i class="fas fa-share-nodes"></i> Share
                            </button>
                            
                            <a href="{{ url_for('delete_history', record_id=scan['id']) }}" class="btn-action btn-delete" 
                               onclick="return confirm('Are you sure you want to permanently delete this record?');">
                                <i class="fas fa-trash-can"></i> Del
                            </a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
        
        <div id="noResultsMessage" class="empty-state" style="display: none;">
            <i class="fas fa-search-minus"></i>
            <h3>No Scans Found</h3>
            <p>You do not have any uploads for the selected month.</p>
        </div>

    {% else %}
        <div class="empty-state">
            <i class="fas fa-inbox"></i>
            <h3>Your History is Empty</h3>
            <p>You have not uploaded any scans yet. Select a modality to get started.</p>
            <div class="empty-links">
                <a href="{{ url_for('xray_upload_route') }}" class="btn-empty"><i class="fas fa-x-ray"></i> X-Ray Upload</a>
                <a href="#" class="btn-empty"><i class="fas fa-circle-notch"></i> CT Scan</a>
                <a href="#" class="btn-empty"><i class="fas fa-brain"></i> MRI Upload</a>
            </div>
        </div>
    {% endif %}

    <div id="reportModal" class="modal-overlay">
        <div class="modal-container">
            <div class="modal-header">
                <h2>🏥 AarogyamScanAI Clinical Report</h2>
                <button class="close-modal" onclick="closeReportModal()">&times;</button>
            </div>
            
            <div class="modal-body" id="printable-report">
                <div class="report-meta">
                    <p><strong>Generated By:</strong> CODE_X_ELITE AI Engine</p>
                    <p><strong>Scan Date:</strong> <span id="modalDate"></span></p>
                </div>
                
                <div class="patient-info-box">
                    <h3>👤 Patient Information</h3>
                    <p><strong>Name:</strong> <span id="modalPatientName"></span></p>
                    <p><strong>Status:</strong> Processed</p>
                </div>

                <div class="diagnosis-box">
                    <h3>🤖 AI Diagnostic Analysis</h3>
                    <table class="report-table">
                        <tr>
                            <th>Modality</th>
                            <th>Detected Condition</th>
                            <th>Confidence Tier</th>
                        </tr>
                        <tr>
                            <td>Medical Scan</td>
                            <td><span id="modalResult" class="modal-badge"></span></td>
                            <td>High Precision</td>
                        </tr>
                    </table>
                </div>

                <div class="scan-image-box">
                    <h3>🔍 Visual Scan</h3>
                    <img id="modalImage" src="" alt="Medical Scan Image">
                </div>
                
                <div class="report-footer-note">
                    <p><em>Disclaimer: This report is generated by Artificial Intelligence. Please consult a certified medical professional for final confirmation.</em></p>
                </div>
            </div>
            
            <div class="modal-footer">
                <button class="btn-print" onclick="printModalReport()"><i class="fas fa-print"></i> Print / Save as PDF</button>
            </div>
        </div>
    </div>

</main>

<script src="{{ url_for('static', filename='js/history.js') }}"></script>
{% endblock %}
"""

# ==========================================
# 2. CSS CODE (history.css) - Same as previous
# ==========================================
css_content = """.history-dashboard { max-width: 1200px; margin: 0 auto; padding: 40px 20px; font-family: 'Segoe UI', Inter, sans-serif; color: #1e293b; min-height: 80vh; }
.toast-container { position: fixed; top: 25px; right: 25px; z-index: 1000; display: flex; flex-direction: column; gap: 12px; }
.toast-message { min-width: 280px; background: #ffffff; padding: 15px 20px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 0.95rem; animation: slideIn 0.4s ease forwards; border-left: 6px solid #3b82f6; }
.toast-message.error { border-color: #ef4444; color: #b91c1c; }
.toast-message.success { border-color: #10b981; color: #047857; }
.close-toast { margin-left: auto; background: transparent; border: none; font-size: 1.2rem; color: #94a3b8; cursor: pointer; }
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
.history-header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px; flex-wrap: wrap; gap: 20px; }
.header-title h2 { font-size: 2rem; color: #0f172a; font-weight: 800; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
.header-title h2 i { color: #2563eb; }
.header-title p { color: #64748b; font-size: 1rem; }
.filter-container label { display: block; font-size: 0.9rem; font-weight: 600; color: #475569; margin-bottom: 8px; }
.custom-select { position: relative; width: 200px; }
.custom-select select { width: 100%; padding: 12px 35px 12px 15px; border: 1px solid #cbd5e1; border-radius: 8px; background: #ffffff; font-size: 1rem; color: #1e293b; appearance: none; cursor: pointer; font-family: inherit; }
.custom-select select:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
.select-icon { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); color: #94a3b8; pointer-events: none; }
.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; }
.history-card { background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; transition: transform 0.3s ease, box-shadow 0.3s ease; display: flex; flex-direction: column; }
.history-card:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,0,0,0.1); }
.card-image { width: 100%; height: 220px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: center; align-items: center; overflow: hidden; }
.history-img { width: 100%; height: 100%; object-fit: cover; }
.img-placeholder { display: flex; flex-direction: column; align-items: center; color: #94a3b8; gap: 10px; }
.card-content { padding: 20px; display: flex; flex-direction: column; gap: 15px; flex-grow: 1; }
.scan-date { font-size: 0.9rem; color: #64748b; font-weight: 500; }
.scan-result { font-size: 1rem; color: #1e293b; display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
.ai-badge { padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; }
.ai-badge { background: #e2e8f0; color: #1e293b; }
.result-normal, .result-negative, .result-low-risk { background: #dcfce7; color: #059669; border: 1px solid #a7f3d0;}
.result-pneumonia, .result-high-risk { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca;}
.card-actions { display: flex; gap: 8px; margin-top: auto; padding-top: 15px; border-top: 1px solid #f1f5f9; }
.btn-action { flex: 1; display: flex; align-items: center; justify-content: center; gap: 5px; padding: 10px 5px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; cursor: pointer; text-decoration: none; border: none; transition: all 0.2s; font-family: inherit; }
.btn-view { background: #e0e7ff; color: #1d4ed8; }
.btn-view:hover { background: #bfdbfe; }
.btn-share { background: #f1f5f9; color: #475569; }
.btn-share:hover { background: #e2e8f0; }
.btn-delete { background: #fef2f2; color: #dc2626; }
.btn-delete:hover { background: #fee2e2; }
.empty-state { text-align: center; padding: 60px 20px; background: #ffffff; border-radius: 20px; border: 2px dashed #cbd5e1; margin-top: 20px; }
.empty-state i { font-size: 3.5rem; color: #94a3b8; margin-bottom: 20px; }
.empty-state h3 { font-size: 1.6rem; color: #0f172a; margin-bottom: 10px; }
.empty-state p { color: #64748b; font-size: 1rem; margin-bottom: 25px; }
.empty-links { display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }
.btn-empty { padding: 10px 20px; background: #ffffff; border: 2px solid #2563eb; color: #2563eb; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s; }
.btn-empty:hover { background: #2563eb; color: #ffffff; }

/* MODAL (POPUP) STYLES */
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(5px); z-index: 2000; align-items: center; justify-content: center; padding: 20px; }
.modal-container { background: #ffffff; width: 100%; max-width: 700px; border-radius: 20px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); overflow: hidden; display: flex; flex-direction: column; max-height: 90vh; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 30px; background: #1e3a8a; color: white; }
.modal-header h2 { font-size: 1.5rem; margin: 0; font-weight: 700; }
.close-modal { background: none; border: none; color: white; font-size: 2rem; cursor: pointer; line-height: 1; }
.modal-body { padding: 30px; overflow-y: auto; }
.report-meta { display: flex; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 20px; color: #64748b; font-size: 0.95rem; }
.patient-info-box, .diagnosis-box, .scan-image-box { margin-bottom: 25px; }
.patient-info-box h3, .diagnosis-box h3, .scan-image-box h3 { font-size: 1.2rem; color: #0f172a; margin-bottom: 15px; border-left: 4px solid #3b82f6; padding-left: 10px; }
.report-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
.report-table th, .report-table td { border: 1px solid #e2e8f0; padding: 12px; text-align: left; }
.report-table th { background: #f8fafc; color: #475569; }
.modal-badge { font-weight: bold; padding: 5px 10px; border-radius: 6px; background: #f1f5f9; }
.scan-image-box img { width: 100%; max-height: 350px; object-fit: contain; border-radius: 12px; border: 1px solid #e2e8f0; background: #000; }
.report-footer-note { font-size: 0.85rem; color: #94a3b8; text-align: center; margin-top: 20px; }
.modal-footer { padding: 20px 30px; border-top: 1px solid #e2e8f0; background: #f8fafc; text-align: right; }
.btn-print { background: #2563eb; color: white; border: none; padding: 12px 25px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 1rem; transition: background 0.3s; }
.btn-print:hover { background: #1d4ed8; }
@media print { body * { visibility: hidden; } #reportModal, #printable-report, #printable-report * { visibility: visible; } #reportModal { position: absolute; left: 0; top: 0; width: 100%; background: none; } .modal-container { box-shadow: none; border: none; } .modal-header, .modal-footer { display: none !important; } }
@media (max-width: 768px) { .history-header { flex-direction: column; align-items: flex-start; } .custom-select { width: 100%; } .card-actions { flex-wrap: wrap; } .btn-action { min-width: 45%; } }
"""

# ==========================================
# 3. JS CODE (history.js) - TYPO FIXED HERE!
# ==========================================
js_content = """document.addEventListener("DOMContentLoaded", function() {
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
        text: `Medical Scan Report:\\nDate: ${dateStr}\\nDiagnosis: ${aiResult}\\n\\nGenerated via Code_X_Elite AI.`,
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
"""

files_to_create = {
    os.path.join(base_dir, "templates", "history.html"): html_content,
    os.path.join(base_dir, "static", "css", "history.css"): css_content,
    os.path.join(base_dir, "static", "js", "history.js"): js_content
}

def fix_view_button():
    print("🚀 AarogyamScanAI - Fixing JavaScript Modal Bug...\n")
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            
    for filepath, content in files_to_create.items():
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content.strip() + "\n")
            print(f"✅ Fixed file: {os.path.basename(filepath)}")

    print("\n🎉 DONE! The 'View' button typo is fixed. The modal will open perfectly now. (Press Ctrl+F5 in your browser to clear cache if needed)")

if __name__ == "__main__":
    fix_view_button()