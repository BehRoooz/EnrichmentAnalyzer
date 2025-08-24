#!/usr/bin/env python3
"""
Easy-to-use launcher for GO and pathway enrichment analysis
This script provides the simplest possible interface for running analyses
"""

import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def gui_mode():
    """Launch GUI for file selection and analysis"""

    class EnrichmentGUI:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("GO & Pathway Enrichment Analysis")
            self.root.geometry("600x500")

            # Variables
            self.input_path = tk.StringVar()
            self.output_path = tk.StringVar(value="enrichment_results")
            self.organism = tk.StringVar(value="human")
            self.analysis_type = tk.StringVar(value="single")
            self.gene_col = tk.StringVar(value="gene")
            self.reg_col = tk.StringVar(value="regulation")
            self.p_threshold = tk.DoubleVar(value=0.05)

            self.setup_gui()

        def setup_gui(self):
            # Ttile
            title_label = tk.Label(self.root, text="GO & Pathway Enrichment Analysis",
                                    font=("Arial", 16, "bold"))
            title_label.pack(pady=10)

            # Input selection frame
            input_frame = ttk.LabelFrame(self.root, text="Input Selection", padding=10)
            input_frame.pack(fill="x", padx=10, pady=5)

            # Analysis type
            ttk.Label(input_frame, text="Analysis Type:").grid(row=0, column=0, sticky="w", pady=2)
            analysis_combo = ttk.Combobox(input_frame, textvariable=self.analysis_type, 
                                        values=["single", "batch"], width=15)
            analysis_combo.grid(row=0, column=1,sticky="w", padx=5)

            # Input path
            ttk.Label(input_frame, text="Input File/Directory:").grid(row=1, column=0, sticky="w", pady=2)
            ttk.Entry(input_frame, textvariable=self.output_path, width=40).grid(row=2, column=1, sticky="w", padx=5)
            ttk.Button(input_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=5)

            # Parameters frame
            param_frame = ttk.LabelFrame(self.root, text="Analysis Parameters", padding=10)
            param_frame.pack(fill="x", padx=10, pady=5)

            # Organism
            ttk.Label(param_frame, text="Organism:").grid(row=0, column=0, sticky="w", pady=2)
            organism_combo = ttk.Combobox(param_frame, textvariable=self.organism, 
                                        values=["human", "zebrafish", "mouse", "rat"], width=15)
            organism_combo.grid(row=0, column=1, sticky="w", padx=5)

            # P-value threshold
            ttk.Label(param_frame, text="P-value Threshold:").grid(row=0, column=2, sticky="w", padx=20, pady=2)
            ttk.Entry(param_frame, textvariable=self.p_threshold, width=10).grid(row=0, column=3, sticky="w", padx=5)
            
            # Column names
            ttk.Label(param_frame, text="Gene Column:").grid(row=1, column=0, sticky="w", pady=2)
            ttk.Entry(param_frame, textvariable=self.gene_col, width=15).grid(row=1, column=1, sticky="w", padx=5)
            
            ttk.Label(param_frame, text="Regulation Column:").grid(row=1, column=2, sticky="w", padx=20, pady=2)
            ttk.Entry(param_frame, textvariable=self.reg_col, width=10).grid(row=1, column=3, sticky="w", padx=5)

            #Control buttons frame
            control_frame = tk.Frame(self.root)
            control_frame.pack(pady=20)

            # Buttons
            ttk.Button(control_frame,text="Create Template", 
                        command=self.create_template).pack(side="left", padx=5)
            ttk.Button(control_frame, text="Run Analysis",
                        command=self.run_analysis, style="Accent.TButton").pack(side="left", padx=5)
            ttk.Button(control_frame, text="Exit",
                        command=self.root.quit).pack(side="left", padx=5)
            
            # Progress frame
            progress_frame = tk.Frame(self.root)
            progress_frame.pack(fill="x", padx=10, pady=10)

            self.progress = ttk.Progressbar(progress_frame, mode="indeterminate")
            self.progress.pack(fill="x", pady=5)

            # Status text
            self.status_text = tk.Text(progress_frame, height=12, width=70)
            self.status_text.pack(fill="both", pady=5)

            # Scrollbar for status text
            scrollbar = ttk.Scrollbar(self.status_text)
            scrollbar.pack(side="right", fill="y")
            self.status_text.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.status_text.yview)

        def browse_input(self):
            if self.analysis_type.get() == "single":
                filename = filedialog.askopenfilename(
                    title="Select DEG XLSX file",
                    filetypes=[("Excel files", "*.xlsx"), ("Excel files start with DEG", "DEG*.xlsx"), ("All files", "*.*")]
                    )
                if filename:
                    self.input_path.set(filename)
            else:
                dirname = filedialog.askdirectory(title="Select directory containing DEG files")
                if dirname:
                    self.input_path.set(dirname)

        def browse_output(self):
            dirname = filedialog.askdirectory(title="Select output directory")
            if dirname:
                self.output_path.set(dirname)

        def create_template(self):
            try:
                from batch_processing import create_template_xlsx
                create_template_xlsx()
                self.log_message("Template file 'template_DEGs.xlsx' created successfully.")
                messagebox.showinfo("Success", "Template file created: template_DEGs.xlsx")
            except Exception as e:
                self.log_message(f"✗ Error creating template: {str(e)}")
                messagebox.showerror("Error", f"Failed to create template: {str(e)}")

        def run_analysis(self):
            if not self.input_path.get():
                messagebox.showwarning("Error", "Please select an input file or directory.")
                return
            
            # Start analysis in a separate thread to prevent GUI freezing
            thread = threading.Thread(target=self.run_analysis_thread)
            thread.daemon = True
            thread.start()

        def run_analysis_thread(self):
            try:
                self.progress.start()
                self.log_message("Starting analysis...")

                # Import here to avoid GUI startup delay
                from enrichment_pipeline import EnrichmentAnalyzer

                # Initialize analyzer
                analyzer = EnrichmentAnalyzer(
                    organism=self.organism.get(),
                    output_dir=self.output_path.get()
                )

                if self.analysis_type.get() == "single":
                    # Single file analysis
                    input_file = Path(self.input_path.get())
                    sample_name = input_file.stem


                    self.log_message(f"Analyzing: {input_file}")

                    result = analyzer.analyze_sample(
                        str(input_file),
                        sample_name,
                        gene_col=self.gene_col.get(),
                        regulation_col= self.reg_col.get(),
                        p_threshold=self.p_threshold.get()
                    )

                    if result['status'] == 'success':
                        self.log_message(f"✓ Analysis completed successfully!")
                        self.log_message(f"  - Upregulated genes: {result['up_genes_count']}")
                        self.log_message(f"  - Downregulated genes: {result['down_genes_count']}")
                        self.log_message(f"  - Results saved to: {self.output_path.get()}")
                    else:
                        self.log_message(f"✗ Analysis failed: {result.get('error', 'Unknown error')}")

                else:
                    # Batch analysis
                    self.log_message(f"Running batch analysis on: {self.input_path.get()}")

                    summary = analyzer.batchanalyze(
                        input_dir=self.input_path.get(),
                        gene_col=self.gene_col.get(),
                        regulation_col=self.reg_col.get(),
                        p_threshold=self.p_threshold.get()
                    )

                    successful = len([r for _, r in summary.iterrows() if r['status'] == 'success'])
                    total = len(summary)

                    self.log_message(f"✓ Batch analysis completed!")
                    self.log_message(f"  - Successful: {successful}/{total}")
                    self.log_message(f"  - Results saved to: {self.output_path.get()}")
                    
                    # Show summary
                    for _, row in summary.iterrows():
                        if row['status'] == 'success':
                            self.log_message(f"  ✓ {row['sample_name']}: "
                                            f"{row['up_genes_count']} up, {row['down_genes_count']} down")
                        else:
                            self.log_message(f"  ✗ {row['sample_name']}: {row.get('error', 'Failed')}")
                
                self.log_message("\n" + "="*50)
                self.log_message("ANALYSIS COMPLETE!")
                self.log_message("="*50)
                
            except Exception as e:
                self.log_message(f"✗ Error during analysis: {str(e)}")
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            finally:
                self.progress.stop()

        def log_message(self, message):
            """Add message to status text widget"""
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END)
            self.root.update_idletasks()

        def run(self):
            self.root.mainloop()

    # Run GUI
    app = EnrichmentGUI()
    app.run()

def command_line_wizard():
    """Interactive command line wizard for analysis setup."""
    
    print("=" * 60)
    print("    GO & PATHWAY ENRICHMENT ANALYSIS WIZARD")
    print("=" * 60)
    print()

    # Analysis type
    print("1. Analysis Type:")
    print("   a) Single file analysis")
    print("   b) Batch analysis (multiple files in nested folders)")
    choice = input("Choose (a/b): ").lower().strip()

    is_batch = choice == 'b'

    # Input selection
    print("\n2. Input Selection:")
    if is_batch:
        input_path = input("Enter parent directory path containing subfolders with DEG files: ").strip()
        if not os.path.isdir(input_path):
            print("ERROR: Directory not found!")
            print("\nExpected structure:")
            print("your_directory/")
            print("├── condition1/")
            print("│   └── DEGs_condition1_vs_control.xlsx")
            print("├── condition2/")
            print("│   └── DEGs_condition2_results.xlsx")
            print("└── treatment_A/")
            print("    └── DEGs_treatment_A.xlsx")
            return
    else:
        input_path = input("Enter XLSX file path (should start with 'DEGs'): ").strip()
        if not os.path.isfile(input_path):
            print("ERROR: File not found!")
            return
        if not os.path.basename(input_path).startswith('DEGs'):
            print("WARNING: File doesn't start with 'DEGs' - proceeding anyway...")
    
    # Output directory
    print("\n3. Output Settings:")
    output_dir = input("Output directory [enrichment_results]: ").strip()
    if not output_dir:
        output_dir = "enrichment_results"

    # Organism
    print("\n4. Organism:")
    print("   1) Human")
    print("   2) Zebrafish") 
    print("   3) Mouse")
    print("   4) Other")
    org_choice = input("Choose (1-4): ").strip()
    
    organisms = {"1": "Human", "2": "Zebrafish", "3": "Mouse", "4": "Other"}
    organism = organisms.get(org_choice, "Human")
    
    if organism == "Other":
        organism = input("Enter organism name: ").strip()

    # Advanced settings
    print("\n5. Advanced Settings (press Enter for defaults):")
    gene_col = input("Gene column name [gene]: ").strip() or "gene"
    reg_col = input("Regulation column name [regulation]: ").strip() or "regulation"
    p_thresh = input("P-value threshold [0.05]: ").strip()
    
    try:
        p_thresh = float(p_thresh) if p_thresh else 0.05
    except ValueError:
        p_thresh = 0.05

    # Confirmation
    print("\n" + "=" * 40)
    print("ANALYSIS CONFIGURATION:")
    print("=" * 40)
    print(f"Type: {'Batch (nested folders)' if is_batch else 'Single file'}")
    print(f"Input: {input_path}")
    if is_batch:
        print("Pattern: DEGs*.xlsx (recursive search)")
    print(f"Output: {output_dir}")
    print(f"Organism: {organism}")
    print(f"Gene column: {gene_col}")
    print(f"Regulation column: {reg_col}")
    print(f"P-value threshold: {p_thresh}")
    print("=" * 40)
    
    confirm = input("\nProceed with analysis? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Analysis cancelled.")
        return
    
    # Run analysis
    print("\nStarting analysis...")
    try:
        from enrichment_pipeline import EnrichmentAnalyzer
        
        analyzer = EnrichmentAnalyzer(organism=organism, output_dir=output_dir)
        
        if is_batch:
            summary = analyzer.batch_analyze(
                input_dir=input_path,
                pattern="DEGs*.xlsx",  # Specific pattern for DEG files
                gene_col=gene_col,
                regulation_col=reg_col,
                p_threshold=p_thresh,
                recursive=True  # Search in subdirectories
            )

            print(f"\nBatch analysis completed!")
            successful = len([r for _, r in summary.iterrows() if r['status'] == 'success'])
            total = len(summary)
            print(f"Results summary: {successful}/{total} successful")

            # Show results by folder
            if successful > 0:
                print(f"\n📊 Results by folder:")
                success_by_folder = summary[summary['status'] == 'success'].groupby('folder')
                for folder_name, group in success_by_folder:
                    print(f"  📁 {folder_name}: {len(group)} successful analyses")
                    for _, row in group.iterrows():
                        print(f"    ✓ {row['sample_name']}: {row['up_genes_count']} up, {row['down_genes_count']} down")

        else:
            sample_name = Path(input_path).stem.replace('DEGs_', '').replace('DEGs', '').strip('_')
            if not sample_name:
                sample_name = Path(input_path).stem

            result = analyzer.analyze_sample(
                input_path, sample_name,
                gene_col=gene_col,
                regulation_col=reg_col,
                p_threshold=p_thresh
            )

            if result['status'] == 'success':
                print(f"\nAnalysis completed successfully!")
                print(f"Sample: {sample_name}")
                print(f"Upregulated genes: {result['up_genes_count']}")
                print(f"Downregulated genes: {result['down_genes_count']}")
            else:
                print(f"Analysis failed: {result.get('error', 'Unknown error')}")
        
        print(f"\nResults saved to: {output_dir}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure files start with 'DEGs'")
        print("2. Check that column names match your data")
        print("3. Verify internet connection for enrichment APIs")

def main():
    """Main launcher function."""

    if len(sys.argv) == 1:
        # No arguments - show menu
        print("GO & Pathway Enrichment Analysis Launcher")
        print("=" * 40)
        print("1. Launch GUI (recommended)")
        print("2. Command line wizard")
        print("3. Quick analysis (drag & drop XLSX file)")
        print("4. Show help")
        print()
        
        choice = input("Choose option (1-4): ").strip()

        if choice == "1":
            try:
                gui_mode()
            except ImportError:
                print("GUI not available (tkinter not installed)")
                print("Using command line wizard instead...")
                command_line_wizard()
        elif choice == "2":
            command_line_wizard()
        elif choice == "3":
            file_path = input("Enter path to XLSX file: ").strip()
            if os.path.isfile(file_path):
                from batch_script import quick_analysis
                quick_analysis(file_path)
            else:
                print("File not found!")
        elif choice == "4":
            print_help()
        else:
            print("Invalid choice!")

    elif len(sys.argv) == 2:
        # Single argument - assume it's a file path for quick analysis
        file_path = sys.argv[1]
        if os.path.isfile(file_path) and file_path.endswith('.xlsx'):
            print(f"Quick analysis of: {file_path}")
            from batch_script import quick_analysis
            quick_analysis(file_path)
        else:
            print(f"Error: {file_path} is not a valid XLSX file")
    
    else:
        print_help()

def print_help():
    """Print help information."""
    help_text = """
GO & Pathway Enrichment Analysis - Help

USAGE:
    python launcher.py                    # Interactive menu
    python launcher.py file.xlsx          # Quick analysis of single file

FEATURES:
    - GUI interface for easy file selection
    - Batch processing of multiple files
    - Support for Human, Zebrafish, Mouse, and other organisms
    - GO terms and pathway enrichment
    - Automatic visualization generation
    - Comprehensive result summaries

SUPPORTED INPUT FORMAT:
    XLSX files with columns:
    - gene: Gene symbols
    - regulation: "Upregulated" or "Downregulated"
    - Other columns are optional

OUTPUT:
    - Excel files with enrichment results
    - PNG plots comparing up/down regulation
    - Summary reports

For more detailed usage, see the documentation or use the GUI interface.
    """
    print(help_text)

if __name__ == "__main__":
    main()