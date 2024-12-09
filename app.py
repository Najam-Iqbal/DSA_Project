import streamlit as st
import pandas as pd
import networkx as nx
from heapq import heappop, heappush
import os

# Load and save CSV functions
def load_graph_from_csv(file_path):
    if not os.path.exists(file_path):
        return nx.Graph()
    df = pd.read_csv(file_path)
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['city1'], row['city2'], weight=row['distance_between'])
    return G

def save_graph_to_csv(file_path, G):
    edges = [
        {'city1': u, 'city2': v, 'distance_between': d['weight']}
        for u, v, d in G.edges(data=True)
    ]
    df = pd.DataFrame(edges)
    df.to_csv(file_path, index=False)

# Shortest path function using A* algorithm
def a_star_shortest_path(G, start, goal):
    if start not in G or goal not in G:
        return None, float('inf')

    open_set = [(0, start)]
    came_from = {}
    g_score = {node: float('inf') for node in G.nodes}
    g_score[start] = 0
    
    while open_set:
        _, current = heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, g_score[goal]

        for neighbor, edge_attr in G[current].items():
            tentative_g_score = g_score[current] + edge_attr['weight']
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                heappush(open_set, (g_score[neighbor], neighbor))

    return None, float('inf')

# Main Streamlit app
st.title("City Graph Manager")

# File paths
csv_file = "cities_distances.csv"

# Load the graph
G = load_graph_from_csv(csv_file)

# Menu options
menu = ["Find Shortest Path", "Display Graph Structure", "Add New Edge"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Find Shortest Path":
    st.header("Find Shortest Path Between Cities")
    
    start_city = st.text_input("Enter starting city:")
    goal_city = st.text_input("Enter destination city:")

    if st.button("Find Path"):
        if start_city and goal_city:
            path, distance = a_star_shortest_path(G, start_city, goal_city)
            if path:
                st.success(f"Shortest path: {' -> '.join(path)}\nTotal distance: {distance:.2f} km")
            else:
                st.error("No path found between the cities.")
        else:
            st.error("Please provide both starting and destination cities.")

elif choice == "Display Graph Structure":
    st.header("Graph Structure")
    st.write("Nodes (Cities):", list(G.nodes))
    st.write("Edges (Connections):")
    for u, v, d in G.edges(data=True):
        st.write(f"{u} <-> {v} ({d['weight']} km)")

elif choice == "Add New Edge":
    st.header("Add New Edge")

    city1 = st.text_input("Enter the first city:")
    city2 = st.text_input("Enter the second city:")
    distance = st.number_input("Enter distance between them (in km):", min_value=0.0, step=0.1)

    if st.button("Add Edge"):
        if city1 and city2 and distance > 0:
            G.add_edge(city1, city2, weight=distance)
            save_graph_to_csv(csv_file, G)
            st.success(f"Edge added between {city1} and {city2} with distance {distance} km. Changes saved to CSV.")
        else:
            st.error("Please provide valid inputs for both cities and distance.")
