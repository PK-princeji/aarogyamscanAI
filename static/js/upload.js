document.addEventListener("DOMContentLoaded", function() {
    
    const fileInput = document.getElementById("xray_image");
    const dropArea = document.getElementById("drag-drop-area");
    const statusBadge = document.getElementById("file-status-badge");

    fileInput.addEventListener("change", function() {
        processFiles(this.files);
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false); 
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('drag-active');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('drag-active');
        }, false);
    });

    dropArea.addEventListener('drop', function(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        fileInput.files = files;
        processFiles(files);
    }, false);

    function processFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            const fileName = file.name;
            const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
            
            statusBadge.classList.add('success');
            statusBadge.innerHTML = `<i class="fas fa-check-circle"></i> Scan Loaded: ${fileName} (${fileSizeMB} MB)`;
            dropArea.style.borderColor = "#10b981";
            dropArea.style.backgroundColor = "#f0fdf4";
        } else {
            statusBadge.classList.remove('success');
            statusBadge.innerHTML = `<i class="fas fa-exclamation-circle"></i> Waiting for file...`;
            dropArea.style.borderColor = "#94a3b8";
            dropArea.style.backgroundColor = "#f8fafc";
        }
    }
});
