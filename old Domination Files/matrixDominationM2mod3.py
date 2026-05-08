import numpy as np
import itertools as ite
import time as tm
import copy

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

def KroneckerProduct(M1, M2):
    return np.kron(M1, np.eye(M2.shape[0], dtype=int)) + np.kron(np.eye(M1.shape[0], dtype=int), M2)

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

def reorder_vertices(m):
    inner = list(range(0, m))
    outer = list(range(m, 2 * m))
    inner_reordered = inner[-1:] + inner[:-1]
    outer_reordered = outer[-1:] + outer[:-1]
    return inner_reordered + outer_reordered

def swapArray(m, n):
    return [i + (n * j) for i in range(n) for j in range(2 * m)]

def build_starting_matrix(m):
    part1 = make_cycle_matrix(m)
    part2 = np.eye(m, dtype=int)
    top = np.hstack((part1, part2))
    bottom = np.hstack((part2, part1))
    full = np.vstack((top, bottom))
    relabel_order = reorder_vertices(m)
    return full[np.ix_(relabel_order, relabel_order)]

def prismCycleAdj(m, n):
    starting_matrix = build_starting_matrix(m)
    path_matrix = make_path_matrix(n)
    result = KroneckerProduct(starting_matrix, path_matrix)
    perm = perm_matrix(swapArray(m, n))
    final = np.dot(np.dot(perm, result), np.transpose(perm)).astype(int)
    final = manual_cycle(final, m, n)
    return final

def checker(adjMatrix, biFilter):
    dominated = np.zeros((1, len(biFilter)), int)
    for i in range(len(biFilter)):
        if biFilter[i] == 1:
            dominated += adjMatrix[i]
    return np.all(dominated > 0)

def fiberClock(m, start):
    "Finds a fiber postions that go clockwise."
    domSet = [0] * (2*m)
    position = start
    domSet[position] = 1
    count = 1
    while count < ((m+1)/3):
        if 0 <= position and position < (m - 3): # Outside Good
            position = position + m + 3
        elif (m - 3) <= position and position < m: # Outside Bad
            position = position + 3
        elif m <= position and position < (2*m - 3): # Inside Good
            position = (position + m + 3) % (2*m)
        else: # Inside Bad
            position = (position + 3) % (2*m)
        domSet[position] = 1
        count += 1
    return domSet

def fiberCounter(m, start):
    "Finds a fiber with different positions that go counter-clockwise."
    domSet = [0] * (2*m)
    position = start
    domSet[position] = 1
    count = 1
    while count < ((m+1)/3):
        if 0 <= position and position < 3: # Outside Bad
            position = (position - 3 + (2*m)) % (2*m)
        elif 3 <= position and position < m: # Outside Good
            position = (position - m - 3 + (2*m)) % (2*m)
        elif m <= position and position < (m + 3): # Inside Bad
            position = position - 3
        else: # Inside Good
            position = (position - m - 3)
        domSet[position] = 1
        count += 1
    return domSet

def oddDomination(adjMatrix, m):
    "Finds all dominating sets for Odd m = 2mod3."
    domSets = set()
    set1 = fiberClock(m, 0)
    for i in range(2*m):
        set2 = fiberClock(m, i)
        for j in range(2*m):
            set3 = fiberClock(m, j)
            temp = set1 + set2 + set3
            if checker(adjMatrix, temp):
                domSets.add(tuple(int(x) for x in temp))
                print(f"0, {i}, {j}")
    return domSets

m = 32
print(f"m = {m}")
adj = prismCycleAdj(m, 3)
domSets = oddDomination(adj, m)