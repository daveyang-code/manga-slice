import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import cv2

class MangaPanelExtractor:
    def __init__(self, master):
        self.master = master
        master.title("Manga Panel Extractor")
        master.geometry("1200x800")

        # Folder selection
        self.input_folder = None
        self.extracted_panels = []

        # Folder selection
        self.select_folder_button = tk.Button(master, text="Select Manga Folder", command=self.select_folder)
        self.select_folder_button.pack(pady=10)

        # Scrollable frame for extracted panels
        self.canvas = tk.Canvas(master)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Control buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        self.export_button = tk.Button(self.button_frame, text="Export Selected Panels", command=self.export_panels)
        self.export_button.pack(side="right", padx=10)

    def select_folder(self):
        # Select folder
        self.input_folder = filedialog.askdirectory()
        if not self.input_folder:
            return

        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.extracted_panels.clear()

        # Sort and load image files
        image_files = sorted([
            f for f in os.listdir(self.input_folder) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ])

        # Process all images in the folder in order
        total_panels = 0
        for filename in image_files:
            img_path = os.path.join(self.input_folder, filename)
            try:
                panels = self.extract_panels(img_path)
                
                # Add panels to extracted panels in order
                for panel in panels:
                    self.add_panel_to_gui(panel)
                    total_panels += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

        # Show summary
        messagebox.showinfo("Processing Complete", f"Extracted {total_panels} panels from {len(image_files)} pages")

    def extract_panels(self, image_path):
        # Read image with OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Dilate to connect components
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=5)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area to exclude small noise
        min_area = img.shape[0] * img.shape[1] * 0.01  # Minimum 1% of image area
        
        # Collect valid panels with their positions
        valid_panels = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area > min_area:
                panel = img[y:y+h, x:x+w]
                valid_panels.append((panel, y))
        
        # Sort panels by y-coordinate (top to bottom)
        valid_panels.sort(key=lambda x: x[1])
        
        # Return only the panels, discarding the y-coordinates
        return [panel for panel, _ in valid_panels]

    def add_panel_to_gui(self, panel):
        # Convert OpenCV image (BGR) to PIL Image (RGB)
        panel_rgb = cv2.cvtColor(panel, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(panel_rgb)
        
        # Resize panel for display
        pil_img.thumbnail((800, 300))  # Limit height while maintaining aspect ratio
        photo = ImageTk.PhotoImage(pil_img)

        # Create a frame for each panel with a checkbox
        panel_frame = tk.Frame(self.scrollable_frame)
        panel_frame.pack(fill='x', padx=10, pady=5)

        var = tk.BooleanVar(value=True)
        checkbox = tk.Checkbutton(panel_frame, variable=var)
        checkbox.pack(side='left')

        label = tk.Label(panel_frame, image=photo)
        label.image = photo  # Keep a reference
        label.pack(side='left', expand=True)

        # Store panel with its selection state
        self.extracted_panels.append({
            'image': panel_rgb,  # Store RGB numpy array
            'checkbox': var
        })

    def export_panels(self):
        # Ask user for export location
        export_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        
        if not export_path:
            return

        # Collect selected panels
        selected_panels = [
            panel['image'] for panel in self.extracted_panels 
            if panel['checkbox'].get()
        ]

        if not selected_panels:
            messagebox.showerror("Error", "No panels selected for export")
            return

        # Resize panels to consistent width while maintaining aspect ratio
        w_min = min(img.shape[1] for img in selected_panels)
        resized_panels = [
            cv2.resize(
                img, 
                (w_min, int(img.shape[0] * w_min / img.shape[1])), 
                interpolation=cv2.INTER_AREA
            ) for img in selected_panels
        ]

        # Concatenate panels vertically
        result_image = cv2.vconcat(resized_panels)

        # Save the result
        cv2.imwrite(export_path, result_image)
        messagebox.showinfo("Success", f"Panels exported to {export_path}")

def main():
    root = tk.Tk()
    app = MangaPanelExtractor(root)
    root.mainloop()

if __name__ == "__main__":
    main()