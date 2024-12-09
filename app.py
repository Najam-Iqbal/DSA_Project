import streamlit as st
import pandas as pd
import networkx as nx
from heapq import heappop, heappush

# Helper functions for A* algorithm
def heuristic(a, b, graph):
    """Simple heuristic function for A* algorithm"""
    return 0  # For this implementation, we'll use 0 as a placeholder

def a_star(graph, start, goal):
    if start not in graph or goal not in graph:
        return [], -1
    
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in graph}
    f_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    f_score[start] = heuristic(start, goal, graph)
    
    while open_set:
        current_f, current = heappop(open_set)
        
        if current == goal:
            path = []
            total_distance = g_score[goal]
            while current:
                path.append(current)
                current = came_from.get(current)
            return path[::-1], total_distance
        
        for neighbor, weight in graph[current]:
            tentative_g_score = g_score[current] + weight
            
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal, graph)
                heappush(open_set, (f_score[neighbor], neighbor))
    
    return [], -1

# Load graph from CSV file
def load_graph_from_csv(file):
    df = pd.read_csv(file)
    graph = {}
    for _, row in df.iterrows():
        city1, city2, distance = row['city1'], row['city2'], row['distance_between']
        
        # Ensure bidirectional connections
        graph.setdefault(city1, []).append((city2, distance))
        graph.setdefault(city2, []).append((city1, distance))
    
    return graph

# Streamlit app
def main():
    st.title("City Graph Manager")

    # Initialize session state for graph
    if 'graph' not in st.session_state:
        st.session_state.graph = {}

    # Upload CSV
    uploaded_file = st.file_uploader("Upload a CSV file containing city distances", type=["csv"])
    
    if uploaded_file:
        # Load graph from uploaded file
        st.session_state.graph = load_graph_from_csv(uploaded_file)
        st.success("Cities and distances loaded successfully!")

    # Display graph structure
    if st.checkbox("Display graph structure"):
        st.subheader("Graph Structure")
        if st.session_state.graph:
            for city, neighbors in st.session_state.graph.items():
                neighbors_str = ", ".join([f"{neighbor} ({dist} km)" for neighbor, dist in neighbors])
                st.write(f"{city} -> {neighbors_str}")
        else:
            st.write("No graph loaded. Please upload a CSV or add edges.")

    # Find shortest path
    st.subheader("Find Shortest Path")
    start_city = st.text_input("Enter starting city:")
    destination_city = st.text_input("Enter destination city:")
    
    if st.button("Find Path"):
        if start_city and destination_city:
            path, distance = a_star(st.session_state.graph, start_city, destination_city)
            if path:
                st.success(f"Shortest path: {' -> '.join(path)}")
                st.success(f"Total distance: {distance} km")
            else:
                st.error("Path not found!")
        else:
            st.error("Please enter both starting and destination cities.")

    # Add new edge
    st.subheader("Add New Edge")
    city1 = st.text_input("City 1:")
    city2 = st.text_input("City 2:")
    distance = st.number_input("Distance (in km):", min_value=0.0, format="%.2f")
    
    if st.button("Add Edge"):
        if city1 and city2 and distance > 0:
            # Ensure bidirectional connection
            st.session_state.graph.setdefault(city1, []).append((city2, distance))
            st.session_state.graph.setdefault(city2, []).append((city1, distance))
            st.success("Edge added successfully!")
        else:
            st.error("Please fill out all fields correctly.")

    # Save graph to CSV
    if st.button("Save to CSV"):
        if st.session_state.graph:
            output_data = []
            for city, neighbors in st.session_state.graph.items():
                for neighbor, dist in neighbors:
                    # Avoid duplicate edges
                    if {city, neighbor} not in [{row['city1'], row['city2']} for row in output_data]:
                        output_data.append({"city1": city, "city2": neighbor, "distance_between": dist})
            
            output_df = pd.DataFrame(output_data)
            output_df.to_csv("updated_cities_distances.csv", index=False)
            st.success("Graph saved to updated_cities_distances.csv")
        else:
            st.error("No graph to save. Please add edges first.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
