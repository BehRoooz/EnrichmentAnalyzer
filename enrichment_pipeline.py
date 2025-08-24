#!/usr/bin/env python3

'''
Reproducible GO and Pathway Enrichment Analysis Pipeline
Author: Behrouz Mirabdi
GitHub: https://github.com/BehRoooz
Date: August 2025

This script performs comprehensive GO and pathway enrichment analysis
for multiple DEG datasets in XLSX format.
'''

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gseapy as gp
from gprofiler import GProfiler
from pathlib import Path
import argparse
import logging
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enrichment_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnrichmentAnalyzer:
    """
    A comprehensive class for performing Gene Onthology (GO) and pathway enrichment analysis
    on differentially expressed genes
    """

    def __init__(self, organism: str = 'human', output_dir: str = 'results'):
        """
        
        
        Initialize the EnrichmentAnalyzer. 

        Args:
            organism: Target organism for analysis (e.g. human, zebrafish, etc. default: human)
            output_dir: Base directory for saving results
        """
        self.organism = organism
        self.output_dir = Path(output_dir)
        self.gprofiler = GProfiler(return_dataframe=True)

        # Create output directory structure
        self.setup_directories()

        # Define analysis libraries for different organisms
        self.libraries = self._get_libraries()

    def setup_directories(self):
        """Create necessary directory structure for outputs."""
        dirs = ['plots', 'go_results', 'pathway_results', 'summary']
        for dir_names in dirs:
            (self.output_dir / dir_names).mkdir(parents=True, exist_ok=True)

    def _get_libraries(self) -> Dict[str, List[str]]:
        """Get appropriate libraries based on organism."""
        if self.organism.lower() == 'zebrafish':
            return{
                'go' : ['GO_Biological_Process_2018', 'GO_Molecular_Function_2018', 'GO_Cellular_Component_2018'],
                'pathways' : ['WikiPathways_2018', 'KEGG_2019']
            }
        
        elif self.organism.lower() == 'human':
            return{
                'go': ['GO_Biological_Process_2021', 'GO_Molecular_Function_2021', 'GO_Cellular_Component_2021'],
                'pathways': ['WikiPathways_2019_Human', 'KEGG_2021_Human']
            }
        
        else:
            # Default libraries
            return{
                'go': ['GO_Biological_Process_2018', 'GO_Molecular_Function_2018', 'GO_Cellular_Component_2018'],
                'pathways': ['WikiPathways_2018', 'KEGG_2019']
            }
        
    def load_degs(self, file_path: str, gene_col: str = 'gene',
                regulation_col: str = 'regulation') -> Tuple[List[str], List[str]]:
        """
        Load DEGs from XLSX file and separate into up/down regulated.
            
        Args:
            file_path: Path to XLSX file containing DEGs
            gene_col: Column name containing gene symbols
            regulation_col: Column name containing regulation direction

        Returns:
            Tuple of (upregulated_genes, downregulated_genes)
        """

        try: 
            df = pd.read_excel(file_path)
            logger.info(f"Loaded {len(df)} DEGs from {file_path}")

            # Check if required columns exist
            if regulation_col not in df.columns:
                df[regulation_col] = np.where(df['log2FoldChange'] > 0, 'Upregulated', 'Downregulated')

            # Extract upregulated and downregulated genes 
            up_genes = df[df[regulation_col] == 'Upregulated'][gene_col].tolist()
            down_genes = df[df[regulation_col] == 'Downregulated'][gene_col].tolist()

            logger.info(f"Found {len(up_genes)} upregulated and {len(down_genes)} down regulated genes.")
            return up_genes, down_genes
            
        except Exception as e:
            logger.error(f"Error loading DEGs from {file_path}: {str(e)}")
            raise
            
    def run_enrichment(self, gene_list: List[str], gene_set: List[str],
                    analysis_name: str) -> Optional[object]:
        """
        run enrichment analysis using GSEApy.
            
        Args:
            gene_list: List of genes to analyze
            gene_set: List of gene set libraries to use
            analysis_name: Name for the analysis (for logging)

        Returns:
            GSEApy enrichment results object
        """

        if not gene_list:
            logger.warning(f"Empty gene list for {analysis_name}")
            return None
                
        try:
            logger.info(f"Running {analysis_name} with {len(gene_list)} genes.")
            enr_result = gp.enrichr(
                gene_list=gene_list,
                gene_sets=gene_set,
                organism=self.organism
            )
            return enr_result
            
        except Exception as e:
            logger.error(f"Error running {analysis_name}: {str(e)}")
            return None 

    def filter_significant(self, results_df: pd.DataFrame, 
                        p_threshold: float = 0.05) -> pd.DataFrame:
        """
        filter results for significant terms.
        """
        if results_df is None or results_df.empty:
            return pd.DataFrame()
        else:
            filtered_results_df = results_df[results_df['Adjusted P-value'] < p_threshold]
        return filtered_results_df
        
    def save_results(self, results: object, filename: str, subdir: str = ''):
        """Save enrichment results to excel file. """
        if results is None:
            logger.warning(f"No results to save for {filename}")
            return
            
        output_path = self.output_dir / subdir / f"{filename}.xlsx"
        try:
            results.results.to_excel(output_path, index=False)
            logger.info(f"Results saved to {output_path}")

        except Exception as e:
            logger.error(f"Error saving results to {output_path}: {str(e)}")
                

    def create_comparison_plot(self, up_results: pd.DataFrame, down_results: pd.DataFrame,
                            title: str, filename: str, top_n: int = 10):
        """
        Create comparison plot for up vs down regulated terms.
        
        Args:
            up_results: Upregulated enrichment results
            down_results: Downregulated enrichment results
            title: Plot title
            filename: Output filename
            top_n: Number of top terms to show
        """
        # Prepare data
        if not up_results.empty:
            up_plot_data = up_results.head(top_n).copy()
            up_plot_data['direction'] = 'Upregulated'
            up_plot_data['-log10(p-value)'] = -np.log10(up_plot_data['Adjusted P-value'])
        else:
            up_plot_data = pd.DataFrame()
                
        if not down_results.empty:
            down_plot_data = down_results.head(top_n).copy()
            down_plot_data['direction'] = 'Downregulated'
            down_plot_data['-log10(p-value)'] = np.log10(down_plot_data['Adjusted P-value'])
        else:
            down_plot_data = pd.DataFrame()
                
        # Combine data
        if up_plot_data.empty and down_plot_data.empty:
            logger.warning(f"No data to plot for {title}")
            return
                    
        combined_data = pd.concat([up_plot_data, down_plot_data], ignore_index=True)

        # Create plot
        plt.figure(figsize=(14, max(3, len(combined_data) * 0.4)))
                
        if not combined_data.empty:
            sns.barplot(data=combined_data, y='Term', x='-log10(p-value)', 
                        hue='direction', palette=['red', 'blue'])
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('-log10(Adjusted P-value)', fontsize=12)
            plt.ylabel('Terms', fontsize=12)
            plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            plt.legend(title='Direction', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            # Save plot
            plot_path = self.output_dir / 'plots' / f"{filename}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            logger.info(f"Plot saved to {plot_path}")
        else:
            plt.close()

    def analyze_sample(self, xlsx_path: str, sample_name: str, 
                    gene_col: str = 'gene', regulation_col: str = 'regulation',
                    p_threshold: float = 0.05) -> Dict:
        """
        Perform complete enrichment analysis for a single sample.
        
        Args:
            xlsx_path: Path to XLSX file with DEGs
            sample_name: Name for this sample (used in output files)
            gene_col: Column name with gene symbols
            regulation_col: Column name with regulation direction
            p_threshold: P-value threshold for significance
            
        Returns:
            Dictionary with analysis results summary
        """
        logger.info(f"Starting analysis for sample: {sample_name}")
                
        # Create sample-specific output directory
        sample_dir = self.output_dir / sample_name
        sample_dir.mkdir(exist_ok=True)
        
        # Load DEGs
        try:
            up_genes, down_genes = self.load_degs(xlsx_path, gene_col, regulation_col)
        except Exception as e:
            logger.error(f"Failed to load DEGs for {sample_name}: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
                
        results_summary = {
            'sample_name': sample_name,
            'up_genes_count': len(up_genes),
            'down_genes_count': len(down_genes),
            'status': 'success'
        }
                
        # GO Enrichment Analysis
        logger.info("Running GO enrichment analysis...")
        go_results = {}
                
        for go_type in ['Biological_Process', 'Molecular_Function', 'Cellular_Component']:
            library = f"GO_{go_type}_2018"
                    
            # Upregulated genes
            up_enr = self.run_enrichment(up_genes, [library], 
                                    f"GO {go_type} upregulated")
            if up_enr:
                self.save_results(up_enr, f"{sample_name}_up_GO_{go_type}", 'go_results')
                go_results[f'up_{go_type.lower()}'] = up_enr.results
            
            # Downregulated genes
            down_enr = self.run_enrichment(down_genes, [library], 
                                        f"GO {go_type} downregulated")
            if down_enr:
                self.save_results(down_enr, f"{sample_name}_down_GO_{go_type}", 'go_results')
                go_results[f'down_{go_type.lower()}'] = down_enr.results
                
        # Pathway Enrichment Analysis
        logger.info("Running pathway enrichment analysis...")
        pathway_results = {}
        
        for pathway_db in ['WikiPathways_2018', 'KEGG_2019']:
            db_name = pathway_db.split('_')[0]
                    
            # Upregulated genes
            up_enr = self.run_enrichment(up_genes, [pathway_db], 
                                    f"{db_name} upregulated")
            if up_enr:
                self.save_results(up_enr, f"{sample_name}_up_{db_name}", 'pathway_results')
                pathway_results[f'up_{db_name.lower()}'] = up_enr.results
            
            # Downregulated genes
            down_enr = self.run_enrichment(down_genes, [pathway_db], 
                                        f"{db_name} downregulated")
            if down_enr:
                self.save_results(down_enr, f"{sample_name}_down_{db_name}", 'pathway_results')
                pathway_results[f'down_{db_name.lower()}'] = down_enr.results
                
        # Create comparison plots
        logger.info("Creating comparison plots...")
        
        # GO plots
        for go_type in ['biological_process', 'molecular_function', 'cellular_component']:
            up_key = f'up_{go_type}'
            down_key = f'down_{go_type}'

            up_data = go_results.get(up_key, pd.DataFrame())
            down_data = go_results.get(down_key, pd.DataFrame())
            
            up_data_filtered = self.filter_significant(go_results.get(up_key, pd.DataFrame()), p_threshold)
            down_data_filtered = self.filter_significant(go_results.get(down_key, pd.DataFrame()), p_threshold)
            
            self.create_comparison_plot(
                up_data, down_data,
                f'{sample_name} - GO {go_type.replace("_", " ").title()}',
                f'{sample_name}_GO_{go_type}'
            )
            
            self.create_comparison_plot(
                up_data_filtered, down_data_filtered,
                f'{sample_name} - GO {go_type.replace("_", " ").title()} (Significant)',
                f'{sample_name}_GO_{go_type}_significant'
            )
            
            # Count significant terms
            results_summary[f'go_{go_type}_up_significant'] = len(up_data_filtered)
            results_summary[f'go_{go_type}_down_significant'] = len(down_data_filtered)
        
        # Pathway plots
        for db in ['wikipathways', 'kegg']:
            up_key = f'up_{db}'
            down_key = f'down_{db}'
            
            up_data = pathway_results.get(up_key, pd.DataFrame())
            down_data = pathway_results.get(down_key, pd.DataFrame())
            
            up_data_filtered = self.filter_significant(pathway_results.get(up_key, pd.DataFrame()), p_threshold)
            down_data_filtered = self.filter_significant(pathway_results.get(down_key, pd.DataFrame()), p_threshold)
            
            self.create_comparison_plot(
                up_data, down_data,
                f'{sample_name} - {db.upper()} Pathways',
                f'{sample_name}_{db}_pathways'
            )
            
            self.create_comparison_plot(
                up_data_filtered, down_data_filtered,
                f'{sample_name} - {db.upper()} Pathways (Significant)',
                f'{sample_name}_{db}_pathways_significant'
            )
            
            # Count significant terms
            results_summary[f'{db}_up_significant'] = len(up_data_filtered)
            results_summary[f'{db}_down_significant'] = len(down_data_filtered)
        
        logger.info(f"Analysis completed for sample: {sample_name}")
        return results_summary
    
    def batch_analyze(self, input_dir: str, pattern: str = "*.xlsx", 
                    gene_col: str = 'gene', regulation_col: str = 'regulation',
                    p_threshold: float = 0.05) -> pd.DataFrame:
        """
        Perform batch analysis on multiple XLSX files.
        
        Args:
            input_dir: Directory containing XLSX files
            pattern: File pattern to match (default: "*.xlsx")
            gene_col: Column name with gene symbols
            regulation_col: Column name with regulation direction
            p_threshold: P-value threshold for significance
            
        Returns:
            Summary DataFrame with results for all samples
        """
        input_path = Path(input_dir)
        xlsx_files = list(input_path.glob(pattern))
        
        if not xlsx_files:
            logger.error(f"No XLSX files found in {input_dir} with pattern {pattern}")
            return pd.DataFrame()
        
        logger.info(f"Found {len(xlsx_files)} files for batch analysis")
        
        all_results = []
        
        for xlsx_file in xlsx_files:
            sample_name = xlsx_file.stem  # Filename without extension
            logger.info(f"Processing file: {xlsx_file}")
            
            try:
                result = self.analyze_sample(
                    str(xlsx_file), sample_name, 
                    gene_col, regulation_col, p_threshold
                )
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {xlsx_file}: {str(e)}")
                all_results.append({
                    'sample_name': sample_name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(all_results)
        
        # Save summary
        summary_path = self.output_dir / 'summary' / 'batch_analysis_summary.xlsx'
        summary_df.to_excel(summary_path, index=False)
        logger.info(f"Batch analysis summary saved to {summary_path}")
        
        return summary_df
    

def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(
        description="Perform GO and pathway enrichment analysis on DEG datasets"
    )
    
    parser.add_argument(
        '--input', '-i', required=True,
        help='Input XLSX file or directory containing XLSX files'
    )
    
    parser.add_argument(
        '--output', '-o', default='enrichment_results',
        help='Output directory (default: enrichment_results)'
    )
    
    parser.add_argument(
        '--organism', default='human',
        help='Target organism (default: human)'
    )
    
    parser.add_argument(
        '--gene-col', default='gene',
        help='Column name containing gene symbols (default: gene)'
    )
    
    parser.add_argument(
        '--regulation-col', default='regulation',
        help='Column name containing regulation direction (default: regulation)'
    )
    
    parser.add_argument(
        '--p-threshold', type=float, default=0.05,
        help='P-value threshold for significance (default: 0.05)'
    )
    
    parser.add_argument(
        '--batch', action='store_true',
        help='Perform batch analysis on directory of XLSX files'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = EnrichmentAnalyzer(organism=args.organism, output_dir=args.output)
    
    if args.batch or Path(args.input).is_dir():
        # Batch analysis
        logger.info("Starting batch analysis...")
        summary = analyzer.batch_analyze(
            args.input, gene_col=args.gene_col, 
            regulation_col=args.regulation_col,
            p_threshold=args.p_threshold
        )
        print("\nBatch Analysis Summary:")
        print(summary.to_string(index=False))
        
    else:
        # Single file analysis
        input_path = Path(args.input)
        sample_name = input_path.stem
        
        logger.info("Starting single file analysis...")
        result = analyzer.analyze_sample(
            args.input, sample_name,
            gene_col=args.gene_col,
            regulation_col=args.regulation_col,
            p_threshold=args.p_threshold
        )
        
        print(f"\nAnalysis completed for {sample_name}")
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Upregulated genes: {result['up_genes_count']}")
            print(f"Downregulated genes: {result['down_genes_count']}")


if __name__ == "__main__":
    main()

