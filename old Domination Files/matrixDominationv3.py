import numpy as np
import itertools
import time as tm
import requests

def send_pushover_TMB(message, title="Code Notification", user_key="u4q5fs89jfxaewvk2a3wudauuv2p4p", app_token="av5sge7omkiuo8mazdk1pkwytsmyf2"):
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

def send_pushover_JAR(message, title="Code Notification", user_key = "upea2iam79bid8wmzwm6rq7p3jgfv3", app_token = "a9o2ouuxqvayb39jpqd4ar4kibd8xy"):
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



def make_cycle_matrix(size):
    """Creates a cycle adjacency matrix with 1's on the diagonal and connections to next/prev nodes."""
    A = np.eye(size, dtype=int)  # diagonal with 1s
    for i in range(size):
        A[i, (i + 1) % size] = 1
        A[i, (i - 1) % size] = 1
    return A

def make_path_matrix(size):
    """Creates a path graph adjacency matrix of given size."""
    A = np.zeros((size, size), dtype=int)
    for i in range(size - 1):
        A[i, i + 1] = 1
        A[i + 1, i] = 1
    return A

def reorder_vertices(m):
    """Returns index order to match your layered clockwise labeling."""
    # Base row order:
    inner = list(range(0, m))
    outer = list(range(m, 2 * m))

    # Rotate to match your starting point: move index 0 to middle position
    inner_reordered = inner[-1:] + inner[:-1]  # rotate right by 1
    outer_reordered = outer[-1:] + outer[:-1]  # rotate right by 1

    return inner_reordered + outer_reordered

def build_starting_matrix(m):
    part1 = make_cycle_matrix(m)
    part2 = np.eye(m, dtype=int)

    top = np.hstack((part1, part2))
    bottom = np.hstack((part2, part1))
    full = np.vstack((top, bottom))

    # Relabel to custom visual order
    relabel_order = reorder_vertices(m)
    full = full[np.ix_(relabel_order, relabel_order)]

    return full

def KroneckerProduct(M1, M2):
    """Computes (M1 ⊗ I2) + (I1 ⊗ M2)."""
    I2 = np.eye(M2.shape[0], dtype=int)
    I1 = np.eye(M1.shape[0], dtype=int)

    kron1 = np.kron(M1, I2)
    kron2 = np.kron(I1, M2)
    return kron1 + kron2

def swapArray(m, n):
    result = []
    for i in range(n):
        for j in range(2*m):
            result.append(i+(n*j))
    return result

def perm_matrix(matrix):
    n = len(matrix)
    result = np.zeros((n, n))
    for r in range(n):
        result[r][matrix[r]] = 1
    return result    

def toBelements(matrix):
    condition = matrix > 0
    result = np.where(condition, 1, 0)
    return result

def manual_cycle(matrix, m, n):
    result = matrix
    for v in range((2*m)):
        result[v][(2*m)*(n-1)+v] = 1
        result[(2*m)*(n-1)+v][v] = 1
    return result

def checker(adjMatrix, biFilter):
    # Checks if a set is a dominating set
    dominated = np.zeros((1, len(biFilter)), int)
    for i in range(len(biFilter)):
        if biFilter[i] == 1:
            dominated += adjMatrix[i]
    condition = dominated > 0
    checked = np.where(condition, 1, 0)
    if np.sum(checked) == len(biFilter):
        return True
    else:
        return False

def binary_lists_with_weight(n, k):
    if k == 0 or n == 0 or k > n:
        return  # No valid binary list possible
    # Always place a 1 at index 0, then choose k-1 indices from positions 1 to n-1
    for ones_indices in itertools.combinations(range(1, n), k - 1):
        binary = np.zeros(n, dtype=int)
        binary[0] = 1  # First element is always 1
        binary[list(ones_indices)] = 1
        yield binary

def generate_binary_segment_of_weight(length, weight, first_entry_must_be_one=False):
    if first_entry_must_be_one:
        if weight < 1 or weight > length:
            return []
        
        remaining_length = length - 1
        remaining_weight = weight - 1
        if remaining_weight < 0 or remaining_weight > remaining_length:
            return []
        segments = []
        for positions_of_ones in itertools.combinations(range(remaining_length), remaining_weight):
            segment_suffix = [0] * remaining_length
            for pos in positions_of_ones:
                segment_suffix[pos] = 1
            segments.append([1] + segment_suffix)
        return segments
    else:
        if weight < 0 or weight > length:
            return []
        segments = []
        for positions_of_ones in itertools.combinations(range(length), weight):
            segment = [0] * length
            for pos in positions_of_ones:
                segment[pos] = 1
            segments.append(segment)
        return segments

def generate_all_binary_arrays(m, n, k_weights):
    segment_length = 2 * m
    if len(k_weights) != n:
        print(f"Error: The length of the 'k_weights' list ({len(k_weights)}) "
              f"must be equal to 'n' ({n}). Please ensure they match.")
        return # Return immediately for invalid input, as it's a generator.
    def backtrack(current_segment_index, current_array_prefix):
        if current_segment_index == n:
            yield current_array_prefix[:]
            return
        target_weight_for_this_segment = k_weights[current_segment_index]
        is_first_segment = (current_segment_index == 0)
        possible_segments_for_current = generate_binary_segment_of_weight(
            segment_length, target_weight_for_this_segment, first_entry_must_be_one=is_first_segment
        )
        for segment in possible_segments_for_current:
            current_array_prefix.extend(segment)
            yield from backtrack(current_segment_index + 1, current_array_prefix)
            for _ in range(segment_length): # Changed from 'm' to 'segment_length'
                current_array_prefix.pop()
    yield from backtrack(0, [])

def hunter(adjMatrix, m, n, k, verbose=False):
    start = tm.time()
    start1 = tm.time()
        #for bf in binary_lists_with_weight(len(adjMatrix), i):
    for bf in generate_all_binary_arrays(m, n, k):
        if (tm.time() - start1) > 600:
            print("#", end = '')
            start1 = tm.time()
        if checker(adjMatrix, bf):
            if verbose:
                end = tm.time()
                print(f"It took {end - start} seconds.")
            return bf
        else:
            pass
    return np.zeros(len(adjMatrix))

def findAll(adjMatrix, m, n, k):
    start = tm.time()
    start1 = tm.time()
    domSets = set()
    #for bf in binary_lists_with_weight(len(adjMatrix), k):
    for bf in generate_all_binary_arrays(m, n, k):
        if (tm.time() - start1) > 600:
            print("#", end = '')
            start1 = tm.time()
        if checker(adjMatrix, bf):
            temp = [int(v) for v in bf]
            domSets.add(tuple(temp))
            print(temp)
        else:
            pass
    return domSets

def matrixToBstring(M):
    s=''
    n=len(M)
    for r in range(1,n):
        for c in range(r):
            s+=str(M[r][c])
    return s

def bstringToG6(binstr):
    g6=''
    n=1
    ## Find the number of vertices
    while (n*(n+1))//2<=len(binstr):
        n+=1
    g6+=chr(n+63)
    ## Pad zeroes so the length is a multiple of 6.
    while len(binstr)%6!=0:
        binstr+='0'
    ## Break it into groups of length 6, convert to ASCII, append to g6
    for i in range(len(binstr)//6):
        g6+=chr(int(binstr[6*i:6*i+6],2)+63)
    return g6

def matrixToG6(matrix):
    return bstringToG6(matrixToBstring(matrix.astype(int)))

# --- Main Program ---

# Get inputs
m = int(input("Enter value for m: "))
n = int(input("Enter value for n: "))
answer = int(input("Path(0) or Cycle(1): "))
weights_input = input("Enter list of weights (comma-separated, one per segment): ")
k = list(map(int, weights_input.strip().split(',')))

# Build matrices
starting_matrix = build_starting_matrix(m)
path_matrix = make_path_matrix(n)    
result = KroneckerProduct(starting_matrix, path_matrix)


# Kronecker sum
perm = perm_matrix(swapArray(m, n))
final = np.dot(np.dot(perm, result), np.transpose(perm)).astype(int)
if answer:
   final = manual_cycle(final, m, n).astype(int)

start = tm.time()
#dominatingSet = hunter(final, m, n, k)
allDomSets = findAll(final, m, n, k)

stream = open(f"m{m}n{n}Results.txt", "w")
stream.write(f"m = {m}, n = {n}, k = {k}\n")
stream.write(f"Dominating Set: {allDomSets}")
stream.close()

end = tm.time()
msg = f"m = {m}, n = {n} FINDALL finished in {round(end-start, 2)} seconds."
print(msg)

send_pushover_TMB(msg)
send_pushover_JAR(msg)


