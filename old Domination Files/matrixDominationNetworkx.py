import networkx as nx
import time as tm
import requests
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import math

def send_pushover_notification(message, title='Code Notification', user_key='u4q5fs89jfxaewvk2a3wudauuv2p4p', app_token='av5sge7omkiuo8mazdk1pkwytsmyf2'):
    """Sends a notification via Pushover.

    Parameters
    ----------
    message: string
        The text of the push notification.
    title: string, optional (default 'Code Notification')
        The title of the push notification.
    user_key: string, optional (default 'u4q5fs89jfxaewvk2a3wudauuv2p4p')
        The unique ID for the user who recieved the message.
    app_token: string, optional (default 'av5sge7omkiuo8mazdk1pkwytsmyf2')
        The unique ID for the application so that a password is not required.

    Returns
    -------
    Nothing

    Outputs
    -------
    Prints to screen if successful or not.
    """
    url = 'https://api.pushover.net/1/messages.json'
    payload = {
        'token': app_token,
        'user': user_key,
        'message': message,
        'title': title
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print('Pushover notification sent successfully!')
    except requests.exceptions.RequestException as e:
        print(f'Error sending Pushover notification: {e}')



def create_prism_graph(m):
    """Create a prism graph consisting of 2 copies of an m-cycle.

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).

    Returns
    -------
    networkx.Graph
        The resulting prism graph with 2m vertices where vertices are labeled:
            Outer cycle: vertices 0, 1, ..., m-1
            Inner cycle: vertices m, m+1, ..., 2m-1

    Outputs
    -------
    Nothing
    """
    G = nx.Graph()
    
    # Add vertices
    outer_vertices = list(range(m))
    inner_vertices = list(range(m, 2*m))
    
    G.add_nodes_from(outer_vertices + inner_vertices)
    
    # Add edges for outer cycle
    for i in range(m):
        G.add_edge(i, (i + 1) % m)
    
    # Add edges for inner cycle
    for i in range(m):
        G.add_edge(m + i, m + (i + 1) % m)
    
    # Add edges connecting outer and inner cycles
    for i in range(m):
        G.add_edge(i, m + i)
    
    return G

def plot_prism_graph(m, figsize=(10, 10), display=True, title=True, save=False):
    """Plot the prism graph with custom positioning
    Vertex 0 at 12 o'clock, clockwise labeling

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    figsize: tuple of two ints, optional (default = (10, 10))
        Sets the size of the figure
    display: bool, optional (default True)
        If True, the image will appear on the screen.
        If False, it will not appear.
    title: bool, optional (default True)
        If True, the image will have a title of 'Prism Graph with m = {m}.'
        If False, no title appears.
    save: bool, optional (default False)
        If True, the image will be saved as 'prism{m}.png'
        If False, the image will not be saved.

    Returns
    -------
    Nothing

    Outputs
    -------
    If display = True, will display the image to the screen.
    """
    G = create_prism_graph(m)
    
    # Create positions for vertices
    pos = {}
    
    # Outer cycle positions (larger radius)
    # Start at 12 o'clock (π/2) and go clockwise (subtract angles)
    outer_radius = 2.0
    for i in range(m):
        angle = np.pi/2 - 2 * np.pi * i / m  # Start from top, go clockwise
        pos[i] = (outer_radius * np.cos(angle), outer_radius * np.sin(angle))
    
    # Inner cycle positions (smaller radius)
    # Same pattern for inner cycle
    inner_radius = 1.0
    for i in range(m):
        angle = np.pi/2 - 2 * np.pi * i / m  # Start from top, go clockwise
        pos[m + i] = (inner_radius * np.cos(angle), inner_radius * np.sin(angle))
    
    # Create the plot
    plt.figure(figsize=figsize)
    
    # Draw edges with medium thickness
    nx.draw_networkx_edges(G, pos, width=2, edge_color='black', alpha=0.7)
    
    # Draw vertices as thin circles
    #nx.draw_networkx_nodes(G, pos, node_color='white', node_size=800, 
    #                      edgecolors='black', linewidths=1)
    # Make the nodes bigger to hold the bigger labels.
    nx.draw_networkx_nodes(G, pos, node_color='white', node_size=1000, 
                          edgecolors='black', linewidths=1)
    
    # Draw labels inside the circles
    #nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    # Make the labels bigger because Brauch is old.
    nx.draw_networkx_labels(G, pos, font_size=24, font_weight='bold')

    if title:
        plt.title(f'Prism Graph with m = {m}', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.axis('off')
    plt.tight_layout()
    
    # Save if requested
    if save:
        filename = f'prism{m}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f'Saved graph as {filename}')

    if display:
        plt.show()

# --- Updated create_stack_prism with detailed comments -----------------------

def create_stack_prism(m, n, cycle=True):
    """Create a *stack prism* consisting of *n* copies of an m-prism.

    Parameters
    ----------
    m: int
       Number of vertices in each ring of a single prism (total 2m per copy).
    n: int
       Number of prism copies to stack.
    cycle: bool, optional (default True)
       If True, connect the last copy back to the first to form a closed cycle
       through corresponding vertices.
       If False, do not connect the last copy back to the first copy

    Returns
    -------
    networkx.Graph
        The resulting stacked prism graph with 2mn vertices.

    Outputs
    -------
    Nothing
    """
    if m <= 0 or n <= 0:
        raise ValueError('m and n must be positive integers')

    stacked = nx.Graph()

    # ------------------------------------------------------------------
    # 1) Build each individual prism and relabel its vertices so that
    #    copy k (0-indexed) occupies labels [2m·k, 2m·(k+1)−1].
    # ------------------------------------------------------------------
    for k in range(n):
        # base prism
        Gk = create_prism_graph(m)
        # map local labels 0..2m−1 to global labels offset by 2m·k
        mapping = {v: v + 2*m*k for v in Gk.nodes()}
        Gk = nx.relabel_nodes(Gk, mapping)
        # merge this copy into the global graph
        stacked = nx.compose(stacked, Gk)

    # ------------------------------------------------------------------
    # 2) Connect corresponding vertices between consecutive copies.
    #    For each vertex position v (0..2m−1) add an edge from copy k
    #    to copy k+1.  If cycle=True also connect last back to first.
    # ------------------------------------------------------------------
    for k in range(n - 1):
        for v in range(2 * m):
            stacked.add_edge(2 * m * k + v, 2 * m * (k + 1) + v)

    if cycle and n > 1:
        for v in range(2 * m):
            stacked.add_edge(v, 2 * m * (n - 1) + v)

    return stacked

# -----------------------------------------------------------------------------
# Plotting helper: position vertices of a single m-prism around two
# concentric circles centred at origin so vertex 0 sits at 12 o'clock.
# -----------------------------------------------------------------------------

def _prism_local_layout(m, outer_r=1.0, inner_r=0.6):
    """Return a dict {vertex_index: (x, y)} for one prism copy.
    Used internally; should not be called directly."""
    layout = {}
    angle_step = 2 * np.pi / m
    for i in range(m):
        theta = np.pi / 2 - i * angle_step  # 12 o'clock then clockwise
        # outer ring vertex i
        layout[i] = (outer_r * np.cos(theta), outer_r * np.sin(theta))
        # inner ring vertex m+i directly inside at same angle
        layout[m + i] = (inner_r * np.cos(theta), inner_r * np.sin(theta))
    return layout

# -----------------------------------------------------------------------------
# Main plotting function for the stacked prism
# -----------------------------------------------------------------------------


def plot_stack_graph(m, n, cycle=True, figsize=(10, 10), display=True,
                     title=True, save=False, label=False):
    """Plot the stacked prism graph with custom positioning
    Vertex 0 at 12 o'clock, clockwise labeling, clockwise copies of prism

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    n: int
       Number of prism copies to stack.
    cycle: bool, optional (default True)
       If True, connect the last copy back to the first to form a closed cycle
       through corresponding vertices.
       If False, do not connect the last copy back to the first copy
    figsize: tuple of two ints, optional (default = (10, 10))
        Sets the size of the figure
    display: bool, optional (default True)
        If True, the image will appear on the screen.
        If False, it will not appear.
    title: bool, optional (default True)
        If True, the image will have a title of 'Prism Graph with m = {m}.'
        If False, no title appears.
    save: bool, optional (default False)
        If True, the image will be saved as 'stack_prism_m(m)_n(n).png'
        If False, the image will not be saved.
    label: bool, optional (default False)
        If True, the index of each vertex will be displayed.
        If False, the vertices will be filled circles.

    Returns
    -------
    Nothing

    Outputs
    -------
    If display = True, will display the image to the screen.
    """
    G = create_stack_prism(m, n, cycle)

    big_R = 3.0
    centre_step = 2*np.pi/n
    local_layout = _prism_local_layout(m, outer_r=0.9, inner_r=0.55)
    pos={}
    for k in range(n):
        phi=np.pi/2 - k*centre_step
        cx,cy=big_R*np.cos(phi), big_R*np.sin(phi)
        for v in range(2*m):
            gv=2*m*k+v
            lx,ly=local_layout[v]
            pos[gv]=(cx+lx, cy+ly)

    # separate edge lists
    intra_edges=[]
    inter_edges=[]
    for u,v in G.edges():
        if u//(2*m)==v//(2*m):
            intra_edges.append((u,v))
        else:
            inter_edges.append((u,v))

    plt.figure(figsize=figsize)

    # draw edges
    nx.draw_networkx_edges(G,pos,edgelist=intra_edges,edge_color='black',width=1.5)
    nx.draw_networkx_edges(G,pos,edgelist=inter_edges,edge_color='red',width=1.5)

    if label:
        # hollow nodes
        nx.draw_networkx_nodes(G,pos,node_size=256,node_color='white',edgecolors='black')
        nx.draw_networkx_labels(G,pos,font_size=8)
    else:
        nx.draw_networkx_nodes(G,pos,node_size=200,node_color='skyblue',edgecolors='black')

    if title:
        plt.title(f'Stacked prism m={m}, n={n}: {"cyclic" if cycle else "path"}')
    plt.axis('off')
    if save:
        fname=f'stack_prism_m{m}_n{n}.png'
        plt.savefig(fname,dpi=300,bbox_inches='tight')
        print('Saved figure to',fname)
    if display:
        plt.show()

def find_undom(graph, fiber1, fiber3):
    """Return intersection of undominated vertices from fiber1 and fiber3.

    Parameters
    ----------
    graph: networkx.Graph
        The graph to analyze.
    fiber1: list[int]
        Vertex subset representing the first fiber.
    fiber3: list[int]
        Vertex subset representing the third fiber.

    Returns
    -------
    list[int]
        Sorted list of vertices that are undominated by both fiber1 and fiber3.

    Outputs
    -------
    Nothing
    """
    # ----- helper to get dominated set for a fiber ---------------------
    def dominated(vertices):
        dom = set()
        for v in vertices:
            dom.update([v])
            dom.update(graph.neighbors(v))
        return dom

    undom1 = set(graph.nodes()).difference(dominated(fiber1))
    undom3 = set(graph.nodes()).difference(dominated(fiber3))

    fiber2 = sorted(undom1.intersection(undom3))
    return fiber2

def find_undom_next(graph, fiber1, fiber2):
    """Return intersection of undominated vertices from fiber1 and fiber3.

    Parameters
    ----------
    graph: networkx.Graph
        The graph to analyze.
    fiber1: list[int]
        Vertex subset representing the first fiber.
    fiber2: list[int]
        Vertex subset representing the second fiber.

    Returns
    -------
    list[int]
        Sorted list of vertices that are undominated in fiber2

    Outputs
    -------
    Nothing
    """
    # ----- helper to get dominated set for a fiber ---------------------
    def dominated(vertices):
        dom = set()
        for v in vertices:
            dom.update([v])
            dom.update(graph.neighbors(v))
        return dom

    undom2 = set(graph.nodes()).difference(dominated(fiber2))

    fiber3 = list(undom2.difference(set(fiber1)))
    fiber3.sort()
    return fiber3

def convert_fibers_stack(m, listOfFibers):
    """Converts a lists of lists representing the vertices in seperate fibers to a
    list of vertices in a stack.

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    listOfFibers: list of lists of int
        The list containing the list of the dominating vertices in each fiber.

    Returns
    -------
    list[int]
        one list of all vertices converted to stack notation

    Outputs
    -------
    Nothing
    """
    vertices = []
    for i, fiber in enumerate(listOfFibers):
        for v in fiber:
            vertices.append(v + (2*m*i))
    vertices.sort()
    return vertices

def fiber_one(m, start=0):
    """From the starting position, finds dominating vertices using the clockwise algorithm
    which is (current + 3) cross from outside to inside or inside to outside.

    Parameters
    ----------
    m: int
        The size of the cycle for the prism
    start: int (optional, default True)
        Where to start for the algorithm

    Returns
    -------
    list[int]
        vertices that nearly dominate the prism based on clockwise algorithm

    Outputs
    -------
    Nothing
    """
    # Start with an listt that contains the start
    domSet = [start]
    # Set the current position to the start
    position = start
    # Count so that you stop when you have "enough"
    count = 1
    # Make sure fiber1 has the right number of vertices
    bound = math.ceil(m/3)
    while count < bound:
        # Apply the clockwise algorithm, with adjustments when you cross 0
        if 0 <= position and position < (m - 3): # Outside Good
            position = position + m + 3
        elif (m - 3) <= position and position < m: # Outside Bad
            position = position + 3
        elif m <= position and position < (2*m - 3): # Inside Good
            position = (position + m + 3) % (2*m)
        else: # Inside Bad
            position = (position + 3) % (2*m)
        domSet.append(position)
        count += 1
    return domSet

def fiber_two(m, fiber1):
    """Use the lowest undominated vertex from fiber1 to do the clockwise
    algorithm starting at that vertex.

    Parameters
    ----------
    m: int
        The size of the cycle for the prism
    fiber1: list[int]
        What is currently dominated in fiber1

    Returns
    -------
    list[int]
        vertices that nearly dominate the prism based on clockwise algorithm

    Outputs
    -------
    Nothing
    """
    # Create the prism graph so we can find what is undominated
    graph = create_prism_graph(m)
    # Helper function to find what is dominated
    def dominated(vertices):
            dom = set()
            for v in vertices:
                dom.update([v])
                dom.update(graph.neighbors(v))
            return dom
    # Find what is undominated by doing vertex - dominated
    undom = list(set(graph.nodes()).difference(dominated(fiber1)))
    # Find the lowest undominated and use the clockwise algorithm
    start = min(undom)
    domSet = fiber_one(m, start)
    # If m = 1 mod 3, then it needs one fewer vertices
    if (m % 3 == 1):
        domSet = domSet[:-1]
    return domSet
    
def m1mod3_subsets(m, n, debug=False):
    """Finds all dominating sets for a *stack prism* consisting of *n* copies
    of an m-prism in a cycle (first and last copies are adjacent).
    LOOKS AT ALL SUBSETS
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 1 mod 3.
    n: int
        Number of prism copies to stack.
        n should be even.
    debug: bool, optional (default False)
        If True, it requires user interaction after every set is created.  This helps
        you kill runaway programs for debugging purposes.
        If False, it runs without user interaction.

    Returns
    -------
    count: the number of dominating sets

    Outputs
    -------
    The dominating sets are written to the file 'm{m}n{n}NxResults.txt'
    """
    if (m % 3) != 1:
        raise ValueError('m must be equivalent to 1 mod 3')
    if (n % 2) != 0:
        raise ValueError('n must be even')
    xOdd = (m+2)//3
    xEven = (m-1)//3
    graph = create_stack_prism(m, n)
    count = 0
    stream = open(f'm{m}n{n}NxResults.txt', 'a')

    # Construct the appropriate sized subsets of the set [0, 2m-1].
    # Since odd and even fibers differ in size of subset.
    subsetsOdd = list(it.combinations(range(2*m), xOdd))
    subsetsEven = list(it.combinations(range(2*m), xEven))

    # The first fiber is special since it must include vertex 0.
    for first in it.combinations(range(1,2*m), xOdd - 1):
        fiber1 = [0] + list(first)
        # Construct the odd fibers by looking at products of combinations of the right size
        for partOdd in it.product(subsetsOdd, repeat=(n//2) - 1):
            # Assign each odd fiber a subset.
            for i in range(n//2 - 1):
                exec(f'fiber{2*i + 3} = list(partOdd[i])')
                # Adjust the vertex index to be between (4i+4)m and (4i+6)m
                exec(f'fiber{2*i + 3} = [x + {(4*i + 4)*m} for x in fiber{2*i + 3}]')
                
            # For each odd fiber, construct the even fibers similarly
            for partEven in it.product(subsetsEven, repeat=(n//2)):
                # Assign each even fiber a subset.
                for j in range(n//2):
                    exec(f'fiber{2*j + 2} = list(partEven[j])')
                    # Adjust the vertex index to be between (4j+2)m and (4j+4)m
                    exec(f'fiber{2*j + 2} = [y + {(4*j + 2)*m} for y in fiber{2*j + 2}]')

                # Combine the values of the fibers to make one long list.
                finalSet = []
                for k in range(1, n + 1):
                    finalSet += eval(f'fiber{k}')
                    
                # Check if the list is a dominating set and if so, record the string version to the file.
                result = nx.is_dominating_set(graph, finalSet)
                if result:
                    count += 1
                    print(finalSet)
                    stream.write(str(finalSet)+"\n")
                    
                # Require interaction if debugging to prevent runaway code
                if debug:
                    input(f'Press enter to check {finalSet}.')
                    print(f'\t{result}')

    # Write the count to the file then close it. This ensures if there are no dominating sets, something is written.
    stream.write(f'Done. Count: {count}.\n')
    stream.close()
    return count

def m1mod3_undom(m, n, debug=False, first_notify = True):
    """Finds all dominating sets for a *stack prism* consisting of *n* copies
    of an m-prism in a cycle (first and last copies are adjacent).
    USES LISTS FOR FIBERS AND HELPER FOR EVEN FIBERS
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 1 mod 3.
    n: int
        Number of prism copies to stack.
        n should be even.
    debug: bool, optional (default False)
        If True, it requires user interaction after every set is created.  This helps
        you kill runaway programs for debugging purposes.
        If False, it runs without user interaction.

    Returns
    -------
    count: the number of dominating sets

    Outputs
    -------
    The dominating sets are written to the file 'm{m}n{n}NxResults.txt'
    """
    if (m % 3) != 1:
        raise ValueError('m must be equivalent to 1 mod 3')
    if (n % 2) != 0:
        raise ValueError('n must be even')
    xOdd = (m+2)//3
    xEven = (m-1)//3
    graph_fiber = create_prism_graph(m)
    graph = create_stack_prism(m, n)
    count = 0
    sent = False
    stream = open(f'm{m}n{n}NxResults3.txt', 'a')

    # Construct the appropriate sized subsets of the set [0, 2m-1].
    # Since odd and even fibers differ in size of subset.
    subsetsOdd = list(it.combinations(range(2*m), xOdd))
    subsetsEven = list(it.combinations(range(2*m), xEven))
    fibers = [list()]*(n+1)

    # Construct the even fibers by finding undominated of odd neighbor
    # Helper function to stop if fiber is wrong size and move to next iteration
    def even_fibers():
        last_odd = [x % (2*m) for x in fibers[n - 1]]
        fibers[n] = find_undom(graph_fiber, fibers[1], last_odd)
        fibers[n] = [y + (((2*n) - 2)*m) for y in fibers[n]]
        for j in range((n//2) - 1):
            current = (2*j) + 2
            prev_fiber = [x % (2*m) for x in fibers[current - 1]]
            next_fiber = [x % (2*m) for x in fibers[current + 1]]
            fibers[current] = find_undom(graph_fiber, prev_fiber, next_fiber)
            if (len(fibers[current]) != (m-1)//3):
                return (False, [])
            # Adjust the vertex index to be between (4j+2)m and (4j+4)m
            fibers[current] = [y + ((4*j + 2)*m) for y in fibers[2*j + 2]]
        # If correct sizes, combine the values of the fibers to make one long list.
        finalSet = []
        for k in range(1, n + 1):
            finalSet += fibers[k]
        return (True, finalSet)


    # The first fiber is special since it must include vertex 0.
    for first in it.combinations(range(1,2*m), xOdd - 1):
        fibers[1] = [0] + list(first)
        # Construct the odd fibers by looking at products of combinations of the right size
        #for partOdd in it.product(subsetsOdd, repeat=(n//2) - 1):
        for partOdd in it.permutations(subsetsOdd, (n//2) - 1):
            # Assign each odd fiber a subset.
            for i in range(n//2 - 1):
                fibers[2*i + 3] = list(partOdd[i])
                # Adjust the vertex index to be between (4i+4)m and (4i+6)m
                fibers[2*i + 3] = [x + ((4*i + 4)*m) for x in fibers[2*i + 3]]
                
            # Check if the list is a dominating set and if so, record the string version to the file.
            result_fiber = even_fibers()
            if result_fiber[0]:
                result = nx.is_dominating_set(graph, result_fiber[1])
                if result:
                    count += 1
                    print(result_fiber[1])
                    stream.write(str(result_fiber[1])+"\n")
                    if not sent and first_notify:
                        message = f'm={m}, n={n} found the first: {result_fiber[1]}.'
                        send_pushover_notification(message)
                        sent = True
                
                # Require interaction if debugging to prevent runaway code
                if debug:
                    input(f'Press enter to check {result_fiber[1]}.')
                    print(f'\t{result}')
            else:
                pass

    # Write the count to the file then close it. This ensures if there are no dominating sets, something is written.
    stream.write(f'Done. Count: {count}.\n')
    stream.close()
    return count

def m1mod3_completer(m, fiber1, fiber2):
    """Uses the first two fibers to find a dominating set for the cyclic stacked prism
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 1 mod 3.
    fiber1: list[int]
        A list of vertices for the dominating set for the first fiber
    fiber2: list[int]
        A list of vertices for the dominated set for the second fiber

    Returns
    -------
    (boolean, int, list[lists])
        boolean is True or False depending on whether a dominating set can be constructed
            from fiber1 and fiber2
        int is the number of fibers for the stack before it repeats
        list[lists] is a list of vertices in each fiber using the convention that the outer
            cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    Nothing
    """
    # Construct the prism for m
    graph = create_prism_graph(m)
    # Keep track of what we have.
    sequence_so_far = [set(fiber1), set(fiber2)]
    # Keep going until we start to repeat
    cont = True
    # We will have three fibers: prev, current, next that will iterate until repeat
    prev_fiber = fiber1
    current_fiber = fiber2
    while cont:
        # Construct what has to be in the next fiber
        next_fiber = find_undom_next(graph, prev_fiber, current_fiber)
        # If it is new, add it then iterate to the next pair of fibers
        if set(next_fiber) not in sequence_so_far:
            sequence_so_far.append(set(next_fiber))
            prev_fiber, current_fiber = current_fiber, next_fiber
        # if it’s already there, then we’re repeating and are done
        # in reality, it should be equal to fiber1 when it starts to repeat
        else:
            n = len(sequence_so_far)
            # Create stack of prisms
            stack = create_stack_prism(m, n)
            domSet = convert_fibers_stack(m, sequence_so_far)
            result = nx.is_dominating_set(stack, domSet)
            return (result, n, sequence_so_far)

def m2mod3_completer(m, fiber1, fiber2):
    """Uses the first two fibers to find a dominating set for the cyclic stacked prism
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 2 mod 3.
    fiber1: list[int]
        A list of vertices for the dominating set for the first fiber
    fiber2: list[int]
        A list of vertices for the dominated set for the second fiber

    Returns
    -------
    (boolean, int, list[lists])
        boolean is True or False depending on whether a dominating set can be constructed
            from fiber1 and fiber2
        int is the number of fibers for the stack before it repeats
        list[lists] is a list of vertices in each fiber using the convention that the outer
            cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    Nothing
    """
    # For 2 mod 3, it can be done in 3 fibers.  Just find the third fiber.
    # Third fiber starts at m+1
    fiber3 = fiber_one(m, m+1)
    sequence_so_far = [set(fiber1), set(fiber2), set(fiber3)]
    n = len(sequence_so_far)
    # Create stack of prisms
    stack = create_stack_prism(m, n)
    # Make the dominating set
    domSet = convert_fibers_stack(m, sequence_so_far)
    #Check that it dominates
    result = nx.is_dominating_set(stack, domSet)
    return (result, n, sequence_so_far)

def solver(m, save=False):
    """Finds a dominating set for stacked prisms when m = 1 (mod 3)
    and m = 2 (mod 3)

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 2 mod 3.
    save: bool, optional (default False)
        If True, the data will be saved to a file
        If False, the data will only appear on screen

    Returns
    -------
    (boolean, int, list[lists])
        boolean is True or False depending on whether a dominating set can be constructed
        int is the number of fibers for the stack before it repeats
        list[lists] is a list of vertices in each fiber using the convention that the outer
            cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    If save is True The dominating sets are written to the file 'Solver_m{m}_n{n}.txt'
    """
    # Construct the "standard" fiber1
    fiber1 = fiber_one(m)
    # Construct the "standard" fiber2
    if (m % 6 == 3):
        fiber2 = fiber_one(m, 2*m - 1)
    else:
        fiber2 = fiber_two(m, fiber1)
    # Choose which completer to use
    #if (m % 3 == 1):
    #    result = m1mod3_completer(m, fiber1, fiber2)
    #elif (m % 3 == 2):
    #    result = m2mod3_completer(m, fiber1, fiber2)
    # Future work: m1mod3_completer(m, fiber1, fiber2)
    if (m % 3 == 2):
        result = m2mod3_completer(m, fiber1, fiber2)
    elif (m % 3 == 1) or (m % 3 == 0):
        result = m1mod3_completer(m, fiber1, fiber2)
    else:
        result = (False, 0, [[]])
    if save:
        file = f'Solver_m{m}_n{result[1]}.txt'
        output = f'm: {m}\nn: {result[1]}\ndomSetStack = {convert_fibers_stack(m, result[2])}\ndomSetFibers = {result[2]}'
        stream = open(file, 'w')
        stream.write(output)
        stream.close()
    return result
    
    


##m = 7
##n = 96
##print(f'Starting m={m}, n={n}.')
##start = tm.time()
##try:
##    count = m1mod3_undom(m, n)
##    end = tm.time()
##    message = f'm={m}, n={n} is finished. It took {end - start} seconds. Found {count} dominating sets.'
##    print(message)
##    send_pushover_notification(message)
##except Exception as e:
##    print(e)
##    end2 = tm.time()
##    send_pushover_notification(f'Failed. m={m}, n={n} took {end2-start} seconds.')
