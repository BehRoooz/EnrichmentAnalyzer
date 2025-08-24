#!usr/bin/env python3

"""
Simplified batch processing script for multiple DEG analyses
This script provides an even easier interface for running analyses on multiple files
"""

import os
import pandas as pd
from pathlib import Path
import argparse
from enrichment_pipeline import EnrichmentAnalyzer

def process_directory_structure(base_dir: str, output_dir: str = 'enrichment_results'):
    """
    Process a directory structure containing multiple DEG files.
    Expected structure:
    base_dir/
    ├── condition1/
    │   └── DEGs_condition1_vs_control.xlsx
    ├── condition2/
    │   └── DEGs_condition2_vs_control.xlsx
    └── ...
    """

    base_path = Path(base_dir)
    output_path = Path(output_dir)

    # Initialize analyzer
    analyzer = EnrichmentAnalyzer(output_dir = str(output_path))

    # Find all XLSX files
    xlsx_files = list(base_path.rglob("*.xlsx"))

    if not xlsx_files:
        print(f"No XLSX files found in {base_dir}")
        return
    
    print(f"Found {len(xlsx_files)} XLSX files to process.")

    # Process each file
    results_summary = []

    for xlsx_file in xlsx_files:
        # Create meaningful sample name from path
        relative_path = xlsx_file.relative_to(base_path)
        sample_name = str(relative_path.with_suffix('')).replace('/', '_')

        print(f"\nProcessing: {xlsx_file}")
        print(f"Sample name: {sample_name}")

        try:
            result = analyzer.analyze_sample(str(xlsx_file), sample_name)
            results_summary.append(result)
            print(f"✓ Completed: {sample_name}")
        except Exception as e:
            print(f"✗ Failed: {sample_name} - {str(e)}")
            results_summary.append({
                'sample_name': sample_name,
                'status': 'failed',
                'error': str(e)
            })

    # Save summary
    summary_df = pd.DataFrame(results_summary)
    summary_path = output_path / "batch_summary.xlsx"
    summary_df.to_excel(summary_path, index=False)

    print(f"\n" + "="*50)
    print("BATCH PROCESSING COMPLETED")
    print(f"Results saved to {output_path}")
    print(f"Summary saved to {summary_path}")
    print("="*50)

    # Print summary statistics
    successful = len([r for r in results_summary if r['status'] == 'success'])
    failed = len(results_summary) - successful

    print(f"Successful analyses: {successful}")
    print(f"Failed analyses: {failed}")

    if successful > 0:
        print(f"\nSuccessful samples:")
        for result in results_summary:
            if result['status'] == 'success':
                print(f"   - {result['sample_name']}: "
                      f"{result['up_genes_count']} up, "
                      f"{result['down_genes_count']} down")
                
    return summary_df

def quick_analysis(xlsx_file: str, sample_name: str = None, output_dir: str = "quick_results"):
    """
    Quick analysis of a single file with sensible defaults.
    """

    if sample_name is None:
        sample_name = Path(xlsx_file).stem

    print(f"Running quick analysis on: {xlsx_file}")
    print(f"Sample name: {sample_name}")
    print(f"Output directory: {output_dir}")

    analyzer = EnrichmentAnalyzer(output_dir=output_dir)
    result = analyzer.analyze_sample(xlsx_file, sample_name)

    if result['status'] == 'success':
        print(f"\n✓ Analysis completed successfully!")
        print(f"Upregulated genes: {result['up_genes_count']}")
        print(f"Downregulated genes: {result['down_genes_count']}")
        
        # Print significant results count
        for key, value in result.items():
            if 'significant' in key and isinstance(value, int):
                print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        print(f"✗ Analysis failed: {result.get('error', 'Unknown error')}")

    return result

def create_template_xlsx():
    """Create a template XLSX file showing the expected format."""
    template_data = {
        'gene': ['gene1', 'gene2', 'gene3', 'gene4', 'gene5'],
        'p_val': [0.001, 0.01, 0.005, 0.0001, 0.02],
        'avg_log2FC': [2.5, -1.8, 3.2, -2.1, 1.5],
        'pct.1': [0.8, 0.3, 0.9, 0.2, 0.7],
        'pct.2': [0.1, 0.7, 0.1, 0.8, 0.2],
        'p_val_adj': [0.01, 0.05, 0.03, 0.001, 0.08],
        'regulation': ['Upregulated', 'Downregulated', 'Upregulated', 
                        'Downregulated', 'Upregulated']
    }
    
    template_df = pd.DataFrame(template_data)
    template_df.to_excel('template_DEGs.xlsx', index=False)
    
    print("Template file created: template_DEGs.xlsx")
    print("This shows the expected format for your DEG files.")
    
    return template_df

def main():
    parser = argparse.ArgumentParser(
        description="Simplified batch processing for DEG enrichment analysis."
    )

    subparsers = parser.add_subparsers(dest='command', help = 'Available commands')

    # Quick analysis command
    quick_parser = subparsers.add_parser('quick', help='Quick analysis of single file')
    quick_parser.add_argument('file', help='XLSX file to analyze')
    quick_parser.add_argument('--name', help='Sample name (default: filename)')
    quick_parser.add_argument('--output', '-o', default='quick_results', help='Output directory')

    # Batch analysis command
    # Batch analysis command
    batch_parser = subparsers.add_parser('batch', help='Batch analysis of directory')
    batch_parser.add_argument('directory', help='Directory containing XLSX files')
    batch_parser.add_argument('--output', '-o', default='batch_results', help='Output directory')

    # Template creation command
    template_parser = subparsers.add_parser('template', help='Create template XLSX file')

    args = parser.parse_args()

    if args.command == 'quick':
        quick_analysis(args.file, args.name, args.output)

    elif args.command == 'batch':
        process_directory_structure(args.directory, args.output)

    elif args.command == 'template':
        create_template_xlsx()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()