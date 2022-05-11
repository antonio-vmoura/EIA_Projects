from graph import Graph
from search import Search

def main():
    graph = Graph() #Create a graph
        
    #Create graph connections (Actual distance)
    graph.connect('Arad', 'Zerind', 75)
    graph.connect('Arad', 'Sibiu', 140)
    graph.connect('Arad', 'Timisoara', 118)
    graph.connect('Zerind', 'Oradea', 71)
    graph.connect('Oradea', 'Sibiu', 151)
    graph.connect('Sibiu', 'Fugaras', 99)
    graph.connect('Sibiu', 'Rimnicu Vilcea', 80)
    graph.connect('Rimnicu Vilcea', 'Pitesti', 97)
    graph.connect('Timisoara', 'Lugoj', 111)
    graph.connect('Lugoj','Mehadia', 70)
    graph.connect('Mehadia', 'Dobreta',75)
    graph.connect('Dobreta', 'Craiova', 120)
    graph.connect('Craiova','Rimnicu Vilcea', 146)
    graph.connect('Craiova','Pitesti', 138)
    graph.connect('Fugaras', 'Bucharest', 211)
    graph.connect('Pitesti', 'Bucharest', 101)
    graph.connect('Giurgiu', 'Bucharest', 90)
        
    #Make graph undirected, create symmetric connections
    graph.make_undirected()
        
    #Create heuristics (straight-line distance) for Destination Bucharest
    heuristics = {
        "Arad": 366,
        "Bucharest": 0,
        "Craiova": 160,
        "Dobreta": 242,
        "Fugaras": 176,
        "Lugoj": 244,
        "Mehadia": 241,
        "Oradea": 380,
        "Pitesti": 10,
        "Rimnicu Vilcea": 193,
        "Sibiu": 253,
        "Timisoara": 329,
        "Zerind": 374,
        "Giurgiu": 77
    }
    
    print("\n" + "- "*10 + "Graph" + " -"*10 + "\n")
    graph.printgraph() #Print Graph Nodes
    print("\n" + "- "*10 + "Result" + " -"*10 + "\n")

    path, totalcost = Search.uniform_cost(graph, 'Arad', 'Bucharest') #Run uniform_cost_search
    print(f"- Uniform Cost Search:\n")
    print(f"FINAL_COST: {str(totalcost)}\n")

    path, totalcost = Search.greedy(graph, heuristics, 'Arad', 'Bucharest') #Run greedy_search
    print(f"- Greedy Search:\n")
    print(f"FINAL_COST: {str(totalcost)}, PATH: {path}\n")
    
    path, totalcost = Search.a_star(graph, heuristics, 'Arad', 'Bucharest') #Run a_star_search
    print(f"- A Star Search:\n")
    print(f"FINAL_COST: {str(totalcost)}, PATH: {path}\n")

# Tell python to run main method
if __name__ == "__main__":
    main()