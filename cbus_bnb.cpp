// CBUS - Pickup and Delivery Problem (n < 15)
//
// Bộ giải Branch-and-Bound (DFS + pruning) cho mô hình CBUS.
// Tương đương về kết quả với mô hình MIP trong ToiUuLapKeHoach.pdf
// nhưng không cần thư viện ngoài — chỉ cần g++.
//
// Các ràng buộc được tôn trọng đầy đủ:
//   * Mỗi điểm trong {1..2n} ghé đúng một lần, xuất phát và quay về 0
//   * Pickup i ghé trước Delivery i+n
//   * Sức chứa [0, k] tại mọi bước
//   * Tối thiểu hóa tổng quãng đường
//
// Pruning:
//   1. Cận dưới = chi phí hiện tại + Σ_j min_in[j] (j chưa thăm) + min_in[0]
//      (mỗi điểm sẽ phải được "vào" ít nhất một lần với cạnh rẻ nhất)
//   2. Khởi tạo upper bound bằng nearest-neighbor (có tôn trọng precedence + capacity)
//   3. Sắp xếp ứng viên theo c[cur][j] tăng dần (best-first nội bộ)
//
// I/O:
//   stdin/file:
//     n k
//     ma trận (2n+1) x (2n+1)
//   stdout:
//     n
//     v_1 ... v_{2n}      (-1 nếu không khả thi)
//
// Build:  g++ -O2 -std=c++17 cbus_bnb.cpp -o cbus_bnb
// Run:    ./cbus_bnb [--time SECONDS] [input.txt]

#include <algorithm>
#include <chrono>
#include <climits>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using namespace std;
using Clock = chrono::steady_clock;

struct Solver {
    int n = 0, k = 0, N = 0;
    vector<vector<int>> c;
    vector<int> q;          // +1 pickup, -1 delivery, 0 depot
    vector<int> min_in;     // min incoming edge for each node

    long long best_cost = LLONG_MAX;
    vector<int> best_route;
    vector<int> cur_route;

    Clock::time_point start;
    double time_limit_sec = 60.0;
    bool aborted = false;
    long long nodes_explored = 0;

    bool time_up() {
        if ((nodes_explored & 0xFFFF) != 0) return aborted;
        double e = chrono::duration<double>(Clock::now() - start).count();
        if (e > time_limit_sec) aborted = true;
        return aborted;
    }

    long long lower_bound_remaining(uint32_t visited) const {
        long long lb = min_in[0];
        for (int j = 1; j < N; j++) {
            if (!(visited & (1u << (j - 1)))) lb += min_in[j];
        }
        return lb;
    }

    void dfs(int cur, uint32_t visited, int load, long long cost) {
        ++nodes_explored;
        if (time_up()) return;
        if (cost >= best_cost) return;

        const uint32_t full = (n == 0) ? 0u : ((1u << (2 * n)) - 1u);
        if (visited == full) {
            long long total = cost + c[cur][0];
            if (total < best_cost) {
                best_cost = total;
                best_route = cur_route;
            }
            return;
        }

        if (cost + lower_bound_remaining(visited) >= best_cost) return;

        // gather feasible candidates, sorted by edge cost
        vector<pair<int, int>> cand;
        cand.reserve(2 * n);
        for (int j = 1; j <= 2 * n; j++) {
            if (visited & (1u << (j - 1))) continue;
            if (j > n) {
                int p = j - n;
                if (!(visited & (1u << (p - 1)))) continue;
            }
            int nl = load + q[j];
            if (nl < 0 || nl > k) continue;
            cand.emplace_back(c[cur][j], j);
        }
        sort(cand.begin(), cand.end());

        for (auto [d, j] : cand) {
            cur_route.push_back(j);
            dfs(j, visited | (1u << (j - 1)), load + q[j], cost + d);
            cur_route.pop_back();
            if (aborted) return;
        }
    }

    void nearest_neighbor_seed() {
        int cur = 0, load = 0;
        long long cost = 0;
        uint32_t visited = 0;
        vector<int> route;
        for (int step = 0; step < 2 * n; step++) {
            int bj = -1, bd = INT_MAX;
            for (int j = 1; j <= 2 * n; j++) {
                if (visited & (1u << (j - 1))) continue;
                if (j > n && !(visited & (1u << (j - n - 1)))) continue;
                int nl = load + q[j];
                if (nl < 0 || nl > k) continue;
                if (c[cur][j] < bd) { bd = c[cur][j]; bj = j; }
            }
            if (bj == -1) return;
            route.push_back(bj);
            cost += c[cur][bj];
            visited |= 1u << (bj - 1);
            load += q[bj];
            cur = bj;
        }
        cost += c[cur][0];
        if (cost < best_cost) { best_cost = cost; best_route = route; }
    }

    bool read_input(istream& in) {
        if (!(in >> n >> k)) return false;
        N = 2 * n + 1;
        c.assign(N, vector<int>(N, 0));
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                if (!(in >> c[i][j])) return false;
        q.assign(N, 0);
        for (int i = 1; i <= n; i++) q[i] = 1;
        for (int i = n + 1; i <= 2 * n; i++) q[i] = -1;
        min_in.assign(N, INT_MAX);
        for (int j = 0; j < N; j++) {
            int m = INT_MAX;
            for (int i = 0; i < N; i++) if (i != j) m = min(m, c[i][j]);
            min_in[j] = m;
        }
        return true;
    }

    void solve() {
        start = Clock::now();
        nearest_neighbor_seed();
        cur_route.clear();
        dfs(0, 0u, 0, 0);
    }

    void write_output(ostream& out) const {
        if (best_route.empty()) { out << -1 << "\n"; return; }
        out << n << "\n";
        for (size_t i = 0; i < best_route.size(); i++) {
            if (i) out << " ";
            out << best_route[i];
        }
        out << "\n";
    }
};

int main(int argc, char** argv) {
    Solver s;
    string path;
    bool verbose = false;
    for (int i = 1; i < argc; i++) {
        string a = argv[i];
        if (a == "--time" && i + 1 < argc) s.time_limit_sec = atof(argv[++i]);
        else if (a == "--verbose" || a == "-v") verbose = true;
        else if (!a.empty() && a[0] != '-') path = a;
    }

    if (!path.empty()) {
        ifstream fin(path);
        if (!fin) { cerr << "cannot open " << path << "\n"; return 2; }
        if (!s.read_input(fin)) { cerr << "bad input\n"; return 2; }
    } else {
        if (!s.read_input(cin)) { cerr << "bad input\n"; return 2; }
    }

    s.solve();
    s.write_output(cout);

    if (verbose) {
        double e = chrono::duration<double>(Clock::now() - s.start).count();
        cerr << "# n=" << s.n << " k=" << s.k << "\n";
        cerr << "# objective=" << s.best_cost << "\n";
        cerr << "# wall_time=" << e << "s\n";
        cerr << "# nodes_explored=" << s.nodes_explored << "\n";
        cerr << "# status=" << (s.aborted ? "TIME_LIMIT" : "OPTIMAL") << "\n";
    }
    return 0;
}
