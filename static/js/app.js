class VideoGenerator {
    constructor() {
        this.currentJobId = null;
        this.statusCheckInterval = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('videoForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateVideo();
        });

        // Example button
        document.getElementById('exampleBtn').addEventListener('click', () => {
            this.toggleExamples();
        });

        // Copy script button
        document.getElementById('copyScriptBtn').addEventListener('click', () => {
            this.copyScript();
        });

        // New video button
        document.getElementById('newVideoBtn').addEventListener('click', () => {
            this.resetToInput();
        });

        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.generateVideo();
        });

        // Back to input button
        document.getElementById('backToInputBtn').addEventListener('click', () => {
            this.resetToInput();
        });
    }

    async generateVideo() {
        const promptInput = document.getElementById('promptInput');
        const prompt = promptInput.value.trim();

        if (!prompt) {
            this.showToast('Please enter a description for your video', 'error');
            return;
        }

        try {
            this.showProgressSection();
            this.updateProgress(0, 'Starting video generation...', 'Initializing AI script generation...');

            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to start video generation');
            }

            const data = await response.json();
            this.currentJobId = data.job_id;
            
            this.showToast('Video generation started!', 'success');
            this.startStatusChecking();

        } catch (error) {
            console.error('Error generating video:', error);
            this.showError(error.message);
        }
    }

    startStatusChecking() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }

        this.statusCheckInterval = setInterval(() => {
            this.checkStatus();
        }, 2000); // Check every 2 seconds
    }

    async checkStatus() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/status/${this.currentJobId}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    const errorData = await response.json();
                    this.handleError(errorData.message || 'Job not found');
                    return;
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const status = await response.json();

            this.updateProgress(
                status.progress || 0,
                status.message || 'Processing...',
                this.getDetailedMessage(status.status)
            );

            if (status.status === 'completed') {
                this.handleSuccess(status);
            } else if (status.status === 'error') {
                const errorMsg = status.error_details || status.message || 'Unknown error occurred';
                this.handleError(errorMsg);
            } else if (status.status === 'not_found') {
                this.handleError(status.message || 'Job not found');
            }

        } catch (error) {
            console.error('Error checking status:', error);
            this.handleError(`Failed to check generation status: ${error.message}`);
        }
    }

    getDetailedMessage(status) {
        const messages = {
            'generating_script': 'AI is analyzing your request and creating the Manim script...',
            'compiling': 'Compiling the animation and rendering the video...',
            'completed': 'Your video has been generated successfully!',
            'error': 'An error occurred during generation.',
            'not_found': 'Job not found in the system.'
        };
        return messages[status] || 'Processing your request...';
    }

    handleSuccess(status) {
        clearInterval(this.statusCheckInterval);
        this.showResultsSection(status.video_url, status.script);
        this.showToast('Video generated successfully!', 'success');
    }

    handleError(message) {
        clearInterval(this.statusCheckInterval);
        this.showError(message);
    }

    updateProgress(progress, message, details) {
        document.getElementById('progressFill').style.width = `${progress}%`;
        document.getElementById('progressMessage').textContent = message;
        document.getElementById('progressDetails').textContent = details;
    }

    showProgressSection() {
        this.hideAllSections();
        document.getElementById('progressSection').style.display = 'block';
    }

    showResultsSection(videoUrl, script) {
        this.hideAllSections();
        
        const resultVideo = document.getElementById('resultVideo');
        resultVideo.src = videoUrl;
        
        const generatedScript = document.getElementById('generatedScript');
        generatedScript.textContent = script;
        
        document.getElementById('resultsSection').style.display = 'block';
    }

    showError(message) {
        this.hideAllSections();
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorSection').style.display = 'block';
        this.showToast(message, 'error');
    }

    hideAllSections() {
        const sections = ['progressSection', 'resultsSection', 'errorSection'];
        sections.forEach(sectionId => {
            document.getElementById(sectionId).style.display = 'none';
        });
    }

    resetToInput() {
        this.hideAllSections();
        this.currentJobId = null;
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        document.getElementById('promptInput').focus();
    }

    async toggleExamples() {
        const examplesSection = document.getElementById('examplesSection');
        const examplesList = document.getElementById('examplesList');

        if (examplesSection.style.display === 'none') {
            try {
                const response = await fetch('/examples');
                const examples = await response.json();
                
                examplesList.innerHTML = '';
                examples.forEach(example => {
                    const exampleItem = document.createElement('div');
                    exampleItem.className = 'example-item';
                    exampleItem.textContent = example;
                    exampleItem.addEventListener('click', () => {
                        document.getElementById('promptInput').value = example;
                        examplesSection.style.display = 'none';
                    });
                    examplesList.appendChild(exampleItem);
                });

                examplesSection.style.display = 'block';
            } catch (error) {
                console.error('Error loading examples:', error);
                this.showToast('Failed to load examples', 'error');
            }
        } else {
            examplesSection.style.display = 'none';
        }
    }

    copyScript() {
        const scriptElement = document.getElementById('generatedScript');
        const scriptText = scriptElement.textContent;

        if (navigator.clipboard) {
            navigator.clipboard.writeText(scriptText).then(() => {
                this.showToast('Script copied to clipboard!', 'success');
                
                // Update button text temporarily
                const copyBtn = document.getElementById('copyScriptBtn');
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalText;
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy script:', err);
                this.fallbackCopyScript(scriptText);
            });
        } else {
            this.fallbackCopyScript(scriptText);
        }
    }

    fallbackCopyScript(text) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showToast('Script copied to clipboard!', 'success');
        } catch (err) {
            console.error('Fallback copy failed:', err);
            this.showToast('Failed to copy script. Please select and copy manually.', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VideoGenerator();
});

// Add some helpful keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to generate video
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('videoForm');
        if (form.style.display !== 'none') {
            form.dispatchEvent(new Event('submit'));
        }
    }
});

// Add auto-resize for textarea
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('promptInput');
    
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
});