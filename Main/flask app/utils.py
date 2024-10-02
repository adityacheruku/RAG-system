import os
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv("C:\\Users\\saiad\\OneDrive\\Documents\\llm_search_template\\.env")

# Load API keys from environment variables
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
OPENAI_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=OPENAI_API_KEY)

model = SentenceTransformer('all-MiniLM-L6-v2')

def search_articles(query):
    """
    Searches for articles related to the query using Serper API.
    Returns a list of dictionaries containing article URLs, headings, and text.
    """
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPER_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    articles = results["organic_results"]
    return articles

def fetch_article_content(url):
    """
    Fetches the article content, extracting headings and text.
    """
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Remove unwanted sections (ads, sponsored)
            unwanted_classes = ['ad', 'sponsored', 'promo', 'advertisement']
            for unwanted in unwanted_classes:
                for tag in soup.find_all(class_=unwanted):
                    tag.decompose()

            # Extract headings and content
            content = ''
            heading = soup.find('title')
            tokenized_text = []
            for x in soup.find_all(['h1', 'h2', 'h3','p']):
                content += x.get_text(strip=True)

            tokens = content.split()
            tokenized_text.extend(tokens)

            article = {
                "title": heading.get_text(strip=True),
                "content": content
            }
            return article, tokenized_text
        else:
            print(f"Error: Unable to fetch article at {url}")
            return None, []
    except Exception as e:
        print(f"Error fetching content: {e}")
        return None, []

def concatenate_content(articles):
    """
    Concatenates the content of the provided articles into a single string.
    """
    full_text = {}
    token_chunks = []
    x = 10
    for i, article in enumerate(articles[:x], start=1):  # Process first 5 articles
        article_content, tokens = fetch_article_content(article["link"])
        if article_content and type(article_content["content"]) == str:
            full_text[i] = article_content
            token_chunks.append(tokens)
        else:
            print("skip")
        if article_content is None:
            resp = requests.get(article["redirect_link"])
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                links = soup.find_all('a')
                if links:
                    article_content, tokens = fetch_article_content(links[0].get('href'))
                    if article_content and type(article_content["content"]) == str:
                        full_text[i] = article_content
                        token_chunks.append(tokens)
                    if article_content is None:
                        x+=1
    return full_text, token_chunks

def sparse_retrieval(query, token_chunks):
    """
    Sparse retrieval using TF-IDF.
    """
    documents = [' '.join(tokens) for tokens in token_chunks]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform([query])
    cosine_similarities = np.dot(query_vector, tfidf_matrix.T).toarray().flatten()
    sparse_results = np.argsort(-cosine_similarities)  # Sort in descending order
    return sparse_results

def dense_retrieval(query, token_chunks):
    """
    Dense retrieval using SentenceTransformer embeddings.
    """
    document_embeddings = [model.encode(' '.join(tokens), convert_to_tensor=True) for tokens in token_chunks]
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = [util.pytorch_cos_sim(query_embedding, doc_embedding)[0][0].item() for doc_embedding in document_embeddings]
    dense_results = np.argsort(-np.array(similarities))  # Sort in descending order
    return dense_results

def rerank_results(sparse_results, dense_results):
    """
    Combines and re-ranks sparse and dense results by summing their ranks.
    """
    combined_scores = {}
    
    # Assign scores based on ranks
    for rank, idx in enumerate(sparse_results):
        if idx not in combined_scores:
            combined_scores[idx] = 0
        combined_scores[idx] += rank
    
    for rank, idx in enumerate(dense_results):
        if idx not in combined_scores:
            combined_scores[idx] = 0
        combined_scores[idx] += rank
    
    # Sort by combined scores
    sorted_indices = sorted(combined_scores, key=combined_scores.get)
    return sorted_indices

def generate_answer(content, query):
    """
    Generates an answer from the concatenated content using GPT-4.
    The content and the user's query are used to generate a contextual answer.
    """
    fin_query = ''
    for ele in content:
        fin_query += (content[ele]['title'] + '\n' + content[ele]['content'] + '\n')
    input_query = f"Based on the following content retrieved from the web pages, answer the query with accurate and orignal content as per the retrived information '{query}': {fin_query}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(input_query)
    print(response.text)
    # Implement OpenAI call logic and get back the response
    return response.text


