import json
import os
import matplotlib.pyplot as plt

# Load results
with open('tests/results/metrics/stress_test_results.json') as f:
    stress = json.load(f)

with open('tests/results/metrics/performance_test_results.json') as f:
    perf = json.load(f)

os.makedirs('tests/results/metrics', exist_ok=True)

# ── Stress Test Chart ──
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Stress Test Results', fontsize=14)

# Concurrent connections
cc = stress['concurrent_connections']
axes[0].bar(['CPU %', 'Memory (MB)', 'Errors'],
            [cc['avg_cpu'], cc['peak_memory'], cc['errors']],
            color=['#4CAF50', '#2196F3', '#F44336'])
axes[0].set_title(f"Concurrent Connections\n{cc['messages_sent']} msgs in {cc['duration']:.1f}s")

# Message flooding
mf = stress['message_flooding']
axes[1].bar(['CPU %', 'Memory (MB)', 'msg/s (÷1000)'],
            [mf['avg_cpu'], mf['peak_memory'], mf['messages_per_second'] / 1000],
            color=['#4CAF50', '#2196F3', '#FF9800'])
axes[1].set_title(f"Message Flooding\n{mf['messages_per_second']:.0f} msg/s")

plt.tight_layout()
plt.savefig('tests/results/metrics/stress_report.png')
plt.close()
print("Saved: stress_report.png")

# ── Latency Chart ──
lat = perf['latency']
fig, ax = plt.subplots(figsize=(8, 5))
labels = ['min', 'avg', 'median', 'p95', 'p99', 'max']
values = [lat['min_latency_ms'], lat['avg_latency_ms'], lat['median_latency_ms'],
          lat['p95_latency_ms'], lat['p99_latency_ms'], lat['max_latency_ms']]
ax.bar(labels, values, color='#2196F3')
ax.set_title('Message Latency (ms)')
ax.set_ylabel('Latency (ms)')
for i, v in enumerate(values):
    ax.text(i, v + 0.01, f'{v:.3f}', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('tests/results/metrics/latency_report.png')
plt.close()
print("Saved: latency_report.png")

# ── Throughput Scaling Chart ──
tp = perf['throughput_scaling']
peers = [int(k) for k in tp.keys()]
tps   = [tp[k]['throughput_msg_per_sec'] for k in tp.keys()]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(peers, tps, marker='o', color='#4CAF50')
ax.set_title('Throughput Scaling')
ax.set_xlabel('Number of Peers')
ax.set_ylabel('Messages/sec')
ax.set_xticks(peers)
plt.tight_layout()
plt.savefig('tests/results/metrics/throughput_report.png')
plt.close()
print("Saved: throughput_report.png")

print("\nAll reports saved to tests/results/metrics/")