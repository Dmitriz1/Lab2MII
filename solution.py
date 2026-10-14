import time
import gc
import collections


class Node:
    __slots__ = ("value", "next")

    def __init__(self, value, next=None):
        self.value = value
        self.next = next

# ---------------------- Задание 1б: Задача Иосифа Флавия ----------------------

def josephus_array(n: int, k: int) -> int:
    """
    Задача Иосифа Флавия на массиве (флаги alive).
    """
    if n <= 0:
        return None
    if n == 1:
        return 0

    alive = [True] * n
    idx = 0
    remaining = n

    while remaining > 1:
        steps = (k - 1) % remaining

        while steps > 0:
            idx = (idx + 1) % n
            if alive[idx]:
                steps -= 1

        alive[idx] = False
        remaining -= 1

        idx = (idx + 1) % n
        while not alive[idx]:
            idx = (idx + 1) % n

    for i in range(n):
        if alive[i]:
            return i


def josephus_linked(n: int, k: int) -> int:
    """
    Задача Иосифа Флавия на круговом односвязном списке.
    """
    if n <= 0:
        return None
    if n == 1:
        return 0

    head = Node(0)
    prev = head
    for i in range(1, n):
        node = Node(i)
        prev.next = node
        prev = node
    prev.next = head

    cur = head
    prev = prev
    remaining = n

    while remaining > 1:
        steps = (k - 1) % remaining
        for _ in range(steps):
            prev = cur
            cur = cur.next

        prev.next = cur.next
        cur = cur.next
        remaining -= 1

    return cur.value


def bench_josephus():
    print("\n=== Задание 1б: Задача Иосифа Флавия ===")
    print("N,k,array_time_s,linked_time_s,survivor_array,survivor_linked")

    sizes = [1000, 2000, 5000, 10000]
    for n in sizes:
        for k in [2, 10, 100, n // 2]:
            gc.collect()

            t0 = time.perf_counter()
            s_arr = josephus_array(n, k)
            t1 = time.perf_counter()

            s_lst = josephus_linked(n, k)
            t2 = time.perf_counter()

            print(f"{n},{k},{t1 - t0:.6f},{t2 - t1:.6f},{s_arr},{s_lst}")


# ---------------------- Задание 2: FIFO Queue ----------------------

class LinkedQueue:
    """
    Собственная FIFO-очередь на указателях/ссылках.
    enqueue: O(1)
    dequeue: O(1)
    Память: O(size)
    """
    __slots__ = ("head", "tail", "size")

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def enqueue(self, value):
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def dequeue(self):
        if self.head is None:
            raise IndexError("dequeue from empty queue")

        node = self.head
        self.head = node.next

        if self.head is None:
            self.tail = None

        self.size -= 1
        return node.value


def percentile(sorted_times, p):
    if not sorted_times:
        return 0
    idx = int(round((p / 100.0) * (len(sorted_times) - 1)))
    return sorted_times[idx]


def run_queue_scenario(enqueue, dequeue, n_ops: int, target_size: int):
    size = 0

    for i in range(target_size):
        enqueue(i)
        size += 1

    times_ns = []

    for i in range(n_ops):
        t0 = time.perf_counter_ns()

        if i % 2 == 0 or size == 0:
            enqueue(i)
            size += 1
        else:
            dequeue()
            size -= 1

        t1 = time.perf_counter_ns()
        times_ns.append(t1 - t0)

    return times_ns


def queue_stats(times_ns):
    total_s = sum(times_ns) / 1e9
    mean_ns = sum(times_ns) / len(times_ns)
    worst_ns = max(times_ns)

    sorted_times = sorted(times_ns)
    p99_ns = percentile(sorted_times, 99.0)
    p999_ns = percentile(sorted_times, 99.9)

    return total_s, mean_ns, worst_ns, p99_ns, p999_ns


def bench_queue(sizes):
    print("\n=== Задание 2: FIFO Queue ===")
    print("impl: custom = LinkedQueue, std = collections.deque")
    print("N,scenario,impl,total_s,mean_ns,worst_ns,p99_ns,p99.9_ns")

    scenarios = [
        ("avg_size~N/5", lambda n: n // 5),
        ("avg_size~10", lambda n: 10),
    ]

    for n_ops in sizes:
        for scenario_name, target_fn in scenarios:
            target = target_fn(n_ops)

            # custom
            gc.collect()
            q_custom = LinkedQueue()
            times_custom = run_queue_scenario(
                q_custom.enqueue,
                q_custom.dequeue,
                n_ops,
                target,
            )
            total_s, mean_ns, worst_ns, p99_ns, p999_ns = queue_stats(times_custom)
            print(
                f"{n_ops},{scenario_name},custom,"
                f"{total_s:.6f},{mean_ns:.2f},{worst_ns},{p99_ns},{p999_ns}"
            )

            # standard
            gc.collect()
            q_std = collections.deque()
            times_std = run_queue_scenario(
                q_std.append,
                q_std.popleft,
                n_ops,
                target,
            )
            total_s, mean_ns, worst_ns, p99_ns, p999_ns = queue_stats(times_std)
            print(
                f"{n_ops},{scenario_name},std,"
                f"{total_s:.6f},{mean_ns:.2f},{worst_ns},{p99_ns},{p999_ns}"
            )


if __name__ == "__main__":
    # Задание 1б
    bench_josephus()

    # Задание 2
    bench_queue([10**4, 10**5, 10**6])