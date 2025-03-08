import numpy as np

numNeighbors = 3
numServers = 4
table = {}

table[(0,1)] = 5
table[(1,3)] = 3
# create a 2D array with infinity values
arr = np.full((numNeighbors, numServers), np.inf)
for label in table:
    arr[label[0]][label[1]] = table[label]

print(arr)


print('Routing Table\n----------------------------------')
for i in range(numServers):
   print(' ', i + 1, end=' ')
print()
for i, elem in enumerate(arr):
  print(i + 1, end='|')
  for j in elem:
    print(j, end=' ')
  print('\n')