from collections import deque

def bfs(graph, start):
    visited = set()          # Track visited nodes
    queue = deque([start])   # Initialize queue

    while queue:
        node = queue.popleft()

        if node not in visited:
            print(node, end=" ")
            visited.add(node)

            # Add neighbors safely
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)

# Example graph
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['E'],
    'D': [],
    'E': []
}

bfs(graph, 'A')
