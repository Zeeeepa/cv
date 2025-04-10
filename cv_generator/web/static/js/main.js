document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const cvForm = document.getElementById('cv-form');
    const generateBtn = document.getElementById('generate-cv');
    const formGenerateBtn = document.getElementById('form-generate-cv');
    const downloadBtn = document.getElementById('download-cv');
    const loadSampleBtn = document.getElementById('load-sample');
    const exportJsonBtn = document.getElementById('export-json');
    const importFileInput = document.getElementById('import-file');
    const randomStyleBtn = document.getElementById('random-style');
    
    // Style elements
    const currentStyleColor = document.getElementById('current-style-color');
    const currentStyleName = document.getElementById('current-style-name');
    
    // Section containers
    const workExperienceContainer = document.getElementById('work-experience-container');
    const educationContainer = document.getElementById('education-container');
    const skillsContainer = document.getElementById('skills-container');
    const certificatesContainer = document.getElementById('certificates-container');
    const honorsContainer = document.getElementById('honors-container');
    
    // Add section buttons
    const addWorkBtn = document.getElementById('add-work');
    const addEducationBtn = document.getElementById('add-education');
    const addSkillBtn = document.getElementById('add-skill');
    const addCertificateBtn = document.getElementById('add-certificate');
    const addHonorBtn = document.getElementById('add-honor');
    
    // Templates
    const workTemplate = document.getElementById('work-experience-template');
    const educationTemplate = document.getElementById('education-template');
    const skillTemplate = document.getElementById('skill-template');
    const certificateTemplate = document.getElementById('certificate-template');
    const honorTemplate = document.getElementById('honor-template');
    
    // Preview container
    const previewContent = document.getElementById('preview-content');
    
    // Current style
    let currentStyle = document.querySelector('input[name="style"]:checked')?.value || 'red';
    
    // Update the current style display
    function updateCurrentStyleDisplay() {
        const styleRadio = document.querySelector(`input[name="style"][value="${currentStyle}"]`);
        if (styleRadio) {
            const styleLabel = styleRadio.nextElementSibling;
            const styleColor = styleLabel.querySelector('.style-color').style.backgroundColor;
            const styleName = styleLabel.querySelector('.style-name').textContent;
            
            currentStyleColor.style.backgroundColor = styleColor;
            currentStyleName.textContent = styleName;
        }
    }
    
    // Initialize the current style display
    updateCurrentStyleDisplay();
    
    // Add event listeners for style selection
    document.querySelectorAll('input[name="style"]').forEach(radio => {
        radio.addEventListener('change', function() {
            currentStyle = this.value;
            updateCurrentStyleDisplay();
            
            // If we have a preview, update it with the new style
            if (downloadBtn.disabled === false) {
                generateCV();
            }
        });
    });
    
    // Add event listener for random style button
    if (randomStyleBtn) {
        randomStyleBtn.addEventListener('click', function() {
            // Show loading state
            randomStyleBtn.disabled = true;
            randomStyleBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            
            // Get a random style from the server
            fetch('/random_style')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update the current style
                        currentStyle = data.style;
                        
                        // Select the corresponding radio button
                        const styleRadio = document.querySelector(`input[name="style"][value="${currentStyle}"]`);
                        if (styleRadio) {
                            styleRadio.checked = true;
                        }
                        
                        // Update the current style display
                        currentStyleColor.style.backgroundColor = data.color;
                        currentStyleName.textContent = data.style.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
                        
                        // If we have a preview, update it with the new style
                        if (downloadBtn.disabled === false) {
                            generateCV();
                        }
                    } else {
                        console.error('Error getting random style:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    // Reset button state
                    randomStyleBtn.disabled = false;
                    randomStyleBtn.innerHTML = '<i class="bi bi-shuffle"></i> Random Style';
                });
        });
    }
    
    // Add event listeners for section buttons
    if (addWorkBtn) addWorkBtn.addEventListener('click', () => addSection(workExperienceContainer, workTemplate));
    if (addEducationBtn) addEducationBtn.addEventListener('click', () => addSection(educationContainer, educationTemplate));
    if (addSkillBtn) addSkillBtn.addEventListener('click', () => addSection(skillsContainer, skillTemplate));
    if (addCertificateBtn) addCertificateBtn.addEventListener('click', () => addSection(certificatesContainer, certificateTemplate));
    if (addHonorBtn) addHonorBtn.addEventListener('click', () => addSection(honorsContainer, honorTemplate));
    
    // Add event listeners for generate buttons
    if (generateBtn) generateBtn.addEventListener('click', generateCV);
    if (formGenerateBtn) formGenerateBtn.addEventListener('click', generateCV);
    
    // Add event listener for download button
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            window.location.href = `/download/${currentStyle}`;
        });
    }
    
    // Add event listener for load sample button
    if (loadSampleBtn) {
        loadSampleBtn.addEventListener('click', loadSampleData);
    }
    
    // Add event listener for export JSON button
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', exportAsJson);
    }
    
    // Add event listener for import file input
    if (importFileInput) {
        importFileInput.addEventListener('change', importFile);
    }
    
    // Function to add a new section
    function addSection(container, template) {
        const clone = document.importNode(template.content, true);
        
        // Add event listener to remove button
        const removeBtn = clone.querySelector('.remove-entry');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                this.closest('.card').remove();
            });
        }
        
        container.appendChild(clone);
    }
    
    // Function to generate CV
    function generateCV() {
        const formData = new FormData(cvForm);
        formData.append('style', currentStyle);
        
        // Show loading state
        previewContent.innerHTML = '<div class="text-center py-5"><div class="spinner-border" role="status"></div><p class="mt-3">Generating CV...</p></div>';
        
        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show preview
                previewContent.innerHTML = `<iframe src="${data.preview_url}"></iframe>`;
                
                // Enable download button
                downloadBtn.disabled = false;
            } else {
                // Show error
                previewContent.innerHTML = `<div class="text-center py-5 text-danger"><p>Error: ${data.error}</p></div>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            previewContent.innerHTML = '<div class="text-center py-5 text-danger"><p>An error occurred while generating the CV.</p></div>';
        });
    }
    
    // Function to load sample data
    function loadSampleData() {
        fetch('/load_sample')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateForm(data.data);
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while loading the sample data.');
            });
    }
    
    // Function to export form data as JSON
    function exportAsJson() {
        const formData = getFormData();
        const jsonString = JSON.stringify(formData, null, 2);
        
        // Create a blob and download link
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cv_data.json';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 0);
    }
    
    // Function to import file
    function importFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                populateForm(data);
            } catch (error) {
                console.error('Error parsing JSON:', error);
                alert('Error parsing the file. Make sure it is a valid JSON file.');
            }
        };
        
        reader.readAsText(file);
    }
    
    // Function to get form data as JSON
    function getFormData() {
        const formData = new FormData(cvForm);
        const data = {};
        
        // Personal information
        data.FirstName = formData.get('firstName') || '';
        data.LastName = formData.get('lastName') || '';
        data.Position = formData.get('position') || '';
        data.Address = formData.get('address') || '';
        data.Mobile = formData.get('mobile') || '';
        data.Email = formData.get('email') || '';
        data.Homepage = formData.get('homepage') || '';
        data.GitHub = formData.get('github') || '';
        data.LinkedIn = formData.get('linkedin') || '';
        data.Quote = formData.get('quote') || '';
        
        // Summary
        data.Summary = formData.get('summary') || '';
        
        // Work Experience
        data['Work Experience'] = [];
        const workTitles = formData.getAll('work_title[]');
        const workCompanies = formData.getAll('work_company[]');
        const workLocations = formData.getAll('work_location[]');
        const workDates = formData.getAll('work_date[]');
        const workDescriptions = formData.getAll('work_description[]');
        
        for (let i = 0; i < workTitles.length; i++) {
            if (workTitles[i]) {
                const job = {
                    Title: workTitles[i],
                    Company: workCompanies[i] || '',
                    Location: workLocations[i] || '',
                    Date: workDates[i] || '',
                    items: workDescriptions[i] ? workDescriptions[i].split('\n').filter(item => item.trim()) : []
                };
                data['Work Experience'].push(job);
            }
        }
        
        // Education
        data.Education = [];
        const eduDegrees = formData.getAll('edu_degree[]');
        const eduInstitutions = formData.getAll('edu_institution[]');
        const eduLocations = formData.getAll('edu_location[]');
        const eduDates = formData.getAll('edu_date[]');
        const eduDescriptions = formData.getAll('edu_description[]');
        
        for (let i = 0; i < eduDegrees.length; i++) {
            if (eduDegrees[i]) {
                const edu = {
                    Degree: eduDegrees[i],
                    Institution: eduInstitutions[i] || '',
                    Location: eduLocations[i] || '',
                    Date: eduDates[i] || '',
                    items: eduDescriptions[i] ? eduDescriptions[i].split('\n').filter(item => item.trim()) : []
                };
                data.Education.push(edu);
            }
        }
        
        // Skills
        data.Skills = [];
        const skillCategories = formData.getAll('skill_category[]');
        const skillLists = formData.getAll('skill_list[]');
        
        for (let i = 0; i < skillCategories.length; i++) {
            if (skillCategories[i]) {
                const skill = {
                    Category: skillCategories[i],
                    Skills: skillLists[i] || ''
                };
                data.Skills.push(skill);
            }
        }
        
        // Certificates
        data.Certificates = [];
        const certNames = formData.getAll('cert_name[]');
        const certIssuers = formData.getAll('cert_issuer[]');
        const certLocations = formData.getAll('cert_location[]');
        const certDates = formData.getAll('cert_date[]');
        const certDescriptions = formData.getAll('cert_description[]');
        
        for (let i = 0; i < certNames.length; i++) {
            if (certNames[i]) {
                const cert = {
                    Name: certNames[i],
                    Issuer: certIssuers[i] || '',
                    Location: certLocations[i] || '',
                    Date: certDates[i] || '',
                    items: certDescriptions[i] ? certDescriptions[i].split('\n').filter(item => item.trim()) : []
                };
                data.Certificates.push(cert);
            }
        }
        
        // Honors
        data.Honors = [];
        const honorNames = formData.getAll('honor_name[]');
        const honorIssuers = formData.getAll('honor_issuer[]');
        const honorLocations = formData.getAll('honor_location[]');
        const honorDates = formData.getAll('honor_date[]');
        
        for (let i = 0; i < honorNames.length; i++) {
            if (honorNames[i]) {
                const honor = {
                    Name: honorNames[i],
                    Issuer: honorIssuers[i] || '',
                    Location: honorLocations[i] || '',
                    Date: honorDates[i] || ''
                };
                data.Honors.push(honor);
            }
        }
        
        return data;
    }
    
    // Function to populate form with data
    function populateForm(data) {
        // Clear existing sections
        workExperienceContainer.innerHTML = '';
        educationContainer.innerHTML = '';
        skillsContainer.innerHTML = '';
        certificatesContainer.innerHTML = '';
        honorsContainer.innerHTML = '';
        
        // Personal information
        document.getElementById('firstName').value = data.FirstName || '';
        document.getElementById('lastName').value = data.LastName || '';
        document.getElementById('position').value = data.Position || '';
        document.getElementById('address').value = data.Address || '';
        document.getElementById('mobile').value = data.Mobile || '';
        document.getElementById('email').value = data.Email || '';
        document.getElementById('homepage').value = data.Homepage || '';
        document.getElementById('github').value = data.GitHub || '';
        document.getElementById('linkedin').value = data.LinkedIn || '';
        document.getElementById('quote').value = data.Quote || '';
        
        // Summary
        document.getElementById('summary').value = data.Summary || '';
        
        // Work Experience
        if (data['Work Experience'] && data['Work Experience'].length > 0) {
            data['Work Experience'].forEach(job => {
                const clone = document.importNode(workTemplate.content, true);
                
                clone.querySelector('input[name="work_title[]"]').value = job.Title || '';
                clone.querySelector('input[name="work_company[]"]').value = job.Company || '';
                clone.querySelector('input[name="work_location[]"]').value = job.Location || '';
                clone.querySelector('input[name="work_date[]"]').value = job.Date || '';
                
                if (job.items && job.items.length > 0) {
                    clone.querySelector('textarea[name="work_description[]"]').value = job.items.join('\n');
                }
                
                // Add event listener to remove button
                const removeBtn = clone.querySelector('.remove-entry');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        this.closest('.card').remove();
                    });
                }
                
                workExperienceContainer.appendChild(clone);
            });
        }
        
        // Education
        if (data.Education && data.Education.length > 0) {
            data.Education.forEach(edu => {
                const clone = document.importNode(educationTemplate.content, true);
                
                clone.querySelector('input[name="edu_degree[]"]').value = edu.Degree || '';
                clone.querySelector('input[name="edu_institution[]"]').value = edu.Institution || '';
                clone.querySelector('input[name="edu_location[]"]').value = edu.Location || '';
                clone.querySelector('input[name="edu_date[]"]').value = edu.Date || '';
                
                if (edu.items && edu.items.length > 0) {
                    clone.querySelector('textarea[name="edu_description[]"]').value = edu.items.join('\n');
                }
                
                // Add event listener to remove button
                const removeBtn = clone.querySelector('.remove-entry');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        this.closest('.card').remove();
                    });
                }
                
                educationContainer.appendChild(clone);
            });
        }
        
        // Skills
        if (data.Skills && data.Skills.length > 0) {
            data.Skills.forEach(skill => {
                const clone = document.importNode(skillTemplate.content, true);
                
                clone.querySelector('input[name="skill_category[]"]').value = skill.Category || '';
                clone.querySelector('input[name="skill_list[]"]').value = skill.Skills || '';
                
                // Add event listener to remove button
                const removeBtn = clone.querySelector('.remove-entry');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        this.closest('.card').remove();
                    });
                }
                
                skillsContainer.appendChild(clone);
            });
        }
        
        // Certificates
        if (data.Certificates && data.Certificates.length > 0) {
            data.Certificates.forEach(cert => {
                const clone = document.importNode(certificateTemplate.content, true);
                
                clone.querySelector('input[name="cert_name[]"]').value = cert.Name || '';
                clone.querySelector('input[name="cert_issuer[]"]').value = cert.Issuer || '';
                clone.querySelector('input[name="cert_location[]"]').value = cert.Location || '';
                clone.querySelector('input[name="cert_date[]"]').value = cert.Date || '';
                
                if (cert.items && cert.items.length > 0) {
                    clone.querySelector('textarea[name="cert_description[]"]').value = cert.items.join('\n');
                }
                
                // Add event listener to remove button
                const removeBtn = clone.querySelector('.remove-entry');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        this.closest('.card').remove();
                    });
                }
                
                certificatesContainer.appendChild(clone);
            });
        }
        
        // Honors
        if (data.Honors && data.Honors.length > 0) {
            data.Honors.forEach(honor => {
                const clone = document.importNode(honorTemplate.content, true);
                
                clone.querySelector('input[name="honor_name[]"]').value = honor.Name || '';
                clone.querySelector('input[name="honor_issuer[]"]').value = honor.Issuer || '';
                clone.querySelector('input[name="honor_location[]"]').value = honor.Location || '';
                clone.querySelector('input[name="honor_date[]"]').value = honor.Date || '';
                
                // Add event listener to remove button
                const removeBtn = clone.querySelector('.remove-entry');
                if (removeBtn) {
                    removeBtn.addEventListener('click', function() {
                        this.closest('.card').remove();
                    });
                }
                
                honorsContainer.appendChild(clone);
            });
        }
    }
});
