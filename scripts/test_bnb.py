from utils import read_cbus_file
from cbus_bnb import CBUSBnB

n, k, c = read_cbus_file('cbus_output_20260517_222958/lc101_cbus.txt')
print(f'Testing with n={n}, k={k}')
print(f'Cost matrix range: {min(min(row) for row in c)} - {max(max(row) for row in c)}')

solver = CBUSBnB(n, k, c)
route, cost, elapsed = solver.solve(time_limit=60.0)

print(f'Route: {" ".join(map(str, route))}')
print(f'Cost: {cost}')
print(f'Time: {elapsed:.2f}s')
print(f'Nodes explored: {solver.nodes_explored}')
print(f'Timeout: {solver.aborted}')
