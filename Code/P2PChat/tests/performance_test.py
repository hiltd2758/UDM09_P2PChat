import sys  
import os  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))  
  
from node import P2PNode  
from test_utils import TestMetrics  
import time  
import statistics  
  
class PerformanceTestSuite:  
    def __init__(self):  
        self.metrics = TestMetrics()  
          
    def test_message_latency(self, message_count: int = 1000):  
        """Measure message latency between two nodes"""  
        print(f"Testing message latency with {message_count} messages...")  
          
        latencies = []  
        received_messages = []  
          
        def on_message(peer, msg):  
            received_messages.append((time.time(), msg))  
              
        # Setup nodes  
        node1 = P2PNode(port=12000, on_message=lambda peer, msg: None,  
                       on_status=lambda msg, typ: None, on_peer_update=lambda addr, status: None)  
        node2 = P2PNode(port=12001, on_message=on_message,  
                       on_status=lambda msg, typ: None, on_peer_update=lambda addr, status: None)  
          
        node1.start_server()  
        node2.start_server()  
          
        # Connect nodes  
        node1.connect_peer('127.0.0.1', 12001)  
        time.sleep(1)  
          
        self.metrics.start_monitoring()  
          
        # Send messages and measure latency  
        for i in range(message_count):  
            send_time = time.time()  
            try:  
                node1.send_to('127.0.0.1:12001', f"Latency test {i}")  
                self.metrics.message_count += 1  
                  
                # Wait for message to be received  
                while len(received_messages) <= i:  
                    time.sleep(0.001)  
                      
                recv_time = received_messages[i][0]  
                latency = (recv_time - send_time) * 1000  # Convert to ms  
                latencies.append(latency)  
                  
            except Exception as e:  
                self.metrics.error_count += 1  
                  
        results = self.metrics.stop_monitoring()  
        results.update({  
            'avg_latency_ms': statistics.mean(latencies),  
            'min_latency_ms': min(latencies),  
            'max_latency_ms': max(latencies),  
            'median_latency_ms': statistics.median(latencies),  
            'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)],  
            'p99_latency_ms': sorted(latencies)[int(len(latencies) * 0.99)]  
        })  
          
        # Cleanup  
        node1.shutdown()  
        node2.shutdown()  
          
        return results  
          
    def test_throughput_scaling(self, peer_counts: list = [2, 5, 10, 20]):  
        """Test how throughput scales with number of peers"""  
        print("Testing throughput scaling...")  
          
        results = {}  
          
        for peer_count in peer_counts:  
            print(f"Testing with {peer_count} peers...")  
            
            # Setup main node  
            main_node = P2PNode(port=12000, on_message=lambda peer, msg: None,  
                              on_status=lambda msg, typ: None, on_peer_update=lambda addr, status: None)  
            main_node.start_server()  
              
            # Launch and connect peers  
            from test_utils import launch_peer_instances  
            peers = launch_peer_instances(peer_count - 1, 12001)  
              
            for port in range(12001, 12001 + peer_count - 1):  
                try:  
                    main_node.connect_peer('127.0.0.1', port)  
                except:  
                    pass  
                      
            time.sleep(2)  # Let connections stabilize  
              
            # Measure throughput  
            self.metrics.start_monitoring()  
            start_time = time.time()  
              
            # Send 100 messages to each peer  
            for i in range(100):  
                try:  
                    main_node.broadcast(f"Throughput test {i}")  
                    self.metrics.message_count += 1  
                except:  
                    self.metrics.error_count += 1  
                      
            end_time = time.time()  
            test_results = self.metrics.stop_monitoring()  
              
            results[peer_count] = {  
                'duration': end_time - start_time,  
                'throughput_msg_per_sec': self.metrics.message_count / (end_time - start_time),  
                'avg_cpu': test_results['avg_cpu'],  
                'peak_memory_mb': test_results['peak_memory']  
            }  
              
            # Cleanup  
            main_node.shutdown()  
            for proc in peers:  
                proc.terminate()  
                  
            time.sleep(2)  # Brief pause between tests  
              
        return results  
  
if __name__ == "__main__":  
    # Create results directory  
    os.makedirs('tests/results/logs', exist_ok=True)  
    os.makedirs('tests/results/metrics', exist_ok=True)  
      
    suite = PerformanceTestSuite()  
      
    # Run tests  
    latency_results = suite.test_message_latency(500)  
    throughput_results = suite.test_throughput_scaling([2, 5, 10])  
      
    # Save results  
    import json  
    with open('tests/results/metrics/performance_test_results.json', 'w') as f:  
        json.dump({  
            'latency': latency_results,  
            'throughput_scaling': throughput_results  
        }, f, indent=2)  
      
    print("Performance test completed. Results saved to tests/results/metrics/")