  // Sample data - in a real app, this would be fetched from your backend
  const reportsData = [
    { 
        id: 1, 
        condition: "Eczema",
        severity: "Moderate",
        date: "2025-03-01",
        confidence: "94%",
        content: "Your skin shows signs of eczema, characterized by dry, itchy patches. The AI analysis identified several affected areas with moderate severity. Recommended treatment includes moisturizing regularly, using a topical corticosteroid, and avoiding known irritants. Consider taking shorter showers with lukewarm water and using fragrance-free products.",
        imageUrl: "/api/placeholder/400/300"
    },
    { 
        id: 2, 
        condition: "Acne Vulgaris",
        severity: "Mild",
        date: "2025-02-15",
        confidence: "89%",
        content: "The AI analysis detected mild acne vulgaris. The affected areas show comedones and a few inflammatory papules. Recommended over-the-counter treatment with benzoyl peroxide or salicylic acid. Establish a gentle cleansing routine and avoid excessive scrubbing. If not improved in 8 weeks, consider a dermatology consultation.",
        imageUrl: "/api/placeholder/400/300"
    },
    { 
        id: 3, 
        condition: "Contact Dermatitis",
        severity: "Moderate",
        date: "2025-01-20",
        confidence: "91%",
        content: "You appear to have contact dermatitis, likely triggered by exposure to an irritant or allergen. The affected skin shows redness, inflammation, and small blisters. Avoid contact with the suspected trigger. Apply a cold compress and use an over-the-counter hydrocortisone cream. If symptoms worsen or don't improve within a week, seek medical attention.",
        imageUrl: "/api/placeholder/400/300"
    },
    { 
        id: 4, 
        condition: "Psoriasis",
        severity: "Severe",
        date: "2024-12-05",
        confidence: "97%",
        content: "The AI analysis has identified psoriasis with a high confidence level. The condition appears severe with thick, scaly plaques on multiple body areas. This chronic condition requires ongoing management. Recommended treatments include topical corticosteroids, vitamin D analogs, and moisturizers. Consider phototherapy and consult with a dermatologist for prescription treatments like biologics or systemic medications.",
        imageUrl: "/api/placeholder/400/300"
    }
];

// DOM Elements
const searchInput = document.getElementById('search-input');
const dateFilter = document.getElementById('date-filter');
const reportsContainer = document.getElementById('reports-container');
const loadingElement = document.getElementById('loading');
const emptyStateElement = document.getElementById('empty-state');
const modal = document.getElementById('report-modal');
const closeModalBtn = document.getElementById('close-modal');
const modalImage = document.getElementById('modal-image');
const modalCondition = document.getElementById('modal-condition');
const modalSeverity = document.getElementById('modal-severity');
const modalDate = document.getElementById('modal-date');
const modalConfidence = document.getElementById('modal-confidence');
const modalContent = document.getElementById('modal-content');
const modalDownload = document.getElementById('modal-download');

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    // Simulate loading data from server
    setTimeout(() => {
        loadingElement.style.display = 'none';
        reportsContainer.style.display = 'grid';
        renderReports(reportsData);
    }, 1000);
    
    // Set up event listeners
    searchInput.addEventListener('input', filterReports);
    dateFilter.addEventListener('change', filterReports);
    closeModalBtn.addEventListener('click', closeModal);
    
    // Close modal when clicking outside the content
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
});

// Render reports
function renderReports(reports) {
    reportsContainer.innerHTML = '';
    
    if (reports.length === 0) {
        reportsContainer.style.display = 'none';
        emptyStateElement.style.display = 'flex';
        return;
    }
    
    reportsContainer.style.display = 'grid';
    emptyStateElement.style.display = 'none';
    
    reports.forEach(report => {
        const card = document.createElement('div');
        card.className = 'card bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700 hover:border-purple-500 transition-colors duration-200';
        
        // Get severity class
        let severityClass = '';
        let severityTextClass = '';
        if (report.severity === 'Mild') {
            severityClass = 'severity-mild';
            severityTextClass = 'text-green-400';
        } else if (report.severity === 'Moderate') {
            severityClass = 'severity-moderate';
            severityTextClass = 'text-yellow-400';
        } else {
            severityClass = 'severity-severe';
            severityTextClass = 'text-red-400';
        }
        
        card.innerHTML = `
            <div class="p-4 border-b border-gray-700">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-bold text-white">${report.condition}</h3>
                        <div class="flex items-center mt-1">
                            <i class="fas fa-clock text-gray-500 mr-1 text-sm"></i>
                            <span class="text-sm text-gray-400">${report.date}</span>
                        </div>
                    </div>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${severityClass}">
                        ${report.severity}
                    </span>
                </div>
                <div class="mt-2">
                    <div class="text-sm text-gray-400">
                        AI Confidence: <span class="text-purple-400 font-medium">${report.confidence}</span>
                    </div>
                </div>
            </div>
            <div class="p-4 bg-gray-900 flex justify-end space-x-2">
                <button class="preview-btn inline-flex items-center px-3 py-1.5 rounded-md text-sm" data-id="${report.id}">
                    <i class="fas fa-eye mr-1"></i>
                    Preview
                </button>
                <button class="download-btn inline-flex items-center px-3 py-1.5 rounded-md text-sm" data-id="${report.id}">
                    <i class="fas fa-download mr-1"></i>
                    Download
                </button>
            </div>
        `;
        
        reportsContainer.appendChild(card);
        
        // Add event listeners to buttons
        const previewBtn = card.querySelector('.preview-btn');
        const downloadBtn = card.querySelector('.download-btn');
        
        previewBtn.addEventListener('click', () => openPreview(report));
        downloadBtn.addEventListener('click', () => downloadReport(report));
    });
}

// Filter reports based on search and date
function filterReports() {
    const searchTerm = searchInput.value.toLowerCase();
    const dateValue = dateFilter.value;
    
    const filtered = reportsData.filter(report => {
        const matchesSearch = report.condition.toLowerCase().includes(searchTerm);
        const matchesDate = dateValue ? report.date === dateValue : true;
        return matchesSearch && matchesDate;
    });
    
    renderReports(filtered);
}

// Open the preview modal
function openPreview(report) {
    modalImage.src = report.imageUrl;
    modalCondition.textContent = report.condition;
    
    // Set severity with appropriate color
    modalSeverity.textContent = report.severity;
    if (report.severity === 'Mild') {
        modalSeverity.className = 'text-green-400';
    } else if (report.severity === 'Moderate') {
        modalSeverity.className = 'text-yellow-400';
    } else {
        modalSeverity.className = 'text-red-400';
    }
    
    modalDate.textContent = report.date;
    modalConfidence.textContent = report.confidence;
    modalContent.textContent = report.content;
    
    // Set download handler
    modalDownload.onclick = () => downloadReport(report);
    
    // Show modal
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent scrolling behind modal
}

// Close the preview modal
function closeModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
}