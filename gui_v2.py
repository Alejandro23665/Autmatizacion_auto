import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import os
import queue
import time

# Add src to path - works for both development and bundled (PyInstaller) modes
def get_base_path():
    """Get base path for both development and PyInstaller bundle"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running in development
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
SRC_PATH = os.path.join(BASE_PATH, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from automation.launch_app import launch_verification_station
from automation.queues import process_auto_queue_loop, find_queue_table, find_auto_row, get_cell_text


class AutoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ABBYY FlexiCapture - Auto Boletas")
        self.root.geometry("700x500")
        
        self.is_running = False
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.process_log_queue()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="ABBYY FlexiCapture - Automatización Boletas AUTO", 
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Estado", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Listo")
        self.status_label = ttk.Label(info_frame, textvariable=self.status_var, font=("Arial", 11))
        self.status_label.pack(anchor=tk.W)
        
        # Count display
        self.count_var = tk.StringVar(value=f"Boletas AUTO: --")
        self.count_label = ttk.Label(info_frame, textvariable=self.count_var, font=("Arial", 12, "bold"), foreground="blue")
        self.count_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = ttk.Button(btn_frame, text="Iniciar Automatización", command=self.start_automation, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(btn_frame, text="Detener", command=self.stop_automation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """Add message to log"""
        self.log_queue.put(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def process_log_queue(self):
        """Process log messages from queue"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)
        
    def start_automation(self):
        """Start automation in background thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start(10)
        self.status_var.set("Iniciando...")
        self.count_var.set("Boletas AUTO")
        self.log("Iniciando automatización...")
        
        self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
        self.automation_thread.start()
        
    def stop_automation(self):
        """Stop automation"""
        self.is_running = False
        self.log("Deteniendo automatización...")
        self.status_var.set("Detenido por usuario")
        
    def update_status(self, status):
        self.root.after(0, lambda: self.status_var.set(status))
        
    def update_count(self, count):
        self.root.after(0, lambda: self._set_count(count))
        
    def _set_count(self, count):
        """Internal method to set count and force UI update"""
        self.count_var.set(f"Boletas AUTO: {count}")
        # Force UI update
        self.count_label.update_idletasks()
        self.root.update_idletasks()
        
    def run_automation(self):
        """Run the automation workflow"""
        try:
            self.update_status("Lanzando ABBYY FlexiCapture...")
            self.log("Lanzando aplicación...")
            
            # Launch app and get main window
            app, main_window = launch_verification_station()
            
            if not self.is_running:
                return
                
            # Find queue table and auto row
            self.update_status("Buscando cola AUTO...")
            self.log("Buscando tabla de colas y fila AUTO...")
            
            from automation.queues import find_queue_table, find_auto_row, get_cell_text
            
            table = find_queue_table(main_window, timeout=15)
            if not table:
                self.log("ERROR: No se encontró tabla de colas")
                return
                
            auto_row = find_auto_row(table, timeout=10)
            if not auto_row:
                self.log("ERROR: No se encontró fila AUTO")
                return
                
            # Get count from column 3
            count_text = get_cell_text(auto_row, 3)
            self.update_status(f"Cantidad de AUTO detectada: {count_text}")
            
            try:
                count = int(count_text.strip())
                self.update_count(count)
                self.log(f"Cantidad de AUTO: {count}")
            except:
                self.log(f"Error parseando cantidad: {count_text}")
                self.update_count(0)
                
            if not self.is_running:
                return
                
            # Run the loop
            self.update_status("Procesando boletas...")
            self.log("Iniciando loop de procesamiento...")
            
            success, detected_count = process_auto_queue_loop(main_window, app, timeout=120)
            
            if success:
                self.update_count(detected_count)
                self.root.after(0, lambda: self.status_var.set("Completado exitosamente"))
                self.log("Automatización completada exitosamente")
            else:
                self.root.after(0, lambda: self.status_var.set("Error en automatización"))
                self.log("Error en automatización")
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"ERROR: {str(e)}"))
            import traceback
            traceback.print_exc()
        finally:
            self.root.after(0, self.automation_finished)
            
    def automation_finished(self):
        self.progress.stop()
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if self.is_running:
            self.status_var.set("Completado")
        else:
            # Keep the count visible, just update status
            current_count = self.count_var.get()
            if "Boletas AUTO: --" in current_count:
                self.status_var.set("Finalizado (sin datos de cantidad)")
            else:
                self.status_var.set(f"Finalizado - {current_count}")
        self.progress.stop()


def main():
    root = tk.Tk()
    root.title("ABBYY FlexiCapture - Auto Boletas")
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Accent.TButton", font=("Arial", 11, "bold"))
    
    app = AutoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()