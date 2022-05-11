
class Search():
    def uniform_cost(graph, start, end):
        open_list = []; closed_list = list(); path = list() #Will store the path we are taking
        curr_node = start #Starting node
        totalcost = 0

        open_list.append((start, 0))

        if(end not in graph.graph_dict): #Incase the goal state does not exist
            print("GOAL STATE DOES NOT EXIST")
            return None, None

        while(curr_node != end): #Runs Until we cannot find the goal state or
            curr_node, curr_dist = open_list.pop(0)

            if(curr_node == end):
                totalcost = curr_dist
                path.append(curr_node)
                break

            if curr_node not in closed_list: #if the node has not been explored
                closed_list.append(curr_node) 
                neighbors = graph.get_n(curr_node) #get the node's neighbors

                for key, value in neighbors.items(): #adding the previous distance
                    open_list.append((key, value + curr_dist))

                open_list.sort(key=lambda tup: tup[1])  #sorting the tuples

        return path, totalcost

    def greedy(graph, heuristics, start, end):
        open_list = list(); closed_list = list(); path = list() #Will store the path we are taking
        curr_node = graph.get_greedy_n(start, heuristics, end) #Starting node
        totalcost = 0

        open_list.append(curr_node)

        if(end not in graph.graph_dict): #Incase the goal state does not exist
            print("GOAL STATE DOES NOT EXIST")
            return None, None

        while(curr_node.name != end): #Runs Until we cannot find the goal state or
            totalcost += curr_node.dist #adding distance to totalcost
            path.append(curr_node.name)
        
            curr_node = open_list.pop() 
            closed_list.append(curr_node)
            curr_node = graph.get_greedy_n(curr_node.parent, heuristics, end)
            open_list.append(curr_node)
            
            if(curr_node.name == end):
                path.append(curr_node.name)
                break

        return path, totalcost

    def a_star(graph, heuristics, start, end):
        open_list = list(); closed_list = list(); path = list() #Will store the path we are taking
        curr_node = graph.get_a_star_n(start, heuristics, end) #Starting node
        totalcost = 0

        open_list.append(curr_node)

        if(end not in graph.graph_dict): #Incase the goal state does not exist
            print("GOAL STATE DOES NOT EXIST")
            return None, None

        while(curr_node.name != end): #Runs Until we cannot find the goal state or
            totalcost += curr_node.dist #adding distance to totalcost
            path.append(curr_node.name)
        
            curr_node = open_list.pop()
            closed_list.append(curr_node)
            curr_node = graph.get_a_star_n(curr_node.parent, heuristics, end)
            open_list.append(curr_node)
            
            if(curr_node.name == end):
                path.append(curr_node.name)
                break

        return path, totalcost