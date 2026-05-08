import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


##----------------------------------------------------------------------
##  Code for constructing prisms and prism stacks
##  Contains functions:
##      create_prism_graph
##      create_stack_graph
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

def create_stack_graph(m, n, cycle=True):
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
##          [create_stack_graph]
##      plot_prism_graph_tikz
##          [create_prism_graph]
##      plot_stack_graph_tikz
##          [create_stack_graph]
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
                     display=True, title=False, save=False, label=False):
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
    G = create_stack_graph(m, n, cycle)

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
    

def plot_stack_graph_tikz(m, n, domSet=[], cycle=True, figsize=(15, 15), title=False, label=True):
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
    G = create_stack_graph(m, n, cycle)
    
    # Calculate scale factor based on figsize
    scale_factor = min(figsize) / 10.0
    
    # Create positions for vertices using same logic as plot_stack_graph
    big_R = 3.0 * scale_factor
    centre_step = 2*np.pi/n
    # You might need to adjust the _r values to make the picture look nice.
    #local_layout = _prism_local_layout(m, outer_r=0.9*scale_factor, inner_r=0.55*scale_factor)
    local_layout = _prism_local_layout(m, outer_r=0.9*scale_factor, inner_r=0.55*scale_factor)
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
