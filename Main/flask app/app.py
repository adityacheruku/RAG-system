from flask import Flask, request, jsonify
import os
import utils

# Load environment variables from .env file

app = Flask(__name__)
print(app.handle_http_exception)
@app.route('/query', methods=['POST'])
def query():
    """
    Handles the POST request to '/query'. Extracts the query from the request,
    processes it through the search, concatenate, and generate functions,
    and returns the generated answer.
    """
    data = request.get_json()
    query = data.get('query', None)
    print(query)
    try:
        print('sfbhash')
        #query = "mgit college"
        # get the data/query from streamlit app
        
        if not query:
            return jsonify({'answer': "Invalid inpjhhgjhghut data"}), 400
        
        # Step 1: Search and scrape articles based on the query
        print("Step 1: searching articles")
        articles = utils.search_articles(query)
        # Step 2: Concatenate content from the scraped articles
        print("Step 2: concatenating content")
        content, token_chunks = utils.concatenate_content(articles)
        # Step 3: Generate an answer using the LLM
        print("Step 3: generating answer")
        sparse_results = utils.sparse_retrieval(str(query), token_chunks)
        dense_results = utils.dense_retrieval(str(query), token_chunks)
        reranked_results = utils.rerank_results(sparse_results, dense_results)
        # return the jsonified text back to streamlit
        top_content = {i+1: content[idx+1] for i, idx in enumerate(reranked_results[:len(reranked_results)]) if idx+1 in content}
        data = utils.generate_answer(content, query)
        print(data)
        return jsonify({'answer': data})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'answer': "An error occurred"}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5004, debug=True)
