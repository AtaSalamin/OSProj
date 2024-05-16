#made by Ata Salamin
import heapq
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.start = None
        self.finish = None
        self.waiting = None
        self.turnaround = None
        self.remaining = burst


def create_processes(data):
    processes = []
    for d in data:
        processes.append(Process(pid=d[0], arrival=d[1], burst=d[2]))
    return processes


def calculate_metrics(processes):
    for p in processes:
        p.turnaround = p.finish - p.arrival
        p.waiting = p.turnaround - p.burst


def print_results(processes, gantt_chart, total_time):
    print("Results:")
    for p in processes:
        print(
            f"Process {p.pid}: Finish time = {p.finish}, Waiting time = {p.waiting}, Turnaround time = {p.turnaround}")
    cpu_utilization = (total_time - sum(p.waiting for p in processes)) / total_time * 100
    print(f"CPU Utilization: {cpu_utilization:.2f}%")

#made by Ata Salamin
def plot_gantt_chart(gantt_chart, title, processes):
    fig, gnt = plt.subplots(figsize=(15, 8))

    colors = plt.cm.tab20.colors  # Use a colormap with 20 distinct colors
    process_colors = {p.pid: colors[i % len(colors)] for i, p in enumerate(processes)}

    y_ticks = [15 + 10 * i for i in range(len(processes))]
    process_ids = [f'P{p.pid}' for p in processes]

    gnt.set_ylim(0, 10 * (len(processes) + 1))
    gnt.set_xlim(0, max(end for _, end, _ in gantt_chart) + 5)

    gnt.set_xlabel('Time')
    gnt.set_ylabel('Processes')

    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(process_ids)

    gnt.grid(True)

    last_end_time = 0
    for start, end, pid in gantt_chart:
        if start > last_end_time:
            # Highlight idle time
            gnt.broken_barh([(last_end_time, start - last_end_time)], (y_ticks[0] - 5, y_ticks[-1] - y_ticks[0] + 10),
                            facecolors=('lightgray'))
            gnt.text((last_end_time + start) / 2, y_ticks[-1] + 5, "Idle", ha='center', va='center', color='black',
                     fontsize=10)
        last_end_time = end

    for start, end, pid in gantt_chart:
        gnt.broken_barh([(start, end - start)], (y_ticks[pid - 1] - 5, 9), facecolors=(process_colors[pid]))
        gnt.text(start + (end - start) / 2, y_ticks[pid - 1], f"P{pid}", ha='center', va='center', color='white',
                 fontsize=10)
        gnt.text(start, y_ticks[pid - 1] + 5, f"{start}", ha='center', va='bottom', color='black', fontsize=8)
        gnt.text(end, y_ticks[pid - 1] + 5, f"{end}", ha='center', va='bottom', color='black', fontsize=8)

    #made by Ata Salamin
    patches = [mpatches.Patch(color=color, label=f'P{pid}') for pid, color in process_colors.items()]
    idle_patch = mpatches.Patch(color='lightgray', label='Idle')
    plt.legend(handles=patches + [idle_patch], loc='upper right', title="Processes")

    plt.title(title)
    plt.tight_layout()
    plt.show()

    # Save plot as image also made by Ata Salamin
    fig.savefig(f"{title.replace(' ', '_')}.png")


def fcfs_scheduling(processes, context_switch):
    processes.sort(key=lambda x: x.arrival)
    time = 0
    gantt_chart = []
    for p in processes:
        if time < p.arrival:
            time = p.arrival
        p.start = time
        gantt_chart.append((time, time + p.burst, p.pid))
        time += p.burst + context_switch
        p.finish = time
    calculate_metrics(processes)
    print_results(processes, gantt_chart, time)
    plot_gantt_chart(gantt_chart, "FCFS Scheduling", processes)


def srt_scheduling(processes, context_switch):
    time = 0
    ready_queue = []
    gantt_chart = []
    processes.sort(key=lambda x: x.arrival)
    i = 0
    while i < len(processes) or ready_queue:
        while i < len(processes) and processes[i].arrival <= time:
            heapq.heappush(ready_queue, (processes[i].remaining, i))
            i += 1
        if ready_queue:
            remaining, index = heapq.heappop(ready_queue)
            if processes[index].start is None:
                processes[index].start = time
            execution_time = min(remaining, processes[i].arrival - time if i < len(processes) else remaining)
            gantt_chart.append((time, time + execution_time, processes[index].pid))
            processes[index].remaining -= execution_time
            time += execution_time
            if processes[index].remaining > 0:
                heapq.heappush(ready_queue, (processes[index].remaining, index))
            else:
                processes[index].finish = time + context_switch
                time += context_switch
        else:
            time = processes[i].arrival
    calculate_metrics(processes)
    print_results(processes, gantt_chart, time)
    plot_gantt_chart(gantt_chart, "SRT Scheduling", processes)


def rr_scheduling(processes, time_quantum, context_switch):
    time = 0
    ready_queue = deque()
    gantt_chart = []
    processes.sort(key=lambda x: x.arrival)
    i = 0
    while i < len(processes) or ready_queue:
        while i < len(processes) and processes[i].arrival <= time:
            ready_queue.append(i)
            i += 1
        if ready_queue:
            index = ready_queue.popleft()
            if processes[index].start is None:
                processes[index].start = time
            execution_time = min(processes[index].remaining, time_quantum)
            gantt_chart.append((time, time + execution_time, processes[index].pid))
            processes[index].remaining -= execution_time
            time += execution_time
            if processes[index].remaining > 0:
                ready_queue.append(index)
            else:
                processes[index].finish = time + context_switch
                time += context_switch
        else:
            time = processes[i].arrival
    calculate_metrics(processes)
    print_results(processes, gantt_chart, time)
    plot_gantt_chart(gantt_chart, "Round-Robin Scheduling", processes)


def read_data_from_file(filename):
    data = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.split()
            pid = int(parts[0])
            arrival = int(parts[1])
            burst = int(parts[2])
            data.append((pid, arrival, burst))
    return data
#made by Ata Salamin
data_file='processes.txt'
data = read_data_from_file(data_file)

context_switch = 1
time_quantum = 4

processes = create_processes(data)
print("FCFS Scheduling: ")
fcfs_scheduling(processes, context_switch)

processes = create_processes(data)
print("\nSRT Scheduling: ")
srt_scheduling(processes, context_switch)

processes = create_processes(data)
print("\nRound-Robin Scheduling: ")
rr_scheduling(processes, time_quantum, context_switch)

