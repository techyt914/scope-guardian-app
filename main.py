from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

# Configure the Gemini API key
# Make sure to set the GOOGLE_API_KEY environment variable
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    # Handle the case where the API key is not set
    print("Error: GOOGLE_API_KEY environment variable not set.")
    # You might want to exit or handle this more gracefully
    exit()


app = Flask(__name__)

# --- AI Configuration ---
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# --- Routes ---

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyzes the scope and new request to generate an email."""
    data = request.json
    original_scope = data.get('original_scope')
    new_request = data.get('new_request')

    if not original_scope or not new_request:
        return jsonify({'error': 'Both original scope and new request are required.'}), 400

    try:
        prompt = build_prompt(original_scope, new_request)
        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        
        # Extract the email content from the response
        # We add a little bit of parsing to clean up the AI's response
        raw_response = convo.last.text
        email_draft = clean_response(raw_response)

        return jsonify({'email_draft': email_draft})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Failed to communicate with the AI model.'}), 500

# --- Helper Functions ---

def build_prompt(scope, request_text):
    """Builds the prompt for the Gemini model."""
    return f"""
    You are "Scope Guardian," an AI assistant for freelancers. Your job is to analyze an original scope of work and a new client request, then generate a polite and professional email draft.

    **Analysis Steps:**
    1.  **Compare:** Carefully compare the new request against the original scope.
    2.  **Decision:**
        *   If the new request is clearly **within** the original scope, generate an "IN_SCOPE" email.
        *   If the new request is clearly **outside** the original scope, generate an "OUT_OF_SCOPE" email.
        *   If it's ambiguous, lean towards "OUT_OF_SCOPE" to protect the freelancer.
    3.  **Generate Email:** Write the email draft based on your decision. Be friendly, professional, and clear.

    **Original Scope of Work:**
    ---
    {scope}
    ---

    **New Client Request:**
    ---
    {request_text}
    ---

    **Output Format:**
    Provide ONLY the email draft text. Do not add any extra commentary, headers, or explanations. Start the email with "Hi [Client Name]," and sign off with "Best regards,\n[Your Name]".

    **Example "OUT_OF_SCOPE" Email:**
    Hi [Client Name],

    Thanks for reaching out with this request.

    Based on my review, this seems like a great addition that falls outside of our original scope. I'd be happy to treat this as a small add-on to our project.

    If you'd like to proceed, just let me know, and I can put together a quick quote for you.

    Best regards,
    [Your Name]

    **Example "IN_SCOPE" Email:**
    Hi [Client Name],

    Thanks for the message.

    This is covered by our original scope, and I'll get started on it right away. I'll let you know if I have any questions.

    Best regards,
    [Your Name]

    Now, generate the email for the provided scope and request.
    """

def clean_response(text):
    """Cleans up the raw response from the AI."""
    # Sometimes the model might wrap the response in markdown
    if "```" in text:
        text = text.split("```")[1]
        if text.lower().startswith('text'):
            text = text[4:].strip()

    return text.strip()


if __name__ == '__main__':
    # Use Gunicorn in production
    # For local dev:
    app.run(debug=True, port=5001)
