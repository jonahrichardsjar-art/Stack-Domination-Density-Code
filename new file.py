def generate_mod3mod6_sequence(m):
    startPoints = [0] * (2*m)
    current = (2*m)-1
    for i in range(1, m+1):
        startPoints[i] = current
        current = (current + (m-1)) % (2*m)
    current = m - 1
    for j in range(m+1, 2*m):
        startPoints[j] = current
        current = (current + (m-1)) % (2*m)
    return startPoints
