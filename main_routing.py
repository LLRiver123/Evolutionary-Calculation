import sys

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

def read_input():
    data = sys.stdin.read().split()
    if not data:
        return None
    if len(data) < 2:
        raise ValueError("Input Error")

    n = int(data[0])
    k = int(data[1])
    size = 2 * n + 1
    expected = 2 + size * size
    if len(data) < expected:
        raise ValueError(
            f"Input Error."
        )
    if len(data) > expected:
        data = data[:expected]

    c = [[0] * size for _ in range(size)]
    idx = 2
    for i in range(size):
        row = c[i]
        for j in range(size):
            row[j] = int(data[idx])
            idx += 1
    return n, k, c

def greedy_route(n, k, c):
    m = 2 * n
    unpicked = set(range(1, n + 1))
    onboard = set()
    route = []
    current = 0
    while len(route) < m:
        candidates = []
        if onboard and (len(onboard) == k or not unpicked):
            candidates = [p + n for p in onboard]
        else:
            candidates = list(unpicked)
            if not candidates and onboard:
                candidates = [p + n for p in onboard]
        next_node = min(candidates, key=lambda v: c[current][v])
        route.append(next_node)
        if 1 <= next_node <= n:
            unpicked.remove(next_node)
            onboard.add(next_node)
        else:
            passenger = next_node - n
            if passenger in onboard:
                onboard.remove(passenger)
        current = next_node
    return route

def solve(n, k, c, time_limit_seconds=30):
    """
    Giải CBUS problem bằng OR-Tools Guided Local Search
    
    Args:
        n: số điểm đón
        k: sức chứa xe
        c: cost matrix
        time_limit_seconds: giới hạn thời gian
    
    Returns:
        route: list các nodes từ 1 đến 2n
    """
    node_count = 2 * n + 1
    max_c = max(max(row) for row in c)
    max_dist = max_c * (2 * n + 1)

    manager = pywrapcp.RoutingIndexManager(node_count, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    flat = [0] * (node_count * node_count)
    for i in range(node_count):
        base = i * node_count
        row = c[i]
        for j in range(node_count):
            flat[base + j] = row[j]

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return flat[from_node * node_count + to_node]

    transit_cb_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_index)

    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        if 1 <= node <= n:
            return 1
        if n < node <= 2 * n:
            return -1
        return 0

    demand_cb_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_cb_index,
        0,
        [k],
        True,
        "Capacity",
    )

    routing.AddDimension(
        transit_cb_index,
        0,
        max_dist,
        True,
        "Distance",
    )

    routing.AddConstantDimension(
        1,
        2 * n + 1,
        True,
        "Order",
    )
    order_dimension = routing.GetDimensionOrDie("Order")

    solver = routing.solver()
    for i in range(1, n + 1):
        pickup = manager.NodeToIndex(i)
        delivery = manager.NodeToIndex(i + n)
        routing.AddPickupAndDelivery(pickup, delivery)
        solver.Add(routing.VehicleVar(pickup) == routing.VehicleVar(delivery))
        solver.Add(order_dimension.CumulVar(pickup) < order_dimension.CumulVar(delivery))


    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.FromSeconds(int(time_limit_seconds))
    search_params.use_full_propagation = True
    search_params.lns_time_limit.FromSeconds(max(1, int(time_limit_seconds / 6)))
    search_params.log_search = False

    greedy = greedy_route(n, k, c)
    assignment = routing.ReadAssignmentFromRoutes([greedy], True)
    if assignment is not None:
        solution = routing.SolveFromAssignmentWithParameters(assignment, search_params)
    else:
        solution = routing.SolveWithParameters(search_params)
    if solution is None:
        return greedy_route(n, k, c)

    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node != 0:
            route.append(node)
        index = solution.Value(routing.NextVar(index))

    if len(route) != 2 * n:
        return greedy_route(n, k, c)
    return route

def main():
    parsed = read_input()
    if parsed is None:
        return
    n, k, c = parsed
    route = solve(n, k, c)
    print(n)
    if route:
        print(" ".join(str(x) for x in route))
    else:
        print("")

if __name__ == "__main__":
    main()
