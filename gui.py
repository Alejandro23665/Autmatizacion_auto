import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from automation.launch_app import launch_verification_station


class AutoGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatizacion Autos")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Variables
        self.auto_count = 0
        self.is_running = False
        self.automation_thread = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Automatizacion Autos", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Estado", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Status label
        self.status_var = tk.StringVar(value="Listo para iniciar")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        # Count label
        self.count_var = tk.StringVar(value="")
        self.count_label = ttk.Label(status_frame, textvariable=self.count_var, font=("Arial", 14, "bold"), foreground="blue")
        self.count_label.pack(pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Iniciar Envio", command=self.start_automation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10), ipadx=20, ipady=5)
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Detener", command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, ipadx=20, ipady=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def start_automation(self):
        """Start automation in background thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress.start(10)
        self.status_var.set("Iniciando...")
        self.count_var.set("")
        self.log("Iniciando automatizacion...")
        
        self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
        
    def stop_automation(self):
        """Stop automation"""
        self.is_running = False
        self.progress.stop()
        self.status_var.set("Detenido por usuario")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("Automatizacion detenida por usuario")
        
    def run_automation(self):
        """Run the automation in background thread"""
        try:
            # Import here to avoid circular imports
            from automation.launch_app import launch_verification_station
            
            self.root.after(0, lambda: self.status_var.set("Iniciando ABBYY FlexiCapture..."))
            self.root.after(0, lambda: self.log("Lanzando aplicacion..."))
            
            # We need to patch the launch function to capture the count
            # For now, run the original function
            app, main_window = launch_verification_station()
            
            if not self.is_running:
                self.root.after(0, self.automation_finished)
                return
                
            # The count is detected inside the automation
            # We'll need to get it from the queues module
            from automation.queues import select_auto_queue_and_open_boleta
            
            # The count is printed in the console, we can't easily capture it
            # For now, show a message
            self.root.after(0, lambda: self.status_var.set("Procesando boletas..."))
            self.root.after(0, lambda: self.log("Automatizacion en ejecucion..."))
            
            # Wait for thread to finish or stop
            while self.is_running and self.automation_thread.is_alive():
                import time
                time.sleep(1)
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Error: {str(e)}"))
        finally:
            self.root.after(0, self.automation_finished)
            
    def automation_finished(self):
        """Called when automation finishes"""
        self.progress.stop()
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Completado")
        self.progress.stop()
        self.log("Automatizacion finalizada")


def main():
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure accent button style
    style.configure("Accent.TButton", font=("Arial", 11, "bold"))
    
    app = AutoGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()