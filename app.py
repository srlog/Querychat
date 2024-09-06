from flask import Flask, render_template, request, jsonify
import groq

app = Flask(__name__)
# Initialize the Groq client with your API key
try:
    client = groq.Groq(api_key="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")
except Exception as e:  
    print(f"Error initializing Groq client: {e}")

import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer

# Initialize SBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load embeddings from Excel file
df = pd.read_excel('embeddings_with_content.xlsx')

# Print columns to verify the presence of necessary columns
print("Columns in the Excel file:", df.columns)

# Check if necessary columns exist
if 'embeddings' not in df.columns or 'fileName' not in df.columns or 'content' not in df.columns:
    raise KeyError("The Excel file must contain 'embeddings', 'fileName', and 'content' columns.")

# Function to clean and validate JSON data
def clean_json(json_str):
    try:
        # Clean up JSON strings
        json_str = json_str.strip().replace("'", '"')  # Replace single quotes with double quotes
        json_str = json_str.replace(" ", "")  # Remove unnecessary spaces
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e} in data: {json_str}")
        return None

# Convert JSON strings back to numpy arrays
def parse_embeddings(json_str):
    data = clean_json(json_str)
    if data is not None:
        try:
            return np.array(data, dtype=np.float32)
        except Exception as e:
            print(f"Error converting JSON to numpy array: {e}")
            return np.array([])  # Return an empty array if conversion fails
    else:
        return np.array([])  # Return an empty array if JSON is invalid

# Apply conversion function to the 'embeddings' column
df['embeddings'] = df['embeddings'].apply(parse_embeddings)

# Function to compute similarity between query and document embeddings
def calculate_similarity(query_embedding, doc_embedding):
    if np.linalg.norm(doc_embedding) == 0 or np.linalg.norm(query_embedding) == 0:
        return 0
    return np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))

# Function to find the best matches for a given query
def find_best_matches(user_query, top_n=3):
    # Compute embedding for the user's query
    query_embedding = model.encode(user_query)

    # Check if the query embedding is valid
    if np.linalg.norm(query_embedding) == 0:
        return {"reply": "Query embedding is invalid. Please provide a more meaningful query."}

    # Calculate similarities and sort results
    df['similarity'] = df['embeddings'].apply(lambda x: calculate_similarity(query_embedding, x))
    
    # Get the top_n most similar documents
    top_matches = df.nlargest(top_n, 'similarity')

    # Check for matches and return the top matches
    if top_matches['similarity'].isnull().all() or top_matches['similarity'].max() == 0:
        return {"reply": "No matching documents found."}
    else:
        replies = []
        for i, row in top_matches.iterrows():
            replies.append(row['content'])
        ans = "\n".join(replies)
        print(ans)
        return f""" User's query: {user_query}
        So for this try to refer the data from this provided information, 
        {ans}
        If you cant find the information just answer it generally, and dont mention about the data
        Make sure the responses are short and precise, like in a chat.
        Also form the sentences, by referring you are part of the college"""
    
from groq import Groq
client = Groq(
    api_key="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"
)

conversation_history = [
    {
        "role": "system",
        "content": "You are a An inference engine capable of deducing implicit geospatial information from user queries."
    }
]
def ask(user_input):
    conversation_history.append({
        "role": "user",
        "content": find_best_matches(user_input)
    })
    
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model="llama3-70b-8192",
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    
    response = chat_completion.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": response
    })
    return response



@app.route('/', methods=['GET', 'POST'])
def index():
    gpt_response = ""
    return render_template('index.html', gpt_response=gpt_response)



import requests
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    groq_reply = ask(user_message)
    ls = groq_reply.split('\n')
    groq_reply = '<br>'.join(ls)
    print('user:',user_message,'AI:',groq_reply)
    return jsonify({'reply': groq_reply})
if __name__ == "__main__":
    app.run(debug=True)