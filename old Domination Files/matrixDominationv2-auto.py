import numpy as np
import itertools
import time as tm
import requests

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

def make_cycle_matrix(size):
    A = np.eye(size, dtype=int)
    for i in range(size):
        A[i, (i + 1) % size] = 1
        A[i, (i - 1) % size] = 1
    return A

def make_path_matrix(size):
    A = np.zeros((size, size), dtype=int)
    for i in range(size - 1):
        A[i, i + 1] = 1
        A[i + 1, i] = 1
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

def toBelements(matrix):
    return np.where(matrix > 0, 1, 0)

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

def binary_lists_with_weight(n, k):
    if k == 0 or n == 0 or k > n:
        return
    for ones_indices in itertools.combinations(range(1, n), k - 1):
        binary = np.zeros(n, dtype=int)
        binary[0] = 1
        binary[list(ones_indices)] = 1
        yield binary

def binary_lists_with_weightInRecurv(n, k):
    for ones_indices in itertools.combinations(range(n), k):
        binary = np.zeros(n, dtype=int)
        binary[list(ones_indices)] = 1
        yield binary

def recursiveBinaryCreator(biArray, m, weights, idx=0):
    if idx >= len(weights):
        yield biArray
    else:
        for bf in binary_lists_with_weightInRecurv(2 * m, weights[idx]):
            tempBi = np.concatenate((biArray, bf))
            yield from recursiveBinaryCreator(tempBi, m, weights, idx + 1)

def recurvHunter(adjMatrix, m, weights, verbose=False):
    start = tm.time()
    last_check = start  # To track the last 10-minute mark
    if verbose:
        print(f"Segment weights: {weights}")
    for first in binary_lists_with_weight(2 * m, weights[0]):
        for full_vec in recursiveBinaryCreator(first, m, weights, idx=1):
            # Check if 10 minutes have passed
            if tm.time() - last_check >= 600:  # 600 seconds = 10 minutes
                print("#", end = "")
                last_check = tm.time()  # Reset the last check time
            if checker(adjMatrix, full_vec):
                if verbose:
                    print(f"Found dominating set in {tm.time() - start:.2f} seconds.")
                return full_vec
    return np.zeros(len(adjMatrix))

def findAll(adjMatrix, m, weights, verbose=False):
    domSets = set()
    start = tm.time()
    if verbose:
        print(f"Finding all dominating sets with segment weights: {weights}")
    for first in binary_lists_with_weight(2 * m, weights[0]):
        for full_vec in recursiveBinaryCreator(first, m, weights, idx=1):
            if checker(adjMatrix, full_vec):
                domSets.add(tuple(int(x) for x in full_vec))
    if verbose:
        print(f"Found {len(domSets)} dominating sets in {tm.time() - start:.2f} seconds.")
    return domSets

def matrixToBstring(M):
    return ''.join(str(M[r][c]) for r in range(1, len(M)) for c in range(r))

def bstringToG6(binstr):
    n = 1
    while (n * (n + 1)) // 2 <= len(binstr):
        n += 1
    g6 = chr(n + 63)
    binstr += '0' * ((6 - len(binstr) % 6) % 6)
    for i in range(0, len(binstr), 6):
        g6 += chr(int(binstr[i:i + 6], 2) + 63)
    return g6

def matrixToG6(matrix):
    return bstringToG6(matrixToBstring(matrix.astype(int)))

# --- Main Program ---

# m = int(input("Enter value for m: "))
while(1):
    m = 7
    # n = int(input("Enter value for n: "))
    file = "next" + str(m) + ".txt"
    stream = open(file, "r")
    contents = stream.read()
    stream.close()
    n = int(contents)
    stream = open(file, "w")
    stream.write(str(n+1))
    stream.close()
    # answer = int(input("Path(0) or Cycle(1): "))
    answer = 1
    # alt_w1 = int(input("Enter weight for odd segments (1st, 3rd, etc): "))
    alt_w1 = 2
    # alt_w2 = int(input("Enter weight for even segments (2nd, 4th, etc): "))
    alt_w2 = 3
    weights = [alt_w1 if i % 2 == 0 else alt_w2 for i in range(n)]
    print(f"m = {m}, n = {n}, k = {weights}.")
    
    starting_matrix = build_starting_matrix(m)
    path_matrix = make_path_matrix(n)
    result = KroneckerProduct(starting_matrix, path_matrix)
    perm = perm_matrix(swapArray(m, n))
    final = np.dot(np.dot(perm, result), np.transpose(perm)).astype(int)
    if answer:
        final = manual_cycle(final, m, n).astype(int)
    
    dominatingSet = recurvHunter(final, m, weights, verbose=True)
    print("Dominating Set:", dominatingSet)
    stream = open(f"m{m}n{n}Results.txt", "w")
    stream.write(f"m = {m}, n = {n}, k = {weights}")
    stream.write(f"Dominating Set: {dominatingSet}")
    stream.close()
    send_pushover_notification(f"m = {m}, n = {n} is finished.")
    send_pushover_notification(f"m = {m}, n = {n} is finished.", user_key = "upea2iam79bid8wmzwm6rq7p3jgfv3", app_token = "a9o2ouuxqvayb39jpqd4ar4kibd8xy")
    print("--------------------------------------------------------------------------------------------------")

