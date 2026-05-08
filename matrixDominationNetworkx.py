import networkx as nx
import math
import matrixDominationPlots as mdp
import numpy as np
import itertools
import time as tm
#import requests
from oct2py import octave as op
from collections import Counter


def send_pushover_notify(message, title="Code Notification", user_key="u4q5fs89jfxaewvk2a3wudauuv2p4p", app_token="av5sge7omkiuo8mazdk1pkwytsmyf2"):
    """Sends a notification via Pushover."""
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": app_token,
        "user": user_key,
        "message": message,
        "title": title
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        print("Pushover notification sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Pushover notification: {e}")

## Provides mdp.plot_prism_graph, mdp.plot_stack_graph,
##          mdp.plot_prism_graph_tikz, mdp.plot_stack_graph_tikz

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
##  Helper functions for finding dominating sets.
##  Contains functions:
##      dominated
##      find_undom_next
##          [dominated]
##      convert_fibers_stack
##      clockwise
##      convert_sets_clock
##          [clockwise]
##----------------------------------------------------------------------

def find_eigenvalues(m, n):
    """Return a list of all eigenvalues for a prism stack adj. matrix. Works on Networkx graph.
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of the prism graph.
    n: int
        Number of prism graphs to put in the stack cycle.
    
    Returns
    -------
    list[list[float]]
        list of eigenvalues
        
    Outputs
    -------
    Nothing
    """
    graph = create_stack_graph(m, n)
    adjmatrix = nx.to_numpy_array(graph)
    eigenvalues = op.eig(adjmatrix)
    return eigenvalues

def flat_list(array):
    """Takes a np.array and flats it to a 1 dimensional rounded 3 decimal place list.
    Parameters
    ----------
    array: np.array(eigenvalues)
        The array that will be turned into a simple list

    Returns
    -------
    list[rounded floats]

    Outputs
    -------
    Nothing
    """
    start_list = array.tolist()
    flat_list = [item for sublist in start_list for item in sublist]
    flat_list = [round(x, 3) for x in flat_list]
    return flat_list

def list_removal(list1, list2):
    """Returns list1 with only occurances of the values in list2. Used for eigenvectors.

    Parameters
    ----------
    list1: list[numbers]
        The list of numbers to be left and returned back
    list2: list[numbers]
        A list to be turned into a set and then used for removing values.

    Returns
    -------
    list[numbers]
        List of remaing eigenvalues

    Outputs
    -------
    Nothing
    """
    set2 = set(list2)
    result = []
    for i in list1:
        if i in set2:
            result.append(i)
    return result

def list_com(list1, list2):
    result = []
    for i in list1:
        for j in list2:
            if i == j:
                result.append(i)
                list2.remove(j)
                break
    return result

def sub_eig(m, n):
    """Returns a list of the remaining eigenvalues of a stack after subtracting the values of the prism.

    Parameters
    ----------
    m: int
        Number of vertices in each ring of the prism graph.
    n: int
        Number of prism graphs to put in the stack cycle.
        
    Returns
    -------
    list[list[float]]
        list of eigenvalues
        
    Outputs
    -------
    Nothing
    """
    stack_graph = create_stack_graph(m, n)
    stack_adjmatrix = nx.to_numpy_array(stack_graph)
    stack_values = op.eig(stack_adjmatrix)
    prism_graph = create_prism_graph(m)
    prism_adjmatrix = nx.to_numpy_array(prism_graph)
    prism_values = op.eig(prism_adjmatrix)
    stack_list = stack_values.tolist()
    prism_list = prism_values.tolist()
    flat_stack_list = [item for sublist in stack_list for item in sublist]
    flat_prism_list = [item for sublist in prism_list for item in sublist]

    flat_stack_list = [round(x, 3) for x in flat_stack_list]
    flat_prism_list = [round(x, 3) for x in flat_prism_list]
    
    counter_a = Counter(flat_stack_list)
    counter_b = Counter(flat_prism_list)
 
    for _ in range(n):
        counter_a -= counter_b
        counter_a += Counter()  # removes negative/zero counts

    result = list(counter_a.elements())
    return result
    
def sub_list(list1, list2):
    """Subtracts the contents of list 2 from list 1 using occurances, only useful for numbers of same type.

    Parameters
    ----------
    list1: list[]
        array of numerical values
    list2: list[]
        array of numerical values

    Returns
    -------
    list[remaining values of list1 after subtraction]

    Outputs
    -------
    Nothing
    """ 
    result = list((Counter(list1) - Counter(list2)).elements())
    return result

def sub_sets(list1, list2):
    """Subtracts the contents of list 2 from list 1 using set subtraction, only useful for numbers of same type.

    Parameters
    ----------
    list1: list[]
        bigger array of numerical values
    list2: list[]
        smaller array of numerical values

    Returns
    -------
    list[remaining values of list1 after subtraction]

    Outputs
    -------
    Nothing
    """ 
    result = set(list1) - set(list2)
    return list(result)

def set_inter(array1, array2):
    """Finds the intersection of two numpy arrays as if they were sets.
    Parameters
    ----------
    array1: array[numbers]
        list of numerical values
    array2: array[numbers]
        another list of numerical values of similar type

    Returns
    -------
    set(intersecting values)
    """
    list1 = array1.tolist()
    list2 = array2.tolist()
    flat_list1 = [item for sublist in list1 for item in sublist]
    flat_list2 = [item for sublist in list2 for item in sublist]
    set1 = set(flat_list1)
    set2 = set(flat_list2)
    return list(set1.intersection(set2))

def binary_lists_with_weight(n, k, start=True):
    """Yields all binary combination lists of length n with k amount of 1's.

    Parameters
    ----------
    n: int
        length of the binary arrays
    k: int
        amount of 1's in each binary array
    start: bool (optional, default True)
        If true, forces a 1 in the first position

    Returns
    -------
    binary: list[int]
        The binary array of ints

    Outputs
    -------
    Nothing
    """
    start_position = 0
    count = k
    if start:
        start_position = 1
        count = k-1
    for ones_indices in itertools.combinations(range(start_position, n), count):
        binary = np.zeros(n, dtype=int)
        if start:
            binary[0] = 1
        binary[list(ones_indices)] = 1
        yield binary

def eigenvalue_frequency(array):
    """Return the freuency of a np array eigenvector and the frequency of each eigenvalue.

    Parameters
    ----------
    array: np.array[floats]
        numpy array of eigenvalues

    Returns
    -------
    dict(float: amount of appearence)
        frequency of eigenvalues in the array

    Outputs
    -------
    Nothing
    """
    frequency_dict = dict()
    count = 0
    frequency_dict["Total Values"] = 0
    for i in array:
        count += 1
        new_float = round(i[0].item(), 3)
        if new_float in frequency_dict.keys():
            frequency_dict[new_float] += 1
        else:
            frequency_dict[new_float] = 1
    frequency_dict["Total Values"] = count
    return frequency_dict

def eig_freq_list(lst):
    """Return the freuency of a list eigenvector and the frequency of each eigenvalue.

    Parameters
    ----------
    list: list[floats]
        list of eigenvalues

    Returns
    -------
    dict(float: amount of appearence)
        frequency of eigenvalues in the array

    Outputs
    -------
    Nothing
    """
    frequency_dict = dict()
    count = 0
    frequency_dict["Total Values"] = 0
    for i in list:
        count += 1
        new_float = round(i, 3)
        if new_float in frequency_dict.keys():
            frequency_dict[new_float] += 1
        else:
            frequency_dict[new_float] = 1
    frequency_dict["Total Values"] = count
    return frequency_dict
    
def absolute_eigenvector(dic):
    """Return the frequency of the eiegnvalue_frequency function in terms of absolute values.

    Parameters
    ----------
    dic: dict(eigenvalue(float): frequency(int))
        dict of eigenvalues and their frequency

    Returns
    -------
    dict(abs eigenvalue(float): frequency(int))
        frequency of absolute value eigenvalues

    Outputs
    -------
    Nothing
    """
    frequency_dict = dict()
    frequency_dict["Total Values"] = dic["Total Values"]
    for i in dic:
        if i == "Total Values":
            continue
        if abs(i) in frequency_dict.keys():
            frequency_dict[abs(i)] += dic[i]
        else:
            frequency_dict[abs(i)] = 0
            frequency_dict[abs(i)] += dic[i]
    return frequency_dict

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
        The list containing the list of the dominating vertices in each fiber and they are numbered not binary according to total vertex count.

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

# clockwise was called fiber_one
def clockwise(m, start=0, bound=None):
    """From the starting position, finds dominating vertices of the m-cyclic
    prism using the clockwise algorithm which is (current + 3) cross from
    outside to inside or inside to outside.  Works only for m-cyclic prism
    graphs.

    Parameters
    ----------
    m: int
        The size of the cycle for the prism
    start: int (optional, default 0)
        Where to start for the algorithm
    bound: bool (optional, default None)
        For manually choosing amount of vertices in each fiber

    Returns
    -------
    list[int]
        vertices that nearly dominate the prism based on clockwise algorithm

    Outputs
    -------
    Nothing
    """
    # Start with an list that contains the start
    fiberSet = [start]
    
    # Set the current position to the start
    position = start
    
    # Count so that you stop when you have "enough"
    count = 1
    
    # Make sure fiber1 has the right number of vertices
    if not bound:
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
        fiberSet.append(position)
        count += 1
    return fiberSet

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
        trial = clockwise(m, v)
        # Need to do subset since it might not be a full clockwise
        if set(fiberSet).issubset(trial):
            # Return the same number of inputs
            return trial[:len(fiberSet)]
    return []

##----------------------------------------------------------------------
##  Algorithmically generated dominating sets.
##  Contains functions:
##      m0134mod3_fibers
##          [create_prism_graph]
##          [find_undom_next]
##      m025mod6_fibers
##          [clockwise]
##      m1mod6_fibers
##          [clockwise]
##      m3mod6_fibers
##          [clockwise]
##      solver
##          [m0134mod6_fibers]
##          [m025mod6_fibers]
##          [convert_fibers_stack]
##          [create_stack_graph]
##          [mdp.plot_stack_graph] if display=True
##          [mdp.plot_stack_graph_tikz] if tikz=True
##----------------------------------------------------------------------

def m0134mod6_fibers(m):
    """Uses the first two fibers to find a dominating set for the cyclic stacked prism
    when m = 0, 1, 3, 4 mode 6.
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 0, 1, 3, 4 mod 6.

    Returns
    -------
    list[sets] is a list of vertices in each fiber using the convention that the outer
        cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    Nothing
    """
    ## Check for appropriate size of m
    if ((m % 6) not in {0, 1, 3, 4}):
        raise ValueError('m must be equivalent to 0, 1 mod 3. Perhaps you mean m2mod3_completer? ')
    
    # Construct the prism for m
    graph = create_prism_graph(m)
    
    # Construct the first two fibers
    fiber1 = clockwise(m)
    # Special case when m = 3 mod 6
    if ((m % 6) == 3):
        fiber2 = clockwise(m, start=(2*m)-1)
    else:
        fiber2 = clockwise(m, start=2)
    # Remember that when m = 1 mod 6, even fibers are short
    if ((m % 3) == 1):
        fiber2 = fiber2[:-1]

    # Keep track of what we have so far
    domFibers = [set(fiber1), set(fiber2)]
    
    # Keep going until we start to repeat
    cont = True
    
    # We will have three fibers: prev, current, next that will iterate until repeat
    prev_fiber = fiber1
    current_fiber = fiber2
    while cont:
        # Construct what has to be in the next fiber
        next_fiber = find_undom_next(graph, prev_fiber, current_fiber)
        
        # If it is new, add it then iterate to the next pair of fibers
        if set(next_fiber) not in domFibers:
            
            # Must append sets to ensure clockwise and counterclockwise walks are the same
            domFibers.append(set(next_fiber))
            prev_fiber, current_fiber = current_fiber, next_fiber
            
        # if it’s already there, then we’re repeating and are done
        # in reality, it should be equal to fiber1 when it starts to repeat
        else:
            return domFibers

def m025mod6_fibers(m):
    """Finds a dominating set for the cyclic stacked prism
    when m = 0, 2, 5 mod 6.
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 0, 2, 5 mod 6.

    Returns
    -------
    list[sets] is a list of vertices in each fiber using the convention that the outer
        cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    Nothing
    """
    # Check for appropriate size of m
    if not ((m % 6) in {0, 2, 5}):
        raise ValueError('m must be equivalent to 0, 2, 5 mod 6.')
    
    # For 0, 2, 5 mod 6, it can be done in 3 fibers.
    # First fiber starts at 0
    fiber1 = clockwise(m, start=0)
    
    # Second fiber starts at 2
    fiber2 = clockwise(m, start=2)
    
    # Third fiber starts at m+1
    fiber3 = clockwise(m, start=m+1)
    
    # Put them all together
    domFibers = [set(fiber1), set(fiber2), set(fiber3)]
    return domFibers

def m1mod6_fibers(m):
    """Finds a dominating set for the cyclic stacked prism
    when m = 1 mod 6.
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 3 mod 6.

    Returns
    -------
    list[lists] is a list of vertices in each fiber using the convention that the outer
        cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    Nothing
    """
    # Check for appropriate size of m
    if not ((m % 6) in {1}):
        raise ValueError('m must be equivalent to 1 mod 6.')

    # Initialize some variables
    domFibers = []
    clock = clockwise(m, bound=2*m)

    # Generate starting points for odd and even fibers
    for i in range(0, 2*m):
        oddStart = i + (i%2)*m - (i//m)*m
        #if i >= m:
        #    oddStart -= m
        oddFiber = clockwise(m, oddStart)
        domFibers.append(oddFiber)

        evenStart = (i+2) + (i%2)*m - ((i+2)//m)*m
        #if i >= 2*m - 2:
        #    evenStart -= 2*m
        #elif i >= m - 2:
        #    evenStart -= m
        evenFiber = clockwise(m, evenStart)
        domFibers.append(evenFiber[:-1])
    return domFibers

def m3mod6_fibers(m):
    """Finds a dominating set for the cyclic stacked prism
    when m = 3 mod 6.
    
    Parameters
    ----------
    m: int
        Number of vertices in each ring of a single prism (total 2m per copy).
        m should be equivalent to 3 mod 6.

    Returns
    -------
    list[lists] is a list of vertices in each fiber using the convention that the outer
        cycle is labeled (0) to (m-1) and the inner cycle is labeled (m) to (2m-1)

    Outputs
    -------
    Nothing
    """
    # Check for appropriate size of m
    if not ((m % 6) in {3}):
       raise ValueError('m must be equivalent to 3 mod 6.')

    # Create a empty list of length 2m
    startPoints = [0] * (2*m)
    current = (2*m)-1
    # Iteratre through the first half to set start points
    for i in range(1, m+1):
        startPoints[i] = current
        current = (current + (m-1)) % (2*m)
    # Set current for m+1 position and start iteration
    current = m - 1
    for j in range(m+1, 2*m):
        startPoints[j] = current
        current = (current + (m-1)) % (2*m)

    # Convert the starting points into clockwise lists
    domFibers = [clockwise(m, x) for x in startPoints]
    return domFibers    

def solver(m, save=False, display=False, tikz=False):
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
    display: bool, optional (default False)
        If True, the image will appear on the screen.
        If False, it will not appear.
    tikz: bool, optional (default False)
        If True, tikz code will be generated for LaTex
        If False, it will not generate code

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
    if display is True, the image will appear on the screen.
    If tikz is True LaTex code will be saved to the file 'tikz_prism_m{m}.tex'
    """
    # Use the correct algorithm to find the fibers
    if (m % 6) in {0, 2, 5}:
        domFibers = m025mod6_fibers(m)
    elif (m % 6) in {1, 3, 4}:
        domFibers = m0134mod6_fibers(m)
    else:
        raise ValueError ('m must be an integer')
        
    # Use the fibers to set some variables  
    n = len(domFibers)
    domSet = convert_fibers_stack(m, domFibers)
    G = create_stack_graph(m, n)
    check = nx.is_dominating_set(G, domSet)
    result = (check, n, domFibers)

    if display:
        if n > 10:
            answer = input('That graph will be large. Are you sure you want to display? [Y/N] ')
            if answer[0].lower() in {'y'}:
                mdp.plot_stack_graph(m, n, domSet=domSet, label=True)
        else:
            mdp.plot_stack_graph(m, n, domSet=domSet, label=True, save=True)
        
    if tikz:
        mdp.plot_stack_graph_tikz(m, n, domSet=domSet, figsize = [20, 20])
    
    if save:
        # Open and write to the file.
        file = f'NxSolver_m{m}_n{n}.txt'
        output = f'm: {m}\nn: {n}\ndomSet = {domSet}\ndomFibers = {domFibers}'
        stream = open(file, 'w')
        stream.write(output)
        stream.close()
    return result

def starts(m):
    domFibers = m1mod6_fibers(m)
    starts = []
    for f in domFibers:
        starts.append(f[0])
    return starts

def test():
    for m in range(3,1003):
        result = solver(m)
        if result[0]:
            print(m)
        else:
            print(f"###################{m}###################")

def dummy():
    n = 10
    k = 2
    graph = create_stack_graph(5, 3)
    fiber1 = list(itertools.combinations(list(range(1, 10)), 1))
    fiber2 = list(itertools.combinations(list(range(10, 20)), 2))
    fiber3 = list(itertools.combinations(list(range(20, 30)), 2))
    prod = itertools.product(fiber1, fiber2, fiber3)
    for i in prod:
        domSet = (0,) + i[0]+i[1]+i[2]
        check = nx.is_dominating_set(graph, domSet)
        if check:
            print(domSet)

def dummy2():
    m = 10
    graph = create_stack_graph(10, 8)
    fiber1 = list(itertools.combinations(list(range(1, m)), 2))
    fiber2 = list(itertools.combinations(list(range(m, 2*m)), 2))
    fiber3 = list(itertools.combinations(list(range(2*m, 3*m)), 3))
    fiber4 = list(itertools.combinations(list(range(3*m, 4*m)), 2))
    fiber5 = list(itertools.combinations(list(range(4*m, 5*m)), 3))
    fiber6 = list(itertools.combinations(list(range(5*m, 6*m)), 2))
    fiber7 = list(itertools.combinations(list(range(6*m, 7*m)), 3))
    fiber8 = list(itertools.combinations(list(range(7*m, 8*m)), 2))
    prod = itertools.product(fiber1, fiber2, fiber3, fiber4, fiber5, fiber6, fiber7, fiber8)
    for i in prod:
        count = 0
        start = tm.time()
        domSet = (0, ) + i[0]+i[1]+i[2]+i[3]+i[4]+i[5]+i[6]+i[7]
        check = nx.is_dominating_set(graph, domSet)
        if check:
            count += 1
            found = tm.time()
            send_pushover_notify(f"dummy2 has a {count}th solution in {found-start} seconds")
            print(domSet)
    end = tm.time()
    send_pushover_notify(f"dummy2 has finished it's work with {count} solutions in {end-start} seconds")
