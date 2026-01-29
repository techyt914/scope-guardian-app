const { GoogleGenerativeAI } = require("@google/generative-ai");

// Assumes GOOGLE_API_KEY is set as an environment variable
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

function buildPrompt(scope, request_text) {
    return `
    You are "Scope Guardian," an AI assistant for freelancers. Your job is to analyze an original scope of work and a new client request, then generate a polite and professional email draft.
    
    **Analysis Steps:**
    1.  **Compare:** Carefully compare the new request against the original scope.
    2.  **Decision:**
        *   If the new request is clearly **within** the original scope, generate an "IN_SCOPE" email.
        *   If the new request is clearly **outside** the original scope, generate an "OUT_OF_SCOPE" email.
    3.  **Generate Email:** Write the email draft based on your decision. Be friendly, professional, and clear.
    
    **Original Scope of Work:**
    ---
    ${scope}
    ---
    
    **New Client Request:**
    ---
    ${request_text}
    ---
    
    **Output Format:**
    Provide ONLY the email draft text. Do not add any extra commentary, headers, or explanations. Start the email with "Hi [Client Name]," and sign off with "Best regards,\\n[Your Name]".
    `;
}

module.exports = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { original_scope, new_request } = req.body;

    if (!original_scope || !new_request) {
        return res.status(400).json({ error: 'Both original_scope and new_request are required.' });
    }

    try {
        const model = genAI.getGenerativeModel({ model: "gemini-pro" });
        const prompt = buildPrompt(original_scope, new_request);
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        
        res.status(200).json({ email_draft: text });

    } catch (error) {
        console.error('Error calling AI model:', error);
        res.status(500).json({ error: 'Failed to communicate with the AI model.' });
    }
};
