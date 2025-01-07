import google.generativeai as genai
import os
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from dotenv import load_dotenv
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

def get_events():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()

    select_query = """
    SELECT * FROM news_articles
    WHERE DATE(date) >= DATE('now', '-3 days');
    """

    cursor.execute(select_query)
    articles = cursor.fetchall()
    conn.close()
    
    embeddings = []

    idx = 0
    print(len(articles))
    for article in articles:
        print(idx)
        idx += 1
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=article[5][:8192])
        embeddings.append(result['embedding'])

    # Step 1: Calculate pairwise cosine similarity
    similarity_matrix = cosine_similarity(embeddings)

    # Step 2: Create graph
    G = nx.Graph()

    # Add nodes for each article
    for i in range(len(embeddings)):
        G.add_node(i)

    # Add edges between nodes if similarity >= 0.8
    threshold = 0.8
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            if similarity_matrix[i][j] >= threshold:
                G.add_edge(i, j)

    # Step 3: Find connected components (clusters)
    connected_components = list(nx.connected_components(G))

    # Step 4: Create a 2D list of clusters (Each cluster is a list of article indices)
    clusters = [list(component) for component in connected_components]

    good_clusters = []
    for cluster in clusters:
        if len(cluster) <= 3 or articles[cluster[0]][5] == "NULL":
            continue
        good_clusters.append(cluster)

    for i in range(len(good_clusters)):
        for j in range(len(good_clusters[i])):
            good_clusters[i][j] = articles[good_clusters[i][j]][0]

    print(good_clusters)
    return good_clusters


