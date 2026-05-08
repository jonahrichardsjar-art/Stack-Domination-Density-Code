# Create a generator function for binary arrays of length m with weight g
import itertools
import numpy as np
import requests
import time as tm

def send_pushover_notification(message, title="Code Notification", user_key="u4q5fs89jfxaewvk2a3wudauuv2p4p", app_token="av5sge7omkiuo8mazdk1pkwytsmyf2"):
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


def generate_binary_arrays(m, g, first_bit_one=False):
    """
    Generator that yields binary arrays of length m with exactly g ones.
    
    Parameters:
    m (int): Length of the binary array
    g (int): Number of ones in the array (weight)
    first_bit_one (bool): If True, requires the first bit to be 1
    
    Yields:
    list: Binary arrays as lists of 0s and 1s
    """
    # Input validation
    if m < 0 or g < 0:
        print("Error: m and g must be non-negative")
        return
    
    if g > m:
        print("Error: Weight g cannot be greater than length m")
        return
    
    if first_bit_one and g == 0:
        print("Error: Cannot have first bit as 1 when weight is 0")
        return
    
    if first_bit_one and m == 0:
        print("Error: Cannot have first bit as 1 when length is 0")
        return
    
    # Handle edge cases
    if m == 0:
        if g == 0:
            yield []
        return
    
    if g == 0:
        yield [0] * m
        return
    
    # Generate combinations
    if first_bit_one:
        # First bit must be 1, so we need to place (g-1) ones in positions 1 to (m-1)
        remaining_positions = list(range(1, m))
        remaining_ones = g - 1
        
        if remaining_ones > len(remaining_positions):
            print("Error: Not enough positions for required ones with first bit constraint")
            return
        
        # Generate all combinations of positions for the remaining ones
        for positions in itertools.combinations(remaining_positions, remaining_ones):
            array = [0] * m
            array[0] = 1  # First bit is always 1
            for pos in positions:
                array[pos] = 1
            yield array
    else:
        # Generate all combinations of positions for the ones
        for positions in itertools.combinations(range(m), g):
            array = [0] * m
            for pos in positions:
                array[pos] = 1
            yield array

def make_path_matrix(size):
    A = np.zeros((size, size), dtype=int)
    for i in range(size - 1):
        A[i, i + 1] = 1
        A[i + 1, i] = 1
    return A

def KroneckerProduct(M1, M2):
    return np.kron(M1, np.eye(M2.shape[0], dtype=int)) + np.kron(np.eye(M1.shape[0], dtype=int), M2)

def swapArray(m, n):
    return [i + (n * j) for i in range(n) for j in range(2 * m)]

def perm_matrix(matrix):
    n = len(matrix)
    result = np.zeros((n, n))
    for r in range(n):
        result[r][matrix[r]] = 1
    return result

def manual_cycle(matrix, m, n):
    for v in range((2 * m)):
        matrix[v][(2 * m) * (n - 1) + v] = 1
        matrix[(2 * m) * (n - 1) + v][v] = 1
    return matrix

def checker(adjMatrix, biFilter):
    dominated = np.zeros((1, len(biFilter)), int)
    for i in range(len(biFilter)):
        if biFilter[i] == 1:
            dominated += adjMatrix[i]
    return np.all(dominated > 0)

def unchecker(adjMatrix, biFilter):
    dominated = np.zeros((1, len(biFilter)), int)
    for i in range(len(biFilter)):
        if biFilter[i] == 1:
            dominated += adjMatrix[i]
    #condition = dominated == 0
    #checked = np.where(condition, 1, 0)
    #return checked[0]
    return (dominated == 0).astype(int)

def findUndom(adjMatrix, bi1, bi2):
    """Finds the undominated vertices of two binary strings of adj. matrices."""
    temp1 = unchecker(adjMatrix, bi1)
    temp2 = unchecker(adjMatrix, bi2)
    return bin2set(temp1[0]).intersection(bin2set(temp2[0]))

def make_cycle_matrix(size):
    A = np.eye(size, dtype=int)
    for i in range(size):
        A[i, (i + 1) % size] = 1
        A[i, (i - 1) % size] = 1
    return A

def reorder_vertices(m):
    inner = list(range(0, m))
    outer = list(range(m, 2 * m))
    inner_reordered = inner[-1:] + inner[:-1]
    outer_reordered = outer[-1:] + outer[:-1]
    return inner_reordered + outer_reordered

def build_starting_matrix(m):
    part1 = make_cycle_matrix(m)
    part2 = np.eye(m, dtype=int)
    top = np.hstack((part1, part2))
    bottom = np.hstack((part2, part1))
    full = np.vstack((top, bottom))
    relabel_order = reorder_vertices(m)
    return full[np.ix_(relabel_order, relabel_order)]

def buildStack(m, n, answer=True):
    starting_matrix = build_starting_matrix(m)
    path_matrix = make_path_matrix(n)
    result = KroneckerProduct(starting_matrix, path_matrix)
    perm = perm_matrix(swapArray(m, n))
    final = np.dot(np.dot(perm, result), np.transpose(perm)).astype(int)
    if answer:
        final = manual_cycle(final, m, n).astype(int)
    return final

def start_checker(adjMatrix, biFilter):
    dominated = np.zeros((1, len(biFilter)), int)
    for i in range(len(biFilter)):
        if biFilter[i] == 1:
            dominated += adjMatrix[i]
    vertices = (dominated >= 1).astype(int)
    return vertices.sum()

def viable_sets(m, first):
    g = (m+2)//3
    good_starts = set()
    A = build_starting_matrix(m)
    for start_set in generate_binary_arrays(2*m, g, first_bit_one=first):
        if start_checker(A, start_set) >= (4*m+2)//3:
            good_starts.add(tuple(int(x) for x in start_set))
    return good_starts

def viable_sets2(m, first):
    g = (m+2)//3
    small_starts = set()
    medium_starts = set()
    large_starts = set()
    A = build_starting_matrix(m)
    for start_set in generate_binary_arrays(2*m, g, first_bit_one=first):
        if start_checker(A, start_set) == (4*m+2)//3:
            small_starts.add(tuple(int(x) for x in start_set))
        if start_checker(A, start_set) == (4*m+2)//3 + 1:
            medium_starts.add(tuple(int(x) for x in start_set))
        if start_checker(A, start_set) == (4*m+2)//3 + 2:
            large_starts.add(tuple(int(x) for x in start_set))
    return (small_starts, medium_starts, large_starts)

def generate_partitions_generator(n, k):
    """
    Generator that yields all partitions of {0, 1, ..., n-1} into n/k subsets of size k each.
    
    Args:
        n: Total number of elements (must be multiple of k)
        k: Size of each subset
    
    Yields:
        Each partition as a tuple of tuples (subsets)
    """
    if n % k != 0:
        raise ValueError("n must be a multiple of k")
    
    elements = list(range(n))
    
    def backtrack(remaining_elements, current_partition):
        # Base case: if no elements left, we have a complete partition
        if not remaining_elements:
            # Sort the partition to ensure canonical form
            canonical_partition = tuple(sorted(current_partition))
            yield canonical_partition
            return
        
        # If we need exactly one more subset, just take all remaining elements
        if len(remaining_elements) == k:
            subset = tuple(sorted(remaining_elements))
            canonical_partition = tuple(sorted(current_partition + [subset]))
            yield canonical_partition
            return
        
        # Generate all possible k-combinations from remaining elements
        # To avoid duplicates, we only consider combinations that include the smallest element
        smallest = min(remaining_elements)
        other_elements = [x for x in remaining_elements if x != smallest]
        
        # Choose k-1 elements from the others to form a subset with the smallest
        for combo in itertools.combinations(other_elements, k-1):
            subset = tuple(sorted([smallest] + list(combo)))
            new_remaining = [x for x in remaining_elements if x not in subset]
            # Recursively yield from the generator
            yield from backtrack(new_remaining, current_partition + [subset])
    
    # Start the recursive generation
    yield from backtrack(elements, [])

# Create a user-friendly generator function
def partition_elements_generator(n, k):
    """
    User-friendly generator function to partition elements 0 to n-1 into groups of size k.
    
    Args:
        n: Total number of elements (must be multiple of k)
        k: Size of each group
    
    Yields:
        Each partition as a list of lists for easy reading
    """
    #print(f"Generating partitions of elements 0 to {n-1} into groups of size {k}")
    #print(f"Number of groups per partition: {n//k}")
    #print("Use in a for loop to process one partition at a time")
    #print()
    
    for partition in generate_partitions_generator(n, k):
        # Convert to more readable format (list of sets)
        readable_partition = [set(subset) for subset in partition]
        yield readable_partition

def bin2set(binary_iterable):
    result = set()
    for i, partition in enumerate(binary_iterable):
        if binary_iterable[i] == 1:
            result.add(i)
    return result

def set2bin(set1, length):
    result = [0]*length
    for i in set1:
        result[i] = 1
    return result

def viable_partition(m):
    """
    Checks which partitions contain viable groups.
    """
    # Generate the set of viable 'large' dominating sets.
    set_of_viable = viable_sets(m, False)

    # Go through each partition and see if each pset is viable.
    for partition in partition_elements_generator(2*m, (m+2)//3):
        good = True
        for pset in partition:
            temp = set2bin(pset, 2*m)
            if temp not in set_of_viable:
                good = False
        if good:
            yield partition


def viable_partition2(m):
    """
    Checks which partitions contain viable groups and are small domination.
    """
    # Generate the set of viable 'large' dominating sets.
    small, _, _ = viable_sets2(m, False)

    # Go through each partition and see if each pset is viable.
    for partition in partition_elements_generator(2*m, (m+2)//3):
        good = True
        for pset in partition:
            temp = tuple(set2bin(pset, 2*m))
            if temp not in small:
                good = False
        if good:
            yield partition

def m4n8():
    prismAdj = build_starting_matrix(4)
    finalAdj = buildStack(4, 8)
    for prt in viable_partition2(4):
        for part in itertools.permutations(prt[1:]):
            fiber1 = set2bin(prt[0], 8)
            fiber3 = set2bin(part[0], 8)
            fiber5 = set2bin(part[1], 8)
            fiber7 = set2bin(part[2], 8)
            fiber2 = set2bin(findUndom(prismAdj, fiber1, fiber3), 8)
            fiber4 = set2bin(findUndom(prismAdj, fiber3, fiber5), 8)
            fiber6 = set2bin(findUndom(prismAdj, fiber5, fiber7), 8)
            fiber8 = set2bin(findUndom(prismAdj, fiber7, fiber1), 8)
            finalSet = fiber1 + fiber2 + fiber3 + fiber4 + fiber5 + fiber6 + fiber7 + fiber8
            result = checker(finalAdj, finalSet)
            if result:
                print(bin2set(fiber1),bin2set(fiber2),bin2set(fiber3),bin2set(fiber4),bin2set(fiber5),
                      bin2set(fiber6),bin2set(fiber7),bin2set(fiber8))

def m10n20():
    m = 10
    prismAdj = build_starting_matrix(m)
    finalAdj = buildStack(m, 20)
    for prt in viable_partition2(m):
        for part in itertools.permutations(prt[1:]):
            fiber1 = set2bin(prt[0], 2*m)
            fiber3 = set2bin(part[0], 2*m)
            fiber5 = set2bin(part[1], 2*m)
            fiber7 = set2bin(part[2], 2*m)
            fiber9 = set2bin(part[3], 2*m)
            fiber2 = set2bin(findUndom(prismAdj, fiber1, fiber3), 2*m)
            fiber4 = set2bin(findUndom(prismAdj, fiber3, fiber5), 2*m)
            fiber6 = set2bin(findUndom(prismAdj, fiber5, fiber7), 2*m)
            fiber8 = set2bin(findUndom(prismAdj, fiber7, fiber9), 2*m)
            fiber10 = set2bin(findUndom(prismAdj, fiber9, fiber1), 2*m)
            finalSet = fiber1 + fiber2 + fiber3 + fiber4 + fiber5 + fiber6 + fiber7 + fiber8 + fiber9 + fiber10
            result = checker(finalAdj, finalSet)
            if result:
                print(bin2set(fiber1),bin2set(fiber2),bin2set(fiber3),bin2set(fiber4),bin2set(fiber5),
                      bin2set(fiber6),bin2set(fiber7),bin2set(fiber8), bin2set(fiber9), bin2set(fiber10))        
                
def m1mod3Small(m, n):
    prismAdj = build_starting_matrix(m)
    finalAdj = buildStack(m, n)
    count = 0
    stream = open(f"m{m}n{n}SmallPartResult.txt", "a")
    for prt in viable_partition2(m):
        for part in itertools.permutations(prt[1:]):
            fiber1 = set2bin(prt[0], 2*m)
            for i in range(3, n, 2):
                exec(f"fiber{i} = set2bin(part[{(i-3)//2}], 2*m)")
            for j in range(2, n, 2):
                exec(f"fiber{j} = set2bin(findUndom(prismAdj, fiber{j-1}, fiber{j + 1}), 2*m)")
            exec(f"fiber{n} = set2bin(findUndom(prismAdj, fiber{n-1}, fiber1), 2*m)")
            finalSet = []
            for k in range(1, n + 1):
                exec(f"finalSet += fiber{k}")
            result = checker(finalAdj, finalSet)
            if result:
                count += 1
                domSet = ""
                for k in range(1, n + 1):
                    domSet += str(eval(f"bin2set(fiber{k})")) + " "
                stream.write(domSet + "\n")
                print(domSet)
    stream.write(f"Done. Count = {count}. \n")
    stream.close()


#start = tm.time()
#try:
#    m = 10
#    n = 20
#    m1mod3Small(m, n)
#    end = tm.time()
#    send_pushover_notification(f"m = {m}, n = {n} is finished. Took {end-start} seconds.")
#except Exception as e:
#    print(e)
#    end2 = tm.time()
#    send_pushover_notification(f"Failed. m{m}n{n} took {end2-start} seconds.")
