// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // Get references to all the important HTML elements
    const uploadForm = document.getElementById('upload-form');
    const uploadInput = document.getElementById('file-upload-input');
    const servingSizeInput = document.getElementById('serving-size-input');
    const uploadSection = document.getElementById('upload-section');
    const reportSection = document.getElementById('report-section');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    // Add a 'submit' event listener to the form
    uploadForm.addEventListener('submit', (event) => {
        // Prevent the browser's default form submission behavior
        event.preventDefault();
        startAnalysis();
    });

    const startAnalysis = () => {
        // --- 1. VALIDATE INPUT ---
        // Check if a file was selected and serving size was entered
        if (!uploadInput.files || uploadInput.files.length === 0) {
            alert("Please select an image file.");
            return;
        }
        if (!servingSizeInput.value) {
            alert("Please enter your serving size.");
            return;
        }

        // --- 2. PREPARE FOR UPLOAD ---
        // Show the loading animation and hide the upload form
        uploadSection.style.display = 'none';
        loadingOverlay.style.display = 'flex';
        
        // Cycle through loading messages
        const texts = ["Calibrating sensors...", "Scanning molecular structure...", "Cross-referencing database...", "Detecting compounds...", "Finalizing report..."];
        let i = 0;
        const interval = setInterval(() => {
            loadingText.textContent = texts[i];
            i = (i + 1) % texts.length;
        }, 1000);

        // --- 3. CREATE FORM DATA & CALL API ---
        // FormData is the standard way to send files and text in a POST request
        const formData = new FormData();
        formData.append('image', uploadInput.files[0]);
        formData.append('servingSize', servingSizeInput.value);

        // Use the Fetch API to send data to your Django backend endpoint
        fetch('/api/analyze/', {
            method: 'POST',
            body: formData,
            // Note: Don't set 'Content-Type' header when using FormData with files,
            // the browser sets it automatically with the correct boundary.
        })
        .then(response => {
            // Check if the server responded with an error
            if (!response.ok) {
                // If so, get the error message from the response body
                return response.json().then(err => {
                    throw new Error(err.error || 'Server responded with an error');
                });
            }
            // If the response is OK, parse the JSON body
            return response.json();
        })
        .then(data => {
            // --- 4. HANDLE SUCCESSFUL RESPONSE ---
            // Stop the loading animation
            clearInterval(interval);
            loadingOverlay.style.display = 'none';
            
            // Show the report section and populate it with data from the API
            reportSection.style.display = 'grid';
            populateReportData(data.analysis);
        })
        .catch(error => {
            // --- 5. HANDLE ERRORS ---
            // Stop the loading animation and show an error message
            clearInterval(interval);
            loadingOverlay.style.display = 'none';
            // Show the upload section again so the user can retry
            uploadSection.style.display = 'block'; 
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
        });
    };

    // This function takes the analysis data and populates the HTML report
    const populateReportData = (analysis) => {
        // Populate specimen info
        document.getElementById('specimen-name').textContent = analysis.productName;
        document.getElementById('specimen-serving').textContent = `Serving Size: ${servingSizeInput.value}`;
        if (uploadInput.files && uploadInput.files[0]) {
            document.getElementById('specimen-image-preview').src = URL.createObjectURL(uploadInput.files[0]);
        }

        // Populate ingredients
        const ingredientsGrid = document.getElementById('ingredients-grid');
        ingredientsGrid.innerHTML = '';
        analysis.ingredients.forEach(ing => {
            const card = document.createElement('div');
            const status = ing.score <= 4 ? 'danger' : ing.score <= 6 ? 'warning' : 'ok';
            card.className = `ingredient-card ${status}`;
            card.innerHTML = `<div class="ingredient-name">${ing.name} <span class="health-score ${status}">${ing.score}/10</span></div>`;
            ingredientsGrid.appendChild(card);
        });

        // Populate nutrient profile
        const nutrientProfile = document.getElementById('nutrient-profile');
        nutrientProfile.innerHTML = '';
        analysis.nutrientProfile.macro.forEach(n => {
            const item = document.createElement('div');
            item.className = 'nutrient-item';
            item.innerHTML = `<div class="nutrient-label"><span>${n.name}</span><span>${n.amount}</span></div><div class="nutrient-bar"><div class="nutrient-bar-fill ${n.name.toLowerCase()}" style="width: ${n.dailyValue}%;"></div></div>`;
            nutrientProfile.appendChild(item);
        });
        
        // ... (Add similar logic for all other report sections: allergens, summary, etc.) ...
        
        // Populate processing score
        document.getElementById('processing-score-value').textContent = `${analysis.processingScore.score}/100`;
        document.getElementById('processing-score-label').textContent = analysis.processingScore.label;
    };
});
