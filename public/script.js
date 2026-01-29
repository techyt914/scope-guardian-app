document.addEventListener('DOMContentLoaded', () => {
    const analyzeButton = document.getElementById('analyze-button');
    const originalScopeEl = document.getElementById('original-scope');
    const newRequestEl = document.getElementById('new-request');
    const generatedEmailEl = document.getElementById('generated-email');

    analyzeButton.addEventListener('click', async () => {
        const originalScope = originalScopeEl.value;
        const newRequest = newRequestEl.value;

        if (!originalScope.trim() || !newRequest.trim()) {
            alert('Please fill in both the original scope and the new request.');
            return;
        }

        // --- UI Updates for Loading State ---
        generatedEmailEl.innerHTML = '<p class="text-gray-400 animate-pulse">Analyzing and generating email...</p>';
        analyzeButton.disabled = true;
        analyzeButton.textContent = 'Analyzing...';
        analyzeButton.classList.add('opacity-50', 'cursor-not-allowed');

        try {
            const response = await fetch('/api/handler', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    original_scope: originalScope,
                    new_request: newRequest,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Format the response to be displayed safely as HTML
            generatedEmailEl.textContent = data.email_draft;

        } catch (error) {
            console.error('Error:', error);
            generatedEmailEl.innerHTML = `<p class="text-red-400">An error occurred: ${error.message}</p>`;
        } finally {
            // --- Restore UI from Loading State ---
            analyzeButton.disabled = false;
            analyzeButton.textContent = 'Analyze & Generate Email';
            analyzeButton.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });
});
