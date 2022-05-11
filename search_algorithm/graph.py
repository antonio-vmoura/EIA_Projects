class Node():
    def __init__(self, name, parent, dist, goal=0, cost=0): #Initializing the class
        self.name = name
        self.parent = parent
        self.dist = dist #Distance to start node #g
        self.goal = goal #Distance to goal node #h
        self.cost = cost #Total cost #f
            
    def __eq__(self, other):  #Comparing two nodes
        return self.name == other.name
    
    def __lt__(self, other): #Sorting nodes
        return self.cost < other.cost
    
    def __repr__(self): #Printing nodes
        return (f"({self.name}: {self.dist}, {self.goal}, {self.cost})")
    
    def printNode(self): #Customized Printing of nodes
        print(f"{self.name}: {self.parent}, {self.dist}, {self.goal}, {self.cost}")

class Graph():
    def __init__(self, graph_dict=None, directed=True): #Initialize the class
        self.graph_dict = graph_dict or {}
        self.directed = directed
        if not directed:
            self.make_undirected()
                
    def make_undirected(self): #Create an undirected graph by adding symmetric edges
        for a in list(self.graph_dict.keys()):
            for (b, dist) in self.graph_dict[a].items():
                self.graph_dict.setdefault(b, {})[a] = dist
    
    #Add a link from A and B of given distance, and also add the inverse link if the graph is undirected
    def connect(self, A, B, distance=1): 
        self.graph_dict.setdefault(A, {})[B] = distance
        if not self.directed:
            self.graph_dict.setdefault(B, {})[A] = distance
               
    def get_n(self, a, b=None): #Get neighbors or a neighbor
        links = self.graph_dict.setdefault(a, {})
        if b is None:
            return links
        else:
            return links.get(b)
            
    def nodes(self): #Return a list of nodes in the graph
        s1 = set([k for k in self.graph_dict.keys()])
        s2 = set([k2 for v in self.graph_dict.values() for k2, v2 in v.items()])
        nodes = s1.union(s2)
        return list(nodes)

    def get_greedy_n(self, city, heuristics, end): #Get a specific neighbour which has minimum heuristics
        nodes = list(); min = 999

        for (b, dist) in self.graph_dict[city].items():
            if(b == end):
                return Node(city, b, dist, heuristics[b])
            nodes.append(Node(city, b, dist, heuristics[b]))
            if (heuristics[b]) < min:
                min = heuristics[b]
                minnode = Node(city, b, dist, heuristics[b])       
        return minnode

    def get_a_star_n(self, city, heuristics, end): #Get a specific neighbour which has minimum cost
        nodes = list(); min = 999

        for (b, dist) in self.graph_dict[city].items():
            if(b == end):
                return Node(city, b, dist, heuristics[b], dist+heuristics[b])
            nodes.append(Node(city, b, dist, heuristics[b], dist+heuristics[b]))
            if (dist+heuristics[b]) < min:
                min = dist+heuristics[b]
                minnode = Node(city, b, dist, heuristics[b], dist+heuristics[b])       
        return minnode
        
    def printgraph(self): #Function to print each edge in the entire graph
        for a in list(self.graph_dict.keys()):
            for (b, dist) in self.graph_dict[a].items():
                print(f"{a} - {b} : {self.graph_dict.setdefault(a, {})[b]}")