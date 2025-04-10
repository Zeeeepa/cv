/**
 * CV Generator Formatting Utilities
 * 
 * This file contains the JavaScript code for the formatting toolbar and text formatting
 * functionality in the CV Generator web UI.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize formatting toolbars
    initFormatting();
});

/**
 * Initialize formatting toolbars and functionality
 */
function initFormatting() {
    // Add formatting toolbar to each textarea
    document.querySelectorAll('.formatting-enabled').forEach(textarea => {
        createFormattingToolbar(textarea);
    });

    // Add event listeners for formatting buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('format-btn') || 
            event.target.parentElement.classList.contains('format-btn')) {
            
            const button = event.target.classList.contains('format-btn') ? 
                event.target : event.target.parentElement;
            
            const formatType = button.dataset.format;
            const textarea = button.closest('.formatting-toolbar').nextElementSibling;
            
            if (formatType === 'bold') {
                applyFormatting(textarea, 'bold');
            } else if (formatType === 'italic') {
                applyFormatting(textarea, 'italic');
            } else if (formatType === 'underline') {
                applyFormatting(textarea, 'underline');
            } else if (formatType === 'color') {
                const colorPicker = button.querySelector('.color-picker');
                if (colorPicker) {
                    colorPicker.click();
                    colorPicker.addEventListener('change', function() {
                        applyFormatting(textarea, 'color', { color: this.value.replace('#', '') });
                    }, { once: true });
                }
            } else if (formatType === 'bullet-list') {
                applyBulletList(textarea);
            } else if (formatType === 'numbered-list') {
                applyNumberedList(textarea);
            } else if (formatType === 'heading') {
                const level = button.dataset.level || 1;
                applyHeading(textarea, level);
            } else if (formatType === 'font-style') {
                const styleSelect = button.querySelector('.font-style-select');
                if (styleSelect) {
                    styleSelect.click();
                    styleSelect.addEventListener('change', function() {
                        applyFormatting(textarea, 'custom', { style: this.value });
                    }, { once: true });
                }
            } else if (formatType === 'font-weight') {
                const weightSelect = button.querySelector('.font-weight-select');
                if (weightSelect) {
                    weightSelect.click();
                    weightSelect.addEventListener('change', function() {
                        applyFormatting(textarea, 'custom', { weight: this.value });
                    }, { once: true });
                }
            } else if (formatType === 'font-size') {
                const sizeSelect = button.querySelector('.font-size-select');
                if (sizeSelect) {
                    sizeSelect.click();
                    sizeSelect.addEventListener('change', function() {
                        applyFormatting(textarea, 'custom', { size: this.value });
                    }, { once: true });
                }
            } else if (formatType === 'markdown') {
                applyFormatting(textarea, 'markdown');
            }
        }
    });

    // Add event listeners for format selection dropdowns
    document.querySelectorAll('.format-select').forEach(select => {
        select.addEventListener('change', function() {
            const formatType = this.dataset.format;
            const textarea = this.closest('.form-group').querySelector('textarea');
            
            if (formatType === 'section-format') {
                // Update the hidden format input
                const formatInput = this.closest('.card-body').querySelector('input[name$="_format[]"]');
                if (formatInput) {
                    formatInput.value = this.value;
                }
            }
        });
    });
}

/**
 * Create a formatting toolbar for a textarea
 * 
 * @param {HTMLElement} textarea - The textarea to create a toolbar for
 */
function createFormattingToolbar(textarea) {
    // Create toolbar container
    const toolbar = document.createElement('div');
    toolbar.className = 'formatting-toolbar btn-toolbar mb-2';
    toolbar.setAttribute('role', 'toolbar');
    toolbar.setAttribute('aria-label', 'Formatting toolbar');
    
    // Create button groups
    const basicGroup = document.createElement('div');
    basicGroup.className = 'btn-group me-2';
    
    const listGroup = document.createElement('div');
    listGroup.className = 'btn-group me-2';
    
    const advancedGroup = document.createElement('div');
    advancedGroup.className = 'btn-group me-2';
    
    // Basic formatting buttons
    basicGroup.innerHTML = `
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="bold" title="Bold">
            <i class="bi bi-type-bold"></i>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="italic" title="Italic">
            <i class="bi bi-type-italic"></i>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="underline" title="Underline">
            <i class="bi bi-type-underline"></i>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="color" title="Text Color">
            <i class="bi bi-palette"></i>
            <input type="color" class="color-picker" style="display: none;">
        </button>
    `;
    
    // List formatting buttons
    listGroup.innerHTML = `
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="bullet-list" title="Bullet List">
            <i class="bi bi-list-ul"></i>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="numbered-list" title="Numbered List">
            <i class="bi bi-list-ol"></i>
        </button>
    `;
    
    // Advanced formatting buttons
    advancedGroup.innerHTML = `
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="heading" data-level="1" title="Heading">
            <i class="bi bi-type-h1"></i>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="font-style" title="Font Style">
            <i class="bi bi-fonts"></i>
            <select class="font-style-select" style="display: none;">
                <option value="default">Default</option>
                <option value="serif">Serif</option>
                <option value="sans-serif">Sans-serif</option>
                <option value="monospace">Monospace</option>
            </select>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="font-size" title="Font Size">
            <i class="bi bi-text-size"></i>
            <select class="font-size-select" style="display: none;">
                <option value="normalsize">Normal</option>
                <option value="small">Small</option>
                <option value="large">Large</option>
                <option value="Large">Larger</option>
                <option value="LARGE">Largest</option>
            </select>
        </button>
        <button type="button" class="btn btn-sm btn-outline-secondary format-btn" data-format="markdown" title="Apply Markdown">
            <i class="bi bi-markdown"></i>
        </button>
    `;
    
    // Add button groups to toolbar
    toolbar.appendChild(basicGroup);
    toolbar.appendChild(listGroup);
    toolbar.appendChild(advancedGroup);
    
    // Add toolbar before textarea
    textarea.parentNode.insertBefore(toolbar, textarea);
}

/**
 * Apply formatting to selected text in a textarea
 * 
 * @param {HTMLElement} textarea - The textarea to apply formatting to
 * @param {string} formatType - The type of formatting to apply
 * @param {Object} options - Additional options for formatting
 */
function applyFormatting(textarea, formatType, options = {}) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    if (selectedText.length === 0) {
        alert('Please select some text to format.');
        return;
    }
    
    // Send formatting request to server
    fetch('/format_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: selectedText,
            format_type: formatType,
            options: options
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Replace selected text with formatted text
            const formattedText = data.formatted_text;
            textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
            
            // Update cursor position
            textarea.selectionStart = start;
            textarea.selectionEnd = start + formattedText.length;
            textarea.focus();
        } else {
            console.error('Error formatting text:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

/**
 * Apply bullet list formatting to selected text
 * 
 * @param {HTMLElement} textarea - The textarea to apply formatting to
 */
function applyBulletList(textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    if (selectedText.length === 0) {
        alert('Please select some text to format as a bullet list.');
        return;
    }
    
    // Split text into lines and add bullet points
    const lines = selectedText.split('\n');
    const bulletedLines = lines.map(line => line.trim() ? `- ${line.trim()}` : line);
    const formattedText = bulletedLines.join('\n');
    
    // Replace selected text with formatted text
    textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
    
    // Update cursor position
    textarea.selectionStart = start;
    textarea.selectionEnd = start + formattedText.length;
    textarea.focus();
}

/**
 * Apply numbered list formatting to selected text
 * 
 * @param {HTMLElement} textarea - The textarea to apply formatting to
 */
function applyNumberedList(textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    if (selectedText.length === 0) {
        alert('Please select some text to format as a numbered list.');
        return;
    }
    
    // Split text into lines and add numbers
    const lines = selectedText.split('\n');
    const numberedLines = lines.map((line, index) => line.trim() ? `${index + 1}. ${line.trim()}` : line);
    const formattedText = numberedLines.join('\n');
    
    // Replace selected text with formatted text
    textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
    
    // Update cursor position
    textarea.selectionStart = start;
    textarea.selectionEnd = start + formattedText.length;
    textarea.focus();
}

/**
 * Apply heading formatting to selected text
 * 
 * @param {HTMLElement} textarea - The textarea to apply formatting to
 * @param {number} level - The heading level (1-6)
 */
function applyHeading(textarea, level) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    if (selectedText.length === 0) {
        alert('Please select some text to format as a heading.');
        return;
    }
    
    // Add heading markers
    const headingMarkers = '#'.repeat(level);
    const formattedText = `${headingMarkers} ${selectedText}`;
    
    // Replace selected text with formatted text
    textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
    
    // Update cursor position
    textarea.selectionStart = start;
    textarea.selectionEnd = start + formattedText.length;
    textarea.focus();
}
