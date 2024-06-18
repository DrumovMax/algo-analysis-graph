import random
import heapq
import networkx as nx


def generate_connected_graph(num_vertices, k=None, min_edges_per_vertex=1, max_edges_per_vertex=None, is_regular=False):
    if max_edges_per_vertex is None:
        max_edges_per_vertex = num_vertices - 1

    if num_vertices <= 0:
        return {}

    G = nx.Graph()
    G.add_nodes_from({chr(ord('A') + i): [] for i in range(num_vertices)})

    for i in range(1, num_vertices):
        vertex = chr(ord('A') + i)
        random_vertex = chr(ord('A') + random.randint(0, i - 1))
        weight = random.randint(1, 10)
        G.add_edge(vertex, random_vertex, weight=weight)

    if is_regular:
        vertices = list(G.nodes())
        for vertex in vertices:
            while G.degree[vertex] < 3:
                neighbor = chr(ord('A') + random.randint(0, num_vertices - 1))
                if neighbor != vertex and neighbor not in list(G.neighbors(vertex)):
                    weight = random.randint(1, 10)
                    G.add_edge(vertex, neighbor, weight=weight)

    if k is not None and k > 0:
        if not nx.is_biconnected(G):
            while not nx.is_biconnected(G):
                vertex = random.choice(list(G.nodes()))
                neighbor = random.choice(list(G.nodes()))
                if vertex != neighbor and not G.has_edge(vertex, neighbor):
                    weight = random.randint(1, 10)
                    G.add_edge(vertex, neighbor, weight=weight)

    for vertex in G.nodes():
        num_edges = random.randint(min_edges_per_vertex, min(max_edges_per_vertex, num_vertices - 1))
        for _ in range(num_edges - len(list(G.neighbors(vertex)))):
            neighbor = chr(ord('A') + random.randint(0, num_vertices - 1))
            if neighbor != vertex and neighbor not in list(G.neighbors(vertex)):
                weight = random.randint(1, 10)
                G.add_edge(vertex, neighbor, weight=weight)
    
    print(nx.is_connected(G))   
    return G

def print_graph():
    global i
    i += 1    

def prim_mst(graph, index=0):
    mst = nx.Graph()
    visited = set()  

    start_vertex = list(graph.nodes())[index]
    visited.add(start_vertex)

    min_heap = [(weight['weight'], start_vertex, neighbor) for neighbor, weight in graph.adj[start_vertex].items()]
    heapq.heapify(min_heap)

    while min_heap:
        weight, src, dest = heapq.heappop(min_heap)

        if dest not in visited:
            visited.add(dest)
            mst.add_edge(src, dest, weight=weight)

            for neighbor, weight in graph.adj[dest].items():
                if neighbor not in visited:
                    heapq.heappush(min_heap, (weight['weight'], dest, neighbor))

    return mst

def count_leaves(mst_edges):
    degrees = [val for (_, val) in mst_edges.degree()]
    return sum(1 for v in degrees if v == 1)

def diff(current, k):
    return abs(k - current)

def cycle_util_to_find_leaves(graph, mst, cycle_path, check_edge, curr_leaves, k):
    mst_copy = nx.Graph(mst)
    diff_min = diff(curr_leaves, k)
    for u, v in cycle_path:
        if  check_edge in [(u, v), (v, u)]:
            continue
        cond_add_1_leaf = (len(list(mst.neighbors(u))) == 2 and len(list(mst.neighbors(v))) > 2) or (len(list(mst.neighbors(v))) == 2 and len(list(mst.neighbors(u))) > 2)
        cond = len(list(mst.neighbors(u))) == 2 and len(list(mst.neighbors(v))) == 2 or cond_add_1_leaf 
        if cond:
            copy = nx.Graph(mst)
            copy.remove_edge(u, v)
            counter_check = count_leaves(copy)
            if counter_check == 0:
                continue
            check_diff = diff(counter_check, k)
            if check_diff < diff_min and nx.is_connected(copy):
                diff_min = check_diff
                mst = copy
            print_graph()
            if counter_check == k and nx.is_connected(copy):
                mst = copy
                k = counter_check
                break
        else: 
            continue 
    if nx.utils.misc.graphs_equal(mst, mst_copy):
        u, v = check_edge
        mst_copy.remove_edge(u, v)
        return mst_copy
    return mst

def prim_mst_with_k_leaves(graph, k):
    mst = prim_mst(graph)
    leaves = count_leaves(mst)
    if leaves == k:
        return mst
    elif leaves < k  or leaves > k:
        checked = set()
        if leaves < k:
            print("Less: ", leaves)
        else: 
            print("Greater: ", leaves)
        new_edge = None
        while leaves < k or leaves > k:
            print_graph()
            for u, v in mst.edges():
                for neighbor, weight in graph.adj[u].items():
                    if not mst.has_edge(neighbor, u):
                        if (neighbor, u) in checked or (u, neighbor) in checked:
                            continue
                        new_weight = weight
                        new_edge = (u, neighbor)
                        break
                for neighbor, weight in graph.adj[v].items():
                    if not mst.has_edge(neighbor, v):
                        if (neighbor, v) in checked or (v, neighbor) in checked:
                            continue
                        new_weight = weight
                        new_edge = (v, neighbor)
                        break

            u, v = new_edge
            if not mst.has_edge(u, v) and (u, v) not in checked and (v, u) not in checked:
                u, v = new_edge
                checked.add(new_edge)
                mst.add_edge(u, v, weight=new_weight)
                try:
                    cycle = list(nx.find_cycle(mst, u))
                except nx.exception.NetworkXNoCycle:
                    cycle = False 

                if cycle:
                    mst = cycle_util_to_find_leaves(graph, mst, cycle, new_edge, leaves, k)
                    counter_check = count_leaves(mst)
                else:
                    counter_check = count_leaves(mst)

                if  counter_check > leaves:
                    leaves += 1
                elif counter_check < leaves:
                    leaves -= 1
                if leaves == k:
                    break
            else:
                break

        if leaves == k:
            return mst

    return []

if __name__ == "__main__":
    num_tests = 1
    num_vertices = 10
    k = 5  # количество висячих вершин
    is_regular = False
    connected = False
    for i in range(num_tests):
        if is_regular:
            graph = generate_connected_graph(num_vertices, is_regular=is_regular)
            print("Сгенерированный 3-regular граф:")
            print(round((2 * num_vertices + 4)/9))
        elif connected:
            graph = generate_connected_graph(num_vertices, 2)
            print("Сгенерированный 2-связный граф:")
            print(len(nx.maximal_independent_set(graph))<=2 + k - 1)
        else:
            graph = generate_connected_graph(num_vertices)
            print("Сгенерированный связный граф:")
        for u, v, d in graph.edges(data="weight"):
            print(f"({u} -{[d]}- {v})")
        mst = prim_mst_with_k_leaves(graph, k)
        print_graph()
        if mst:
            print("\nОстовное дерево с {} висячими вершинами:".format(k))
            for edge in mst.edges():
                print(edge)
        else:
            print("\nНевозможно построить остовное дерево с {} висячими вершинами.".format(k))
    print("\n" + "="*50 + "\n")