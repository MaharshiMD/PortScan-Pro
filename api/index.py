from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add root folder to sys.path so we can import scanner.py
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from scanner import PortScanner

app = Flask(__name__)
CORS(app)

@app.route('/api/scan', methods=['POST'])
def run_web_scan():
    try:
        data = request.json or {}
        target = data.get('target', '').strip()
        
        if not target:
            return jsonify({"error": "Target IP address or domain name is required."}), 400
            
        use_common = data.get('use_common', True)
        start_port = data.get('start_port', 1)
        end_port = data.get('end_port', 1024)
        threads = data.get('threads', 50)
        timeout = data.get('timeout', 0.3)
        skip_ping = data.get('skip_ping', True)  # Default to True for serverless execution

        # Clean/cast inputs
        try:
            threads = min(max(int(threads), 1), 100) # Clamp threads between 1 and 100 for safety
            timeout = min(max(float(timeout), 0.1), 3.0) # Clamp timeout between 0.1s and 3.0s
            start_port = int(start_port)
            end_port = int(end_port)
        except ValueError:
            return jsonify({"error": "Threads, timeout, and ports must be valid numbers."}), 400

        # Safety boundary: serverless execution limits
        if not use_common:
            if start_port < 1 or end_port > 65535 or start_port > end_port:
                return jsonify({"error": "Invalid port range. Ensure start port is <= end port, and ports are between 1 and 65535."}), 400
            
            total_ports = end_port - start_port + 1
            if total_ports > 150:
                return jsonify({
                    "error": "For security and serverless timeout reasons, the web scan is limited to a maximum of 150 custom ports. For unlimited scanning, please use the CLI tool (scanner.py) or Desktop app (gui.py)."
                }), 400

        scanner = PortScanner(
            target=target,
            start_port=start_port,
            end_port=end_port,
            thread_count=threads,
            use_common_ports=use_common,
            timeout=timeout
        )

        # Execute scan
        results = scanner.run_scan(skip_ping=skip_ping)
        
        if "error" in results:
            return jsonify({"error": results["error"]}), 400
            
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": f"Internal server scanner error: {str(e)}"}), 500

# For testing or run locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
