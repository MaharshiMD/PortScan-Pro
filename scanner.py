import socket
import threading
from queue import Queue
from datetime import datetime
import json
import csv
import subprocess
import platform
import argparse
import sys
import logging

# Set up logging for professional output tracking
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Common ports dictionary to define frequently used ports and their services
COMMON_PORTS = {
    21: 'FTP',
    22: 'SSH',
    23: 'Telnet',
    25: 'SMTP',
    53: 'DNS',
    80: 'HTTP',
    110: 'POP3',
    143: 'IMAP',
    443: 'HTTPS',
    445: 'SMB',
    3306: 'MySQL',
    3389: 'RDP'
}

class PortScanner:
    """
    A professional network port scanner that uses multithreading to quickly check for open ports,
    verifies host status via ICMP, and exports rich logging details.
    """
    def __init__(self, target, start_port=1, end_port=1024, thread_count=100, use_common_ports=False, timeout=0.5):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.thread_count = thread_count
        self.use_common_ports = use_common_ports
        self.timeout = timeout
        
        self.open_ports = []
        self.closed_ports = []
        self.queue = Queue()
        self.lock = threading.Lock()
        self.target_ip = None
        self.total_scanned = 0

    def resolve_target(self):
        """Resolves hostname to an IPv4 address."""
        try:
            self.target_ip = socket.gethostbyname(self.target)
            return True
        except socket.gaierror:
            return False

    def ping_host(self):
        """Checks if the host is alive using ICMP ping."""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.target_ip]
        try:
            # We redirect standard output and error to avoid console noise
            output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
            return output.returncode == 0
        except Exception:
            return False

    def grab_banner(self, s, port=None):
        """Attempts to grab a service banner from an open connection, using HTTP probes if needed."""
        try:
            # Try to receive passive banner (e.g. SSH, FTP send banners immediately on connection)
            s.settimeout(0.2)
            try:
                banner = s.recv(1024).decode(errors='ignore').strip()
                if banner:
                    return banner.replace('\r', '').replace('\n', ' ')
            except socket.timeout:
                pass
            
            # If no passive banner and it's a typical web port, send a clean HTTP probe
            if port in [80, 443, 8080]:
                probe = "HEAD / HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
                s.sendall(probe.encode())
                s.settimeout(0.5)
                response = s.recv(1024).decode(errors='ignore').strip()
                if response:
                    lines = response.split('\n')
                    server_header = [l.strip() for l in lines if l.lower().startswith('server:')]
                    if server_header:
                        return server_header[0]
                    return lines[0].strip()
            else:
                # Nudge other services with a newline probe
                s.sendall(b"\r\n")
                s.settimeout(0.3)
                banner = s.recv(1024).decode(errors='ignore').strip()
                if banner:
                    return banner.replace('\r', '').replace('\n', ' ')
            
            return "No banner available"
        except Exception:
            return "No banner available"

    def _try_get_service(self, port):
        """Safely gets service name by port from socket library."""
        try:
            return socket.getservbyport(port, "tcp")
        except OSError:
            return "Unknown"

    def scan_port(self, port):
        """Checks a single port to see if it is open."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout) 
            
            result = s.connect_ex((self.target_ip, port))
            
            if result == 0:
                service = COMMON_PORTS.get(port, self._try_get_service(port))
                banner = self.grab_banner(s, port)
                
                with self.lock:
                    self.open_ports.append({
                        'port': port, 
                        'service': service, 
                        'banner': banner
                    })
            else:
                with self.lock:
                    self.closed_ports.append(port)
                    
            s.close()
            
        except Exception:
            with self.lock:
                self.closed_ports.append(port)
                
        # Progress Tracking
        with self.lock:
            self.total_scanned += 1
            if self.total_scanned % 100 == 0:  # simple progress trace for large ranges
                sys.stdout.write('.')
                sys.stdout.flush()

    def worker(self):
        """Worker thread that takes a port from the queue and scans it."""
        while not self.queue.empty():
            port = self.queue.get()
            self.scan_port(port)
            self.queue.task_done()

    def run_scan(self, skip_ping=False):
        """Orchestrates the scanning process using multithreading."""
        if not self.resolve_target():
            return {"error": "Invalid target. Could not resolve hostname/IP."}

        if not skip_ping:
            sys.stdout.write("[*] Verifying host status via ping... ")
            sys.stdout.flush()
            if not self.ping_host():
                print("Host seems DOWN.")
                return {"error": "Host is unresponsive to ICMP pings. Use --skip-ping to bypass this check."}
            print("Host is UP.")

        if self.use_common_ports:
            ports_to_scan = list(COMMON_PORTS.keys())
        else:
            ports_to_scan = range(self.start_port, self.end_port + 1)
        
        for port in ports_to_scan:
            self.queue.put(port)

        start_time = datetime.now()

        # Create and start threads
        thread_list = []
        for _ in range(self.thread_count):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            thread_list.append(t)
            t.start()

        # Block main thread until the queue is empty
        self.queue.join()

        end_time = datetime.now()
        scan_time = (end_time - start_time).total_seconds()

        self.open_ports = sorted(self.open_ports, key=lambda x: x['port'])
        print() # Add newline after progress dots
        
        return {
            "target": self.target,
            "target_ip": self.target_ip,
            "scan_time": scan_time,
            "open_ports": self.open_ports,
            "closed_ports_count": len(self.closed_ports),
            "total_scanned": len(ports_to_scan) // 1 if ports_to_scan else 0
        }

    # EXPORT METHODS
    def export_json(self, result_data, filename="scan_results.json"):
        with open(filename, 'w') as f:
            json.dump(result_data, f, indent=4)
            
    def export_csv(self, result_data, filename="scan_results.csv"):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Port', 'Service', 'Banner'])
            for p in result_data.get('open_ports', []):
                writer.writerow([p['port'], p['service'], p['banner']])
                
    def export_html(self, result_data, filename="scan_results.html"):
        html_content = f"""
        <html>
        <head>
            <title>Port Scan Report: {result_data['target']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; color: #333; }}
                .meta {{ margin-bottom: 20px; background: #fafafa; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h2>🛡️ Network Port Scan Report</h2>
            <div class="meta">
                <p><strong>Target:</strong> {result_data['target']} ({result_data['target_ip']})</p>
                <p><strong>Time Elapsed:</strong> {result_data['scan_time']:.2f} seconds</p>
                <p><strong>Total Scanned:</strong> {result_data['total_scanned']} | <strong>Open:</strong> {len(result_data['open_ports'])}</p>
            </div>
            <table>
                <tr><th>Port</th><th>Service</th><th>Banner / Info</th></tr>
        """
        for p in result_data.get('open_ports', []):
            html_content += f"<tr><td>{p['port']}</td><td>{p['service']}</td><td>{p['banner']}</td></tr>"
            
        html_content += """
            </table>
        </body>
        </html>
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional Network Port Scanner")
    parser.add_argument('target', help="Target IP or Domain (e.g., 192.168.1.1 or example.com)")
    parser.add_argument('-c', '--common', action='store_true', help="Scan common ports only")
    parser.add_argument('-p', '--ports', default="1-1000", help="Port range (e.g., 1-1000, 80-443)")
    parser.add_argument('-t', '--threads', type=int, default=100, help="Number of concurrent threads (default: 100)")
    parser.add_argument('-T', '--timeout', type=float, default=0.5, help="Socket timeout in seconds (default: 0.5)")
    parser.add_argument('--export', choices=['json', 'csv', 'html', 'all'], help="Export report format")
    parser.add_argument('--skip-ping', action='store_true', help="Skip the ICMP discovery ping check")

    args = parser.parse_args()
    
    use_common = args.common
    start_port, end_port = 1, 1000
    
    if not use_common:
        try:
            if '-' in args.ports:
                s, e = args.ports.split('-')
                start_port, end_port = int(s), int(e)
            else:
                start_port = end_port = int(args.ports)
        except ValueError:
            logging.error("[-] Invalid port range format. Use -p START-END")
            sys.exit(1)
            
    logging.info(f"\n[+] Starting scan on {args.target}...")
    
    scanner = PortScanner(
        args.target, 
        start_port=start_port, 
        end_port=end_port, 
        thread_count=args.threads, 
        use_common_ports=use_common, 
        timeout=args.timeout
    )
    
    results = scanner.run_scan(skip_ping=args.skip_ping)
    
    if "error" in results:
        logging.error(f"[-] Error: {results['error']}")
        sys.exit(1)
        
    logging.info(f"\n[+] Scan completed in {results['scan_time']:.2f} seconds.")
    logging.info(f"[+] Target IP: {results['target_ip']}")
    logging.info(f"[+] Total Ports Scanned: {results['total_scanned']}")
    logging.info(f"[+] Open Ports Found: {len(results['open_ports'])}")
    
    logging.info("\n" + "-"*75)
    logging.info(f"{'PORT':<8} | {'SERVICE':<15} | {'BANNER/INFO'}")
    logging.info("-" * 75)
    
    for port_info in results['open_ports']:
        banner_text = port_info['banner'][:45] + "..." if len(port_info['banner']) > 45 else port_info['banner']
        logging.info(f"{port_info['port']:<8} | {port_info['service']:<15} | {banner_text}")
        
    logging.info("-" * 75)
    
    # Handle Exports
    if args.export:
        formats = ['json', 'csv', 'html'] if args.export == 'all' else [args.export]
        for f in formats:
            if f == 'json':
                scanner.export_json(results)
                logging.info("[+] Saved results to scan_results.json")
            elif f == 'csv':
                scanner.export_csv(results)
                logging.info("[+] Saved results to scan_results.csv")
            elif f == 'html':
                scanner.export_html(results)
                logging.info("[+] Saved results to scan_results.html")
