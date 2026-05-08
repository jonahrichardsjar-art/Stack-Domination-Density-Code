import numpy as np
import itertools
import time as tm

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
    #condition = matrix > 0
    #result = np.where(condition, 1, 0)
    matrix[matrix > 0] = 1
    return matrix

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
    dominated[dominated > 0] = 1
    #condition = dominated > 0
    #checked = np.where(condition, 1, 0)
    if np.sum(dominated) == len(biFilter):
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

def hunter(adjMatrix, small = 1, verbose=False):
    start = tm.time()
    start1 = tm.time()
    for i in range(small, len(adjMatrix)):
        if verbose:
            print(f"Checking dominating set size {i}")
        for bf in binary_lists_with_weight(len(adjMatrix), i):
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

def findAll(adjMatrix, k):
    domSets = set()
    for bf in binary_lists_with_weight(len(adjMatrix), k):
        if checker(adjMatrix, bf):
            temp = [int(v) for v in bf]
            domSets.add(tuple(temp))
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
startingPoint = int(input("Enter dominating set start: "))
#weights_input = input("Enter list of weights (comma-separated, one per segment): ")
#k = list(map(int, weights_input.strip().split(',')))

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
dominatingSet = hunter(final, small = startingPoint)
allDomSets = findAll(final, startingPoint)
end = tm.time()
print(end - start)
#allDomSets = findAll(final, int(np.sum(dominatingSet)))
# Print the result
np.set_printoptions(linewidth=200)
#print("\nKronecker Sum Result Matrix:")
#print(result)

#print(matrixToG6(result))

# m3n2
# perm = perm_matrix([0, 2, 4, 6, 8, 10, 1, 3, 5, 7, 9, 11])
# m3n3
# perm = perm_matrix([0, 3, 6, 9, 12, 15, 1, 4, 7, 10, 13, 16, 2, 5, 8, 11, 14, 17])
# m4n2
# perm = perm_matrix([0, 2, 4, 6, 8, 10, 12, 14, 1, 3, 5, 7, 9, 11, 13, 15])
# m4n3
# perm = perm_matrix([0, 3, 6, 9, 12, 15, 18, 21, 1, 4, 7, 10, 13, 16, 19, 22, 2, 5, 8, 11, 14, 17, 20, 23])
# m5n2
# perm = perm_matrix([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19])


print("----------------------------------------------------------------------------------------------")
#print(matrixToG6(final))

# Pause so user can see output



