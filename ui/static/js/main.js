// Main JavaScript for On-Page SEO Audit Tool

document.addEventListener('DOMContentLoaded', function() {
    const auditForm = document.getElementById('audit-form');
    const loadingSection = document.getElementById('loading');
    const resultsSection = document.getElementById('results');
    const resultsContent = document.getElementById('results-content');
    const reportLink = document.getElementById('report-link');
    const newAuditBtn = document.getElementById('new-audit-btn');
    const submitBtn = document.getElementById('submit-btn');

    // Handle form submission
    auditForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading section
        auditForm.parentElement.parentElement.style.display = 'none';
        loadingSection.style.display = 'block';
        
        // Get form data
        const formData = new FormData(auditForm);
        const url = formData.get('url');
        const keywords = formData.get('keywords');
        
        // Get selected audit types
        const auditTypes = [];
        document.querySelectorAll('input[name="audit_types"]:checked').forEach(checkbox => {
            auditTypes.push(checkbox.value);
        });
        
        // Prepare request data
        const requestData = {
            url: url,
            audit_types: auditTypes
        };
        
        // Add keywords if provided
        if (keywords && keywords.trim() !== '') {
            requestData.keywords = keywords.split(',').map(k => k.trim());
        }
        
        // Send request to API
        fetch('/audit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading section
            loadingSection.style.display = 'none';
            
            // Show results section
            resultsSection.style.display = 'block';
            
            // Update report link
            reportLink.href = `/static/reports/${data.report_id}.html`;
            console.log('Report ID:', data.report_id);
            console.log('Report Path:', data.report_path);
            
            // Extract report ID from the report path if report_id is not available
            if (!data.report_id && data.report_path) {
                const pathParts = data.report_path.split('/');
                const filename = pathParts[pathParts.length - 1];
                reportLink.href = `/static/reports/${filename}`;
                console.log('Using filename from path:', filename);
            }
            
            // Display summary results
            displaySummaryResults(data.summary, data.url, requestData.keywords);
        })
        .catch(error => {
            console.error('Error:', error);
            loadingSection.style.display = 'none';
            alert('An error occurred while running the audit. Please try again.');
            auditForm.parentElement.parentElement.style.display = 'block';
        });
    });
    
    // Handle new audit button click
    newAuditBtn.addEventListener('click', function() {
        resultsSection.style.display = 'none';
        auditForm.reset();
        auditForm.parentElement.parentElement.style.display = 'block';
    });
    
    // Function to display summary results
    function displaySummaryResults(summary, url, keywords) {
        // Clear previous results
        resultsContent.innerHTML = '';
        
        // Create summary header
        const summaryHeader = document.createElement('div');
        summaryHeader.className = 'mb-4';
        let headerHTML = `
            <h3 class="mb-3">Audit Summary for <a href="${url}" target="_blank">${url}</a></h3>
        `;
        
        // Add keywords if provided
        if (keywords && keywords.length > 0) {
            headerHTML += `<p class="mb-3">Target Keywords: <strong>${keywords.join(', ')}</strong></p>`;
        }
        
        headerHTML += `
            <div class="alert alert-${getSummaryAlertClass(summary.score)}" role="alert">
                Overall Score: <strong>${summary.score}%</strong> based on ${summary.total_checks} checks
            </div>
        `;
        
        summaryHeader.innerHTML = headerHTML;
        resultsContent.appendChild(summaryHeader);
        
        // Create summary cards row
        const summaryRow = document.createElement('div');
        summaryRow.className = 'row mb-4';
        
        // Overall summary card
        const overallCard = document.createElement('div');
        overallCard.className = 'col-md-4';
        overallCard.innerHTML = `
            <div class="summary-card">
                <h4 class="text-center">Overall Score</h4>
                <div class="summary-score ${getScoreClass(summary.score)}">${summary.score}%</div>
                <div class="text-center">
                    <span class="badge bg-success">${summary.passed} Passed</span>
                    <span class="badge bg-warning text-dark">${summary.warnings} Warnings</span>
                    <span class="badge bg-danger">${summary.errors} Errors</span>
                </div>
            </div>
        `;
        summaryRow.appendChild(overallCard);
        
        // Category scores card
        const categoriesCard = document.createElement('div');
        categoriesCard.className = 'col-md-8';
        let categoriesHtml = `
            <div class="summary-card">
                <h4 class="text-center">Category Scores</h4>
                <div class="row">
        `;
        
        // Add category scores
        for (const [category, data] of Object.entries(summary.category_scores)) {
            categoriesHtml += `
                <div class="col-md-6 mb-2">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>${formatCategoryName(category)}</span>
                        <span class="badge ${getScoreBadgeClass(data.score)}">${data.score}%</span>
                    </div>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar ${getProgressBarClass(data.score)}" role="progressbar" style="width: ${data.score}%" 
                             aria-valuenow="${data.score}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            `;
        }
        
        categoriesHtml += `
                </div>
            </div>
        `;
        categoriesCard.innerHTML = categoriesHtml;
        summaryRow.appendChild(categoriesCard);
        
        resultsContent.appendChild(summaryRow);
        
        // Add note about full report
        const reportNote = document.createElement('div');
        reportNote.className = 'alert alert-info';
        reportNote.innerHTML = `
            <strong>Note:</strong> Click the "View Full Report" button below to see detailed results for all ${summary.total_checks} SEO factors.
        `;
        resultsContent.appendChild(reportNote);
    }
    
    // Helper functions for styling
    function getSummaryAlertClass(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }
    
    function getScoreClass(score) {
        if (score >= 80) return 'score-good';
        if (score >= 60) return 'score-warning';
        return 'score-error';
    }
    
    function getScoreBadgeClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning text-dark';
        return 'bg-danger';
    }
    
    function getProgressBarClass(score) {
        if (score >= 80) return 'bg-success';
        if (score >= 60) return 'bg-warning';
        return 'bg-danger';
    }
    
    function formatCategoryName(category) {
        return category
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
});
