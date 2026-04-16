import sys  
import os  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))  
  
from node import P2PNode  
from test_utils import TestMetrics, launch_peer_instances  
import time  
import threading  
import random  
  
class StressTestSuite:  
    def __init__(self):  
        self.metrics = TestMetrics()  
          
    def test_concurrent_connections(self, max_peers: int = 50):  
        """Test system with many concurrent connections"""  
        print(f"Testing {max_peers} concurrent connections...")  
          
        # Launch main node  
        main_node = P2PNode(  
            port=12000,  
            on_message=lambda peer, msg: None,
            on_status=lambda msg, typ: None,  
            on_peer_update=lambda addr, status: None  
        )  
        main_node.start_server()  
          
        self.metrics.start_monitoring()  
          
        # Launch peer instances  
        peers = launch_peer_instances(max_peers, 12001)  
          
        # Connect all peers to main node  
        connected = 0  
        for i, peer_port in enumerate(range(12001, 12001 + max_peers)):  
            try:  
                main_node.connect_peer('127.0.0.1', peer_port)  
                connected += 1  
                print(f"Connected peer {i+1}/{max_peers}")  
            except Exception as e:  
                self.metrics.error_count += 1  
                print(f"Failed to connect peer {peer_port}: {e}")  
                  
        # Wait for connections to stabilize  
        time.sleep(10)  
          
        # Test broadcasting to all peers  
        for i in range(100):  
            try:  
                main_node.broadcast(f"Stress test message {i}")  
                self.metrics.message_count += 1  
            except Exception as e:  
                self.metrics.error_count += 1  
                  
        results = self.metrics.stop_monitoring()  
          
        # Cleanup  
        main_node.shutdown()  
        for proc in peers:  
            proc.terminate()  
              
        return results  
          
    def test_message_flooding(self, duration: int = 60):  
        """Test system with high message volume"""  
        print(f"Testing message flooding for {duration} seconds...")  
          
        # Setup 2 nodes  
        node1 = P2PNode(port=12000, on_message=lambda peer, msg: None,   
                       on_status=lambda msg, typ: None, on_peer_update=lambda addr, status: None)  
        node2 = P2PNode(port=12001, on_message=lambda peer, msg: None,  
                       on_status=lambda msg, typ: None, on_peer_update=lambda addr, status: None)  
          
        node1.start_server()  
        node2.start_server()  
          
        # Connect nodes  
        node1.connect_peer('127.0.0.1', 12001)  
        time.sleep(1)  
          
        self.metrics.start_monitoring()  
          
        # Flood with messages  
        start_time = time.time()  
        msg_count = 0  
        while time.time() - start_time < duration:  
            try:  
                node1.send_to('127.0.0.1:12001', f"Flood message {msg_count}")  
                self.metrics.message_count += 1  
                msg_count += 1  
            except Exception as e:  
                self.metrics.error_count += 1  
                  
        results = self.metrics.stop_monitoring()  
        results['messages_per_second'] = self.metrics.message_count / duration  
          
        # Cleanup  
        node1.shutdown()  
        node2.shutdown()  
          
        return results  
  
if __name__ == "__main__":  
    # Create results directory  
    os.makedirs('tests/results/logs', exist_ok=True)  
    os.makedirs('tests/results/metrics', exist_ok=True)  
      
    suite = StressTestSuite()  
      
    # Run tests  
    conn_results = suite.test_concurrent_connections(30)  
    flood_results = suite.test_message_flooding(30)  
      
    # Save results  
    import json  
    with open('tests/results/metrics/stress_test_results.json', 'w') as f:  
        json.dump({  
            'concurrent_connections': conn_results,  
            'message_flooding': flood_results  
        }, f, indent=2)  
      
    print("Stress test completed. Results saved to tests/results/metrics/")