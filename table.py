numServers = 4
numNeighbors = 3

table = {}

for i in range (numServers):
    for j in range (numNeighbors):
        table[(i + 1, j + 1)] = float('inf')

table[(1, 2)] = 6

print(table)