import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from scanner import PortScanner

class PortScannerGUI:
    """
    A professional Tkinter-based Graphical User Interface for the Network Port Scanner.
    Features progress tracking, threading limits, and advanced export options.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("PortScan Pro - Advanced GUI")
        self.root.geometry("750x700")
        self.root.resizable(False, False)
        
        # UI Styling using ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, font=("Helvetica", 10))
        style.configure("TLabel", padding=5, font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), padding=10)
        
        # Main Container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header Label
        header_lbl = ttk.Label(main_frame, text="🛡️ PortScan Pro", style="Header.TLabel")
        header_lbl.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Settings Container
        settings_frame = ttk.LabelFrame(main_frame, text="Scanner Settings", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Column 1: Target & Range
        ttk.Label(settings_frame, text="Target (IP/Domain):").grid(row=0, column=0, sticky=tk.W)
        self.target_entry = ttk.Entry(settings_frame, width=30)
        self.target_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        ttk.Label(settings_frame, text="Scan Type:").grid(row=1, column=0, sticky=tk.W)
        self.scan_type_var = tk.StringVar(value="common")
        
        radio_frame = ttk.Frame(settings_frame)
        radio_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(radio_frame, text="Common Ports", variable=self.scan_type_var, value="common", command=self.toggle_range).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(radio_frame, text="Custom Range", variable=self.scan_type_var, value="custom", command=self.toggle_range).pack(side=tk.LEFT)
        
        self.range_frame = ttk.Frame(settings_frame)
        self.range_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.range_frame, text="Start:").pack(side=tk.LEFT)
        self.start_port_entry = ttk.Entry(self.range_frame, width=6)
        self.start_port_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.start_port_entry.insert(0, "1")
        self.start_port_entry.config(state="disabled")
        
        ttk.Label(self.range_frame, text="End:").pack(side=tk.LEFT)
        self.end_port_entry = ttk.Entry(self.range_frame, width=6)
        self.end_port_entry.pack(side=tk.LEFT)
        self.end_port_entry.insert(0, "1024")
        self.end_port_entry.config(state="disabled")
        
        # Column 2: Advanced Settings
        ttk.Label(settings_frame, text="Threads:").grid(row=0, column=2, sticky=tk.E, padx=(30, 5))
        self.thread_entry = ttk.Entry(settings_frame, width=8)
        self.thread_entry.grid(row=0, column=3, sticky=tk.W, pady=5)
        self.thread_entry.insert(0, "150")

        ttk.Label(settings_frame, text="Timeout (s):").grid(row=1, column=2, sticky=tk.E, padx=(30, 5))
        self.timeout_entry = ttk.Entry(settings_frame, width=8)
        self.timeout_entry.grid(row=1, column=3, sticky=tk.W, pady=5)
        self.timeout_entry.insert(0, "0.5")

        self.skip_ping_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Skip Ping Check", variable=self.skip_ping_var).grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=(30, 5))
        
        # Export settings
        bottom_settings = ttk.Frame(settings_frame)
        bottom_settings.grid(row=3, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)
        ttk.Label(bottom_settings, text="Export Format:").pack(side=tk.LEFT)
        self.export_var = tk.StringVar(value="JSON")
        self.export_combo = ttk.Combobox(bottom_settings, textvariable=self.export_var, values=("JSON", "CSV", "HTML"), state="readonly", width=8)
        self.export_combo.pack(side=tk.LEFT, padx=10)

        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.scan_btn = ttk.Button(btn_frame, text="▶ Start Scan", command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Save Results", command=self.save_results, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🧹 Clear Output", command=self.clear_fields)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=700, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, pady=(5, 10))
        
        # Output Log 
        self.results_area = scrolledtext.ScrolledText(main_frame, width=85, height=20, font=("Consolas", 9), bg="#f8f9fa")
        self.results_area.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.current_results = None
        self.scanner_instance = None

    def toggle_range(self):
        if self.scan_type_var.get() == "custom":
            self.start_port_entry.config(state="normal")
            self.end_port_entry.config(state="normal")
        else:
            self.start_port_entry.config(state="disabled")
            self.end_port_entry.config(state="disabled")

    def log(self, msg):
        self.results_area.insert(tk.END, msg + "\n")
        self.results_area.see(tk.END)

    def start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target IP address or domain name.")
            return
            
        use_common = self.scan_type_var.get() == "common"
        start_port, end_port = 1, 1024
        
        if not use_common:
            try:
                start_port = int(self.start_port_entry.get())
                end_port = int(self.end_port_entry.get())
                if start_port > end_port or start_port < 1 or end_port > 65535:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid port range. Ensure they are numbers between 1 and 65535, and start <= end.")
                return

        try:
            threads = int(self.thread_entry.get())
            timeout = float(self.timeout_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Threads must be an integer and Timeout must be a number.")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.results_area.delete(1.0, tk.END)
        self.current_results = None
        
        # Reset progress bar
        self.progress["value"] = 0
        total_ports = 12 if use_common else (end_port - start_port + 1) # 12 common ports currently
        self.progress["maximum"] = total_ports
        
        self.log(f"[*] Initializing Professional Scan on target: {target}")
        self.log(f"[*] Threads: {threads} | Timeout: {timeout}s")
        self.log(f"[*] Please wait while scanning...")
        
        self.scanner_instance = PortScanner(
            target, 
            start_port, 
            end_port, 
            thread_count=threads, 
            use_common_ports=use_common,
            timeout=timeout
        )
        
        # Start a UI update loop for the progress bar
        self.update_progress()
            
        threading.Thread(target=self.run_scanner, args=(self.scanner_instance, self.skip_ping_var.get()), daemon=True).start()

    def update_progress(self):
        if self.scanner_instance:
            current_scanned = self.scanner_instance.total_scanned
            self.progress["value"] = current_scanned
            
            # Continue updating until done
            if self.scan_btn["state"] == tk.DISABLED:
                self.root.after(100, self.update_progress)

    def run_scanner(self, scanner, skip_ping):
        # We catch any return dict from run_scan which contains errors or results
        # To pass output back to UI, we must use after()
        try:
            results = scanner.run_scan(skip_ping=skip_ping)
            self.root.after(0, self.update_ui_scan_complete, results)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"\n[-] Unexpected crash: {str(e)}"))
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

    def update_ui_scan_complete(self, results):
        self.progress["value"] = self.progress["maximum"] # complete bar
        self.scan_btn.config(state=tk.NORMAL)
        
        if "error" in results:
            self.log(f"\n[-] Critical Error: {results['error']}")
            return
            
        self.current_results = results
        self.save_btn.config(state=tk.NORMAL)
        
        self.log(f"\n[+] Target IP Resolved: {results['target_ip']}")
        self.log(f"[+] Total Time Elapsed: {results['scan_time']:.2f} seconds")
        self.log(f"[+] Ports Evaluated:    {results['total_scanned']}")
        self.log(f"[+] Closed/Filtered:    {results['closed_ports_count']}")
        self.log(f"[+] Open Ports Found:   {len(results['open_ports'])}\n")
        
        self.log(f"{'PORT':<8} | {'SERVICE':<15} | {'BANNER INFO'}")
        self.log("-" * 80)
        
        if not results['open_ports']:
            self.log("    No open ports discovered in the requested range.")
        else:
            for port in results['open_ports']:
                banner_preview = port['banner'][:50] + "..." if len(port['banner']) > 50 else port['banner']
                self.log(f"{port['port']:<8} | {port['service']:<15} | {banner_preview}")

    def save_results(self):
        if not self.current_results or not self.scanner_instance:
            return
            
        export_format = self.export_var.get().lower()
        filename = f"scan_report.{export_format}"
        
        try:
            if export_format == "json":
                self.scanner_instance.export_json(self.current_results, filename)
            elif export_format == "csv":
                self.scanner_instance.export_csv(self.current_results, filename)
            elif export_format == "html":
                self.scanner_instance.export_html(self.current_results, filename)
                
            filepath = os.path.abspath(filename)
            messagebox.showinfo("Export Successful", f"{export_format.upper()} Report successfully saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save log: {str(e)}")

    def clear_fields(self):
        self.target_entry.delete(0, tk.END)
        self.results_area.delete(1.0, tk.END)
        self.current_results = None
        self.progress["value"] = 0
        self.save_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerGUI(root)
    root.mainloop()
