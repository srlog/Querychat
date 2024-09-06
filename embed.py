import os
import pandas as pd
import nltk
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from docx import Document

# Download NLTK data for tokenization
nltk.download('punkt')

# Initialize SBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Folder path - adjust to your environment
folder_path = '/content/drive/MyDrive/docs/scraped_pages'

# Function to extract text from PDF files
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX files
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to process and extract text from different document formats
def process_documents(folder_path):
    data = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        file_extension = file_name.split('.')[-1].lower()

        # Process based on file type
        if file_extension == 'pdf':
            content = extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            content = extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            with open(file_path, 'r') as file:
                content = file.read()
        else:
            continue

        # Tokenize and split content into smaller chunks
        tokens = nltk.word_tokenize(content)
        chunks = [' '.join(tokens[i:i+300]) for i in range(0, len(tokens), 300)]  # Chunk size: 300 tokens
        for i, chunk in enumerate(chunks):
            data.append({'fileName': f"{file_name}-part-{i+1}", 'content': chunk})

    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=['fileName', 'content'])
    return df

# Process documents and create embeddings
df = process_documents(folder_path)

# Ensure the 'content' column exists and generate embeddings
if 'content' in df.columns:
    # Remove any NaN values or empty strings in 'content'
    df['content'] = df['content'].fillna('')

    # Generate embeddings for each content chunk
    df['embeddings'] = df['content'].apply(lambda x: model.encode(str(x)).tolist())
else:
    print("No 'content' column found. Please check your document processing.")

# Save embeddings and data to an Excel file
df.to_excel('/content/embeddings_with_content.xlsx', index=False)

print("Embeddings generated and saved to an Excel file.")
