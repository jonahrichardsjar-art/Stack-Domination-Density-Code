import networkx as nx
import time as tm
import requests
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
import math

##----------------------------------------------------------------------
##  Code for sending push messages
##  The default user_key is Brauch's account.
##  The default app_token is Python for Brauch
##----------------------------------------------------------------------

def send_pushover_notification(message, title='Code Notification',
                               user_key='u4q5fs89jfxaewvk2a3wudauuv2p4p',
                               app_token='av5sge7omkiuo8mazdk1pkwytsmyf2'):
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

##----------------------------------------------------------------------
##  Code for constructing prisms and prism stacks
##  Contains functions:
##      create_prism_graph
##      create_stack_prism
##----------------------------------------------------------------------

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

def create_stack_prism(m, n, cycle=True):
    """Create a stacked prism graph consisting of n copies of m-prisms.

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
        The resulting stacked prism graph with 2mn vertices where vertices are labeled:
            Copy k: Outer cycle (2mk), (2mk) + (1), ..., (2mk) + (m-1)
                    Inner cycle: (2mk) + (m), (2mk) + (m+1), ..., (2mk) + (2m-1)

    Outputs
    -------
    Nothing
    """
    G = nx.Graph()
    
    # Add all vertices
    total_vertices = 2 * m * n
    G.add_nodes_from(range(total_vertices))
    
    # Add edges within each prism copy
    for k in range(n):
        base = 2 * m * k
        
        # Add edges for outer cycle of copy k
        for i in range(m):
            u = base + i
            v = base + (i + 1) % m
            G.add_edge(u, v)
        
        # Add edges for inner cycle of copy k
        for i in range(m):
            u = base + m + i
            v = base + m + (i + 1) % m
            G.add_edge(u, v)
        
        # Add edges connecting outer and inner cycles of copy k
        for i in range(m):
            u = base + i
            v = base + m + i
            G.add_edge(u, v)
    
    # Add edges between consecutive copies
    for k in range(n - 1):
        base_k = 2 * m * k
        base_k1 = 2 * m * (k + 1)
        
        # Connect corresponding vertices
        for i in range(2 * m):
            u = base_k + i
            v = base_k1 + i
            G.add_edge(u, v)
    
    # If cycle is True, connect last copy back to first
    if cycle and n > 1:
        base_last = 2 * m * (n - 1)
        base_first = 0
        
        for i in range(2 * m):
            u = base_last + i
            v = base_first + i
            G.add_edge(u, v)

    return G

##----------------------------------------------------------------------
##  Code for creating images of prisms and prism stacks
##  Contains functions:
##      plot_prism_graph
##          [create_prism_graph]
##      _prism_local_layout [internal function]
##      plot_stack_graph
##          [create_stack_prism]
##      plot_prism_graph_tikz
##          [create_prism_graph]
##      plot_stack_graph_tikz
##          [create_stack_prism]
##----------------------------------------------------------------------

def plot_prism_graph(m, domSet=[], figsize=(10, 10), display=True, title=True,
                     save=False, label=True):
    """Plot the prism graph with custom positioning
    Vertex 0 at 12 o'clock, clockwise labeling

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    domSet: list, optional (default [])
        List of vertex indices to highlight in orange color.
        All other vertices will be displayed in lightblue.
    figsize: tuple of two ints, optional (default = (10, 10))
        Sets the size of the figure
    display: bool, optional (default True)
        If True, the image will appear on the screen.
        If False, it will not appear.
    title: bool, optional (default True)
        If True, the image will have a title of 'Prism Graph with m = {m}.'
        If False, no title appears.
    save: bool, optional (default False)
        If True, the image will be saved
        If False, the image will not be saved.
    label: bool, optional (default True)
        If True, vertex labels will be displayed.
        If False, no vertex labels will be shown.

    Returns
    -------
    Nothing

    Outputs
    -------
    If display=True, will display the image to the screen.
    If save=True, will save a copy of the image as 'prism_m{m}.png' and print confirmation
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

    # Set the colors for the components.  You can use [0-1, 0-1, 0-1]
    # or named colors.
    in_set = [1.00, 0.65, 0.00] # Set the color for dominatING vertices
    not_in_set = [0.70, 0.75, 0.90] # Set color for dominatED vertices
    intra = [0.00, 0.00, 0.00] # Set color for intRAprism edges
    
    # Create node colors based on domSet
    node_colors = []
    for node in G.nodes():
        if node in domSet:
            node_colors.append(in_set)
        else:
            node_colors.append(not_in_set)
    
    # Create the plot
    plt.figure(figsize=figsize)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color=intra, width=2)
    
    # Draw nodes with appropriate colors
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=500, edgecolors='black')
    
    # Draw labels only if label=True
    if label:
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    
    if title:
        plt.title(f'Prism Graph with m = {m}', fontsize=16, fontweight='bold')
    
    plt.axis('off')
    
    if save:
        plt.savefig(f'prism_m{m}.png', dpi=300, bbox_inches='tight')
        print(f'Saved figure as prism_m{m}.png')
    
    if display:
        plt.show()

def _prism_local_layout(m, outer_r=1.0, inner_r=0.6):
    """Helper function to create local layout for a single prism"""
    pos = {}
    
    # Outer cycle positions
    for i in range(m):
        angle = np.pi/2 - 2 * np.pi * i / m
        pos[i] = (outer_r * np.cos(angle), outer_r * np.sin(angle))
    
    # Inner cycle positions
    for i in range(m):
        angle = np.pi/2 - 2 * np.pi * i / m
        pos[m + i] = (inner_r * np.cos(angle), inner_r * np.sin(angle))
    
    return pos

def plot_stack_graph(m, n, domSet=[], cycle=True, figsize=(10, 10),
                     display=True, title=True, save=False, label=False):
    """Plot the stacked prism graph with custom positioning
    Vertex 0 at 12 o'clock, clockwise labeling, clockwise copies of prism

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    n: int
        Number of prism copies to stack.
    domSet: list of int, optional (default [])
        List of vertex indices to highlight with a different color.
        If empty, all vertices use the default color.
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
    If save = True, will save a copy of the image as 'stack_prism_m{m}_n{n}.png' and print confirmation
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

    # Set the colors for the components.  You can use [0-1, 0-1, 0-1]
    # or named colors.
    in_set = [1.00, 0.65, 0.00] # Set the color for dominatING vertices
    not_in_set = [0.70, 0.75, 0.90] # Set color for dominatED vertices
    intra = [0.00, 0.00, 0.00] # Set color for intRAprism edges
    inter = [1.00, 0.00, 0.00] # Set color for intERprism edges

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
    nx.draw_networkx_edges(G,pos,edgelist=intra_edges,edge_color=intra,width=1.5)
    nx.draw_networkx_edges(G,pos,edgelist=inter_edges,edge_color=inter,width=1.5)

    # Prepare node colors based on domSet
    node_colors = []
    all_nodes = list(G.nodes())
    
    for node in all_nodes:
        if node in domSet:
            node_colors.append(in_set)  # Highlight color for domSet vertices
        else:
            node_colors.append(not_in_set)  # Default color

    if label:
        # hollow nodes with colors
        nx.draw_networkx_nodes(G,pos,node_size=256,node_color=node_colors,edgecolors='black')
        nx.draw_networkx_labels(G,pos,font_size=8)
    else:
        nx.draw_networkx_nodes(G,pos,node_size=200,node_color=node_colors,edgecolors='black')

    if title:
        plt.title(f'Stacked prism m={m}, n={n}: {"cyclic" if cycle else "path"}')
    plt.axis('off')
    if save:
        fname=f'stack_prism_m{m}_n{n}.png'
        plt.savefig(fname,dpi=300,bbox_inches='tight')
        print('Saved figure to',fname)
    if display:
        plt.show()

def plot_prism_graph_tikz(m, domSet=[], figsize=(10, 10), title=True, label=True):
    """Generate TikZ LaTeX code for the prism graph with custom positioning
    Vertex 0 at 12 o'clock, clockwise labeling

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    domSet: list, optional (default [])
        List of vertex indices to highlight in orange color.
        All other vertices will be displayed in lightblue.
    figsize: tuple of two ints, optional (default = (10, 10))
        Sets the scale of the figure (affects coordinate scaling)
    title: bool, optional (default True)
        If True, the LaTeX will include a title 'Prism Graph with m = {m}.'
        If False, no title appears.
    label: bool, optional (default True)
        If True, vertex labels will be displayed.
        If False, no vertex labels will be shown.

    Returns
    -------
    Nothing

    Outputs
    -------
    Creates a file f'tikz_prism_m{m}.tex' containing TikZ LaTeX code.
    Prints confirmation to the screen.
    """
    
    # Create the graph structure
    G = create_prism_graph(m)
    
    # Calculate scale factor based on figsize
    scale_factor = min(figsize) / 10.0
    
    # Create positions for vertices
    pos = {}
    
    # Outer cycle positions (larger radius)
    # Start at 12 o'clock (π/2) and go clockwise (subtract angles)
    outer_radius = 2.0 * scale_factor
    for i in range(m):
        angle = np.pi/2 - 2 * np.pi * i / m  # Start from top, go clockwise
        pos[i] = (outer_radius * np.cos(angle), outer_radius * np.sin(angle))
    
    # Inner cycle positions (smaller radius)
    # Same pattern for inner cycle
    inner_radius = 1.0 * scale_factor
    for i in range(m):
        angle = np.pi/2 - 2 * np.pi * i / m  # Start from top, go clockwise
        pos[m + i] = (inner_radius * np.cos(angle), inner_radius * np.sin(angle))
    
    # Start building the TikZ code
    tikz_code = []

    #Format the labels to be displayed
    custom_labels = {}
    for v in range(m):
        custom_labels[v] = f'$v_{{r, {v}}}$'
        custom_labels[v+m] = f'$u_{{r, {v}}}$'
    
    # Document header and packages
    tikz_code.append("\\documentclass{standalone}")
    tikz_code.append("\\usepackage{tikz}")
    tikz_code.append("\\begin{document}")
    tikz_code.append("\\begin{document}")
    tikz_code.append("\\begin{figure}")
    tikz_code.append("\\begin{tikzpicture}")
    
    # Define colors
    #########################################################################
    ## Change from RGB to rgb so it uses the same format 0-1 as matplotlib ##
    ## Then merge this with other where tikz is an optional parameter      ##
    #########################################################################
    tikz_code.append("\\definecolor{in_set}{RGB}{255,165,0}") # Set the color for dominatING vertices
    tikz_code.append("\\definecolor{not_in_set}{RGB}{173,216,230}") # Set color for dominatED vertices
    tikz_code.append("\\definecolor{intra}{RGB}{0, 0, 0}") # Set color for intRAprism edges
    
    # Draw edges first (so they appear behind nodes)
    tikz_code.append("% Edges")
    for edge in G.edges():
        u, v = edge
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        tikz_code.append(f"\\draw[thick, intra] ({x1:.3f},{y1:.3f}) -- ({x2:.3f},{y2:.3f});")
    
    # Draw nodes
    tikz_code.append("% Nodes")
    for node in G.nodes():
        x, y = pos[node]
        
        # Determine node color
        if node in domSet:
            color = "in_set"
        else:
            color = "not_in_set"
        
        # Draw the node
        tikz_code.append(f"\\node[circle, draw=black, fill={color}, minimum size=0.4cm] at ({x:.3f},{y:.3f}) {{{custom_labels[node] if label else ''}}};")
    
    # Add title if requested
    if title:
        # Calculate title position (above the graph)
        max_y = max(pos[i][1] for i in range(2*m))
        title_y = max_y + 0.8 * scale_factor
        tikz_code.append(f"% Title")
        tikz_code.append(f"%\\node[font=\\Large\\bfseries] at (0,{title_y:.3f}) {{Prism Graph with m = {m}}};")
    
    # Close TikZ environment
    tikz_code.append("\\end{tikzpicture}")
    tikz_code.append("\\caption{Your Caption!}")
    tikz_code.append("\\label{Fig:cap}")
    tikz_code.append("\\end{figure}")
    tikz_code.append("\\end{document}")
    
    # Write to file
    filename = f'tikz_prism_m{m}.tex'
    with open(filename, 'w') as f:
        f.write('\n'.join(tikz_code))
    
    print(f"TikZ LaTeX code saved to '{filename}'")
    print(f"The file contains {len(tikz_code)} lines of LaTeX/TikZ code")
    

def plot_stack_graph_tikz(m, n, domSet=[], cycle=True, figsize=(10, 10), title=True, label=True):
    """Generate TikZ LaTeX code for the stacked prism graph with custom positioning
    Vertex 0 at 12 o'clock, clockwise labeling, clockwise copies of prism

    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
    n: int
        Number of prism copies to stack.
    domSet: list, optional (default [])
        List of vertex indices to highlight in orange color.
        All other vertices will be displayed in lightblue.
    cycle: bool, optional (default True)
       If True, connect the last copy back to the first to form a closed cycle
       through corresponding vertices.
       If False, do not connect the last copy back to the first copy
    figsize: tuple of two ints, optional (default = (10, 10))
        Sets the scale of the figure (affects coordinate scaling)
    title: bool, optional (default True)
        If True, the LaTeX will include a title.
        If False, no title appears.
    label: bool, optional (default True)
        If True, vertex labels will be displayed.
        If False, no vertex labels will be shown.

    Returns
    -------
    Nothing

    Outputs
    -------
    Creates a file f'tikz_stack_m{m}_n{n}.tex' containing TikZ LaTeX code.
    Prints confirmation to the screen.
    """

    # Create the graph structure
    G = create_stack_prism(m, n, cycle)
    
    # Calculate scale factor based on figsize
    scale_factor = min(figsize) / 10.0
    
    # Create positions for vertices using same logic as plot_stack_graph
    big_R = 3.0 * scale_factor
    centre_step = 2*np.pi/n
    # You might need to adjust the _r values to make the picture look nice.
    #local_layout = _prism_local_layout(m, outer_r=0.9*scale_factor, inner_r=0.55*scale_factor)
    local_layout = _prism_local_layout(m, outer_r=1.1*scale_factor, inner_r=0.55*scale_factor)
    pos = {}
    
    for k in range(n):
        phi = np.pi/2 - k*centre_step
        cx, cy = big_R*np.cos(phi), big_R*np.sin(phi)
        for v in range(2*m):
            gv = 2*m*k + v
            lx, ly = local_layout[v]
            pos[gv] = (cx + lx, cy + ly)
    
    # Separate edge lists (same as original function)
    intra_edges = []
    inter_edges = []
    for u, v in G.edges():
        if u//(2*m) == v//(2*m):
            intra_edges.append((u, v))
        else:
            inter_edges.append((u, v))
    
    # Start building the TikZ code
    tikz_code = []

    # Format the labels to be displayed
    custom_labels = {}
    for r in range(1, n+1):
        for v in range(m):
            custom_labels[v + (r-1)*(2*m)] = f'$v_{{{r}, {v}}}$'
            custom_labels[v+m + (r-1)*(2*m)] = f'$u_{{{r}, {v}}}$'
            
    # Document header and packages
    tikz_code.append("\\documentclass{standalone}")
    tikz_code.append("\\usepackage{tikz}")
    tikz_code.append("\\begin{document}")
    tikz_code.append("\\begin{figure}")
    tikz_code.append("\\begin{tikzpicture}")
    
    # Define colors
    #########################################################################
    ## Change from RGB to rgb so it uses the same format 0-1 as matplotlib ##
    ## Then merge this with other where tikz is an optional parameter      ##
    #########################################################################
    tikz_code.append("\\definecolor{in_set}{RGB}{255,165,0}") # Set the color for dominatING vertices
    tikz_code.append("\\definecolor{not_in_set}{RGB}{173,216,230}") # Set color for dominatED vertices
    tikz_code.append("\\definecolor{intra}{RGB}{0, 0, 0}") # Set color for intRAprism edges
    tikz_code.append("\\definecolor{inter}{RGB}{255,0,0}") # Set color for intERprism edges
    
    # Draw edges first (so they appear behind nodes)
    tikz_code.append("% Intra-prism edges")
    for edge in intra_edges:
        u, v = edge
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        tikz_code.append(f"\\draw[thick, intra] ({x1:.3f},{y1:.3f}) -- ({x2:.3f},{y2:.3f});")
    
    tikz_code.append("% Inter-prism edges")
    for edge in inter_edges:
        u, v = edge
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        tikz_code.append(f"\\draw[thick, inter] ({x1:.3f},{y1:.3f}) -- ({x2:.3f},{y2:.3f});")
    
    # Draw nodes
    tikz_code.append("% Nodes")
    for node in G.nodes():
        x, y = pos[node]
        
        # Determine node color
        if node in domSet:
            color = "in_set"
        else:
            color = "not_in_set"
        
        # Draw the node
        tikz_code.append(f"\\node[circle, draw=black, fill={color}, minimum size=0.3cm] at ({x:.3f},{y:.3f}) {{{custom_labels[node] if label else ''}}};")
    
    # Add title if requested
    if title:
        # Calculate title position (above the graph)
        max_y = max(pos[i][1] for i in range(2*m*n))
        title_y = max_y + 1.0 * scale_factor
        cycle_text = "with cycle" if cycle else "without cycle"
        tikz_code.append(f"% Title")
        tikz_code.append(f"%\\node[font=\\Large\\bfseries] at (0,{title_y:.3f}) {{Stacked Prism Graph: m={m}, n={n} {cycle_text}}};")
    
    # Close TikZ environment
    tikz_code.append("\\end{tikzpicture}")
    tikz_code.append("\\caption{Your Caption!}")
    tikz_code.append("\\label{Fig:cap}")
    tikz_code.append("\\end{figure}")
    tikz_code.append("\\end{document}")
    
    # Write to file
    filename = f'tikz_stack_m{m}_n{n}.tex'
    with open(filename, 'w') as f:
        f.write('\n'.join(tikz_code))
    
    print(f"TikZ LaTeX code saved to '{filename}'")
    print(f"The file contains {len(tikz_code)} lines of LaTeX/TikZ code")
    print(f"Graph parameters: m={m}, n={n}, cycle={cycle}")

##----------------------------------------------------------------------
##  Helper functions for finding dominating sets.
##  Contains functions:
##      dominated
##      find_undom_between
##          [dominated]
##      find_undom_next
##          [dominated]
##      convert_fibers_stack
##      fiber_one ## This is the Clockwise algorithm
##      fiber_two
##          [create_prism_graph]
##          [dominated]
##----------------------------------------------------------------------

def dominated(graph, domSet):
    """Return a set dominatED vertices from the dominatING set.  Works for
    any Networkx graph.

    Parameters
    ----------
    graph: networkx.Graph
        The graph to analyze.
    domSet: list[int]

    Returns
    -------
    set[int]
        set of dominatED vertices

    Outputs
    -------
    Nothing
    """
    dominated = set()
    
    # Every vertex in domSet and neighbors are dominated
    for v in domSet:
        dominated.update([v])
        dominated.update(graph.neighbors(v))
    return dominated

def find_undom_between(graph, fiber1, fiber3):
    """Return vertices from fiber2 that are not dominated by fiber1 or fiber3
    where fiber1 comes before fiber2 and fiber3 comes after fiber2. Graph should
    be a single fiber in a stacked graph.

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
    # Find what is undominated from previous and next neighbor
    undom1 = set(graph.nodes()).difference(dominated(graph, fiber1))
    undom3 = set(graph.nodes()).difference(dominated(graph, fiber3))

    # What is in common is undominated in fiber2
    fiber2 = sorted(undom1.intersection(undom3))
    return fiber2

def find_undom_next(graph, fiber1, fiber2):
    """Return vertices from fiber2 that are not dominated by fiber1 or fiber2
    and need to be dominated in fiber3.  Graph should be a single fiber in a
    stacked graph.

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
    # Find the vertices not directly dominated in fiber2
    undom2 = set(graph.nodes()).difference(dominated(graph, fiber2))
    
    # Remove vertices that are dominated by fiber1
    fiber3 = sorted(undom2.difference(set(fiber1)))
    return fiber3

def convert_fibers_stack(m, listOfFibers):
    """Converts a lists of lists representing the vertices in seperate fibers to a
    list of vertices in an m-cyclic prism stack.

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
    
    # Adjust the index for each fiber
    for i, fiber in enumerate(listOfFibers):
        for v in fiber:
            vertices.append(v + (2*m*i))

    # Make sure they are in order (why? Why not?!)
    vertices.sort()
    return vertices

def fiber_one(m, start=0):
    """From the starting position, finds dominating vertices of the m-cyclic
    prism using the clockwise algorithm which is (current + 3) cross from
    outside to inside or inside to outside.  Works only for m-cyclic prism
    graphs.

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
    # Start with an list that contains the start
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
    """Finds dominating vertices of the m-cyclic prism using the clockwise
    algorithm starting at the lowest labeled vertex that is undominated by
    fiber1.  Works only for stacked m-cyclic prism graphs.

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
    
    # Find what is undominated by doing vertex - dominated
    undom = list(set(graph.nodes()).difference(dominated(graph, fiber1)))
    
    # Find the lowest undominated and use the clockwise algorithm
    start = min(undom)
    domSet = fiber_one(m, start)
    
    # If m = 1 mod 3, then it needs one fewer vertices
    if (m % 3 == 1):
        domSet = domSet[:-1]
    return domSet

##----------------------------------------------------------------------
##  Exhaustive searches for dominating sets.
##  Contains functions:
##      m1mod3_subsets
##          [create_stack_prism]
##      m1mod3_undom
##          [create_prism_graph]
##          [create_stack_prism]
##          [find_undom_between]
##          [_even_fibers, interal]
##----------------------------------------------------------------------
    
def m1mod3_subsets(m, n, debug=False):
    """Finds all dominating sets for a *stack prism* consisting of *n* copies
    of an m-cyclic prism cycle (first and last copies are adjacent).
    LOOKS AT ALL SUBSETS - Roughly big-oh(m!n!)
    
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
    The dominating sets are printed to the screen.
    The dominating sets are written to the file 'NxSubset_m{m}_n{n}.txt'
    """
    # Check that m & n are correctly specified
    if (m % 3) != 1:
        raise ValueError('m must be equivalent to 1 mod 3')
    if (n % 2) != 0:
        raise ValueError('n must be even')
    
    # Initialize some parameters
    xOdd = (m+2)//3
    xEven = (m-1)//3
    graph = create_stack_prism(m, n)
    count = 0
    stream = open(f'NxSubset_m{m}_n{n}.txt', 'a')

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

def m1mod3_undom(m, n):
    """Finds all dominating sets for a *stack prism* consisting of *n* copies
    of an m-cyclic prism cycle (first and last copies are adjacent).
    USES LISTS FOR FIBERS AND HELPER FOR EVEN FIBERS - Roughly big-oh(m!n)
    
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
    The dominating sets are printed to the screen.
    The dominating sets are written to the file 'NxUndom_m{m}_n{n}.txt'
    """
    # Check that m & n are correctly specified
    if (m % 3) != 1:
        raise ValueError('m must be equivalent to 1 mod 3')
    if (n % 2) != 0:
        raise ValueError('n must be even')

    # Initialize some parameters
    xOdd = (m+2)//3
    xEven = (m-1)//3
    graph_fiber = create_prism_graph(m)
    graph = create_stack_prism(m, n)
    count = 0
    stream = open(f'NxUndom_m{m}_n{n}.txt', 'a')

    # Construct the appropriate sized subsets of the set [0, 2m-1].
    # Since odd and even fibers differ in size of subset.
    subsetsOdd = list(it.combinations(range(2*m), xOdd))
    subsetsEven = list(it.combinations(range(2*m), xEven))
    fibers = [list()]*(n+1)

    # Construct the even fibers by finding undominated of odd neighbors
    # Helper function to stop if fiber is wrong size and move to next iteration
    def _even_fibers():
        last_odd = [x % (2*m) for x in fibers[n - 1]]
        fibers[n] = find_undom_between(graph_fiber, fibers[1], last_odd)
        fibers[n] = [y + (((2*n) - 2)*m) for y in fibers[n]]
        for j in range((n//2) - 1):
            current = (2*j) + 2
            prev_fiber = [x % (2*m) for x in fibers[current - 1]]
            next_fiber = [x % (2*m) for x in fibers[current + 1]]
            fibers[current] = find_undom_between(graph_fiber, prev_fiber, next_fiber)
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
            result_fiber = _even_fibers()
            if result_fiber[0]:
                result = nx.is_dominating_set(graph, result_fiber[1])
                if result:
                    count += 1
                    print(result_fiber[1])
                    stream.write(str(result_fiber[1])+"\n")

    # Write the count to the file then close it. This ensures if there are no dominating sets, something is written.
    stream.write(f'Done. Count: {count}.\n')
    stream.close()
    return count

##----------------------------------------------------------------------
##  Algorithmically generated dominating sets.
##  Contains functions:
##      m1mod3_completer
##          [create_prism_graph]
##          [find_undom_next]
##          [create_stack_prism]
##          [convert_fibers_stack]
##      m2mod3_completer
##          [fiber_one]
##          [create_stack_prism]
##          [convert_fibers_stack]
##      solver
##          [fiber_one]
##          [fiber_two]
##          [m2mod3_completer]
##          [m1mod3_completer]
##          [convert_fibers_stack]
##----------------------------------------------------------------------

def m1mod3_completer(m, fiber1, fiber2):
    """Uses the first two fibers to find a dominating set for the cyclic stacked prism
    when m = 0, 1 mode 3.
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 0, 1 mod 3.
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
        list[sets] is a list of sets of vertices in each fiber using the convention that
            the outer cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to
            (2m-1)

    Outputs
    -------
    Nothing
    """
    # Check for appropriate size of m
    if ((m % 3) != 0) and ((m % 3) != 1):
        raise ValueError('m must be equivalent to 0, 1 mod 3. Perhaps you mean m2mod3_completer? ')
    
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
            
            # Must append sets to ensure clockwise and counterclockwise walks are the same
            sequence_so_far.append(set(next_fiber))
            prev_fiber, current_fiber = current_fiber, next_fiber
            
        # if it’s already there, then we’re repeating and are done
        # in reality, it should be equal to fiber1 when it starts to repeat
        else:
            n = len(sequence_so_far)
            
            # Create stack of prisms
            stack = create_stack_prism(m, n)

            # Parse the results and write them
            domSet = convert_fibers_stack(m, sequence_so_far)
            result = nx.is_dominating_set(stack, domSet)
            return (result, n, sequence_so_far)

def m2mod3_completer(m, fiber1, fiber2):
    """Uses the first two fibers to find a dominating set for the cyclic stacked prism
    when m = 2 mode 3.
    
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
    # Check for appropriate size of m
    if ((m % 3) != 2):
        raise ValueError('m must be equivalent to 2 mod 3. Perhaps you mean m1mod3_completer? ')
    
    # For 2 mod 3, it can be done in 3 fibers.  Just find the third fiber.
    # Third fiber starts at m+1
    # Must append sets for consistency with m1mod3_completer
    fiber3 = fiber_one(m, m+1)
    sequence_so_far = [set(fiber1), set(fiber2), set(fiber3)]

    # Initialize some parameters
    n = len(sequence_so_far)
    stack = create_stack_prism(m, n)
    
    # Make the dominating set
    domSet = convert_fibers_stack(m, sequence_so_far)
    
    # Check if it dominates
    result = nx.is_dominating_set(stack, domSet)
    return (result, n, sequence_so_far)

def solver(m, save=False):
    """Finds a dominating set for stacked prisms and finds how long before the
    pattern repeats

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
    If save is True The dominating sets are written to the file 'NxSolver_m{m}_n{n}.txt'
    """
    # Construct the "standard" fiber1
    fiber1 = fiber_one(m)
    
    # Construct the "standard" fiber2 depending on the value of m.
    if (m % 6 == 3):
        fiber2 = fiber_one(m, 2*m - 1)
    else:
        fiber2 = fiber_two(m, fiber1)
        
    # Choose which completer to use
    # Note that 0 and 1 mod 3 can use the same completer
    if (m % 3 == 2):
        result = m2mod3_completer(m, fiber1, fiber2)
    elif (m % 3 == 1) or (m % 3 == 0):
        result = m1mod3_completer(m, fiber1, fiber2)
        
    # You shouldn't ever reach this, but just in case
    else:
        result = (False, 0, [[]])

    # If you want to save the results to a file
    if save:

        # Parse the results
        _, n, domSetFibers = result
        domSetStack = convert_fibers_stack(m, domSetFibers)

        # Open and write to the file.
        file = f'NxSolver_m{m}_n{n}.txt'
        output = f'm: {m}\nn: {n}\ndomSetStack = {domSetStack}\ndomSetFibers = {domSetFibers}'
        stream = open(file, 'w')
        stream.write(output)
        stream.close()
    return result

##############################################################################
def convert_sets_clock(m, fiberSet):
    """Converts a set of numbers into a list using the clockwise algorithm
    if the set is not a valid clockwise set, then returns an empty list

    Parameters
    ----------
    m: int
        The size of the cycle for the prism you are converting
    fiberSet: set
        The set of vertices to convert

    Returns
    -------
    list[int]
        vertices from the set in order based on the clockwise algorithm

    Outputs
    -------
    Nothing
    """
    # Try each vertex as a possible starting point
    # If the clockwise matches the set, then you're done
    for v in fiberSet:
        trial = fiber_one(m, v)
        # Need to do subset since it might not be a full clockwise
        if set(fiberSet).issubset(trial):
            # Return the same number of inputs
            return trial[:len(fiberSet)]
    return []


def test(m):
    for startOdd in range(14):
        for startEven in range(14):
            fiber1 = fiber_one(m, start=startOdd)
            fiber2 = fiber_one(m, start=startEven)
            fiber2 = fiber2[:-1]
            result = m1mod3_completer(m, fiber1, fiber2)
            if (result[0]) and (set() not in result[2]) and (0 in result[2][0]):
                starts = []
                for fiber in result[2]:
                    clock = convert_sets_clock(m, fiber)
                    starts.append(clock[0])
                print(starts)
