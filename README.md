# GO and Pathway Enrichment Analysis Pipeline

A reproducible pipeline for performing Gene Ontology (GO) and pathway enrichment analysis on differentially expressed genes (DEGs) from XLSX files.

## Features

- **Batch Processing**: Analyze multiple DEG files at once
- **Multiple Organisms**: Support for Zebrafish, Human, and other organisms
- **Comprehensive Analysis**: GO terms (BP, MF, CC) and pathways (WikiPathways, KEGG)
- **Automated Visualization**: Generate comparison plots automatically
- **Flexible Input**: Works with any XLSX format with customizable column names
- **Summary Reports**: Detailed summaries of all analyses
- **Error Handling**: Robust error handling and logging

## Installation

### Requirements

```bash
# Install required packages
pip install numpy pandas matplotlib seaborn gseapy gprofiler-official openpyxl pathlib
```

### Full requirements.txt
```
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
gseapy>=1.0.0
gprofiler-official>=1.0.0
openpyxl>=3.0.0
pathlib>=1.0.0
pyyaml>=5.4.0
```

## Quick Start

### 1. Analyze a Single File
```bash
# Basic analysis
python batch_script.py quick my_degs.xlsx

# With custom sample name and output directory
python batch_script.py quick my_degs.xlsx --name "Treatment_vs_Control" --output "my_results"
```

### 2. Batch Analysis of Multiple Files
```bash
# Analyze all XLSX files in a directory
python batch_script.py batch /path/to/deg_files/ --output "batch_results"
```

### 3. Using the Main Pipeline Script
```bash
# Single file with custom parameters
python enrichment_pipeline.py --input "DEGs.xlsx" --organism "Zebrafish" --p-threshold 0.01

# Batch analysis
python enrichment_pipeline.py --input "deg_directory/" --batch --output "results"
```

## Input File Format

Your XLSX files should contain the following columns (customizable):

| gene | p_val | avg_log2FC | pct.1 | pct.2 | p_val_adj | regulation |
|------|-------|------------|-------|-------|-----------|--------------|
| gene1 | 0.001 | 2.5 | 0.8 | 0.1 | 0.01 | Upregulated |
| gene2 | 0.01 | -1.8 | 0.3 | 0.7 | 0.05 | Downregulated |

### Required Columns:
- **gene**: Gene symbols
- **regulation**: Must contain "Upregulated" and "Downregulated" values

### Create Template File:
```bash
python batch_script.py template
```

## Usage Examples

### Example 1: Basic Single File Analysis
```python
from enrichment_pipeline import EnrichmentAnalyzer

# Initialize analyzer
analyzer = EnrichmentAnalyzer(organism='Zebrafish', output_dir='results')

# Analyze single sample
result = analyzer.analyze_sample('DEGs_hypoxia_vs_control.xlsx', 'hypoxia_treatment')
print(f"Found {result['up_genes_count']} upregulated and {result['down_genes_count']} downregulated genes")
```

### Example 2: Batch Analysis with Custom Settings
```python
from enrichment_pipeline import EnrichmentAnalyzer

analyzer = EnrichmentAnalyzer(organism='Human', output_dir='human_analysis')

# Batch analyze all files in directory
summary = analyzer.batch_analyze(
    input_dir='deg_files/',
    pattern='*_DEGs.xlsx',
    gene_col='GeneName',
    regulation_col='Direction',
    p_threshold=0.01
)

print("Analysis Summary:")
print(summary[['sample_name', 'status', 'up_genes_count', 'down_genes_count']])
```

### Example 3: Custom Column Names
```bash
python enrichment_pipeline.py \
    --input "my_data.xlsx" \
    --gene-col "GeneName" \
    --regulation-col "Direction" \
    --organism "Human" \
    --p-threshold 0.01
```

## Output Structure

```
results/
├── plots/                          # Comparison plots
│   ├── sample1_GO_biological_process_significant.png
│   ├── sample1_kegg_pathways_significant.png
│   └── ...
├── go_results/                     # GO enrichment Excel files
│   ├── sample1_up_GO_Biological_Process.xlsx
│   ├── sample1_down_GO_Molecular_Function.xlsx
│   └── ...
├── pathway_results/                # Pathway enrichment Excel files
│   ├── sample1_up_WikiPathways.xlsx
│   ├── sample1_down_KEGG.xlsx
│   └── ...
├── summary/                        # Analysis summaries
│   └── batch_analysis_summary.xlsx
└── enrichment_analysis.log         # Detailed log file
```

## Supported Organisms

- **Zebrafish** (`drerio`)
- **Human** (`hsapiens`)
- **Mouse** (`mmusculus`)
- **Rat** (`rnorvegicus`)
- And many others supported by GSEApy and g:Profiler

## Troubleshooting

### Common Issues

1. **"No significant terms found"**
   - Try lowering the p-value threshold: `--p-threshold 0.1`
   - Check if gene symbols are correctly formatted
   - Ensure adequate number of DEGs (>10 recommended)

2. **"Empty gene list"**
   - Verify column names match your data
   - Check significance categories ("Upregulated"/"Downregulated")

3. **Network/API errors**
   - Check internet connection
   - Try running analysis again (temporary API issues)

### Debug Mode
```bash
# Enable detailed logging
python enrichment_pipeline.py --input "file.xlsx" --verbose
```

## Advanced Features

### Custom Analysis Parameters
```python
# Initialize with custom settings
analyzer = EnrichmentAnalyzer(
    organism='Human',
    output_dir='custom_results'
)

# Override default libraries
analyzer.libraries = {
    'go': ['GO_Biological_Process_2021'],
    'pathways': ['KEGG_2021_Human', 'Reactome_2022']
}
```

### Integration with Other Tools
```python
# Load results for further analysis
import pandas as pd

# Load GO results
go_results = pd.read_excel('results/go_results/sample_up_GO_Biological_Process.xlsx')
significant_go = go_results[go_results['Adjusted P-value'] < 0.05]

# Custom visualization
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.barh(significant_go['Term'][:10], -np.log10(significant_go['Adjusted P-value'][:10]))
plt.xlabel('-log10(Adjusted P-value)')
plt.title('Top 10 GO Terms')
plt.tight_layout()
plt.show()
```

## Citation

If you use this pipeline in your research, please cite the underlying tools:

- **GSEApy**: Fang et al. (2023). GSEApy: a comprehensive package for performing gene set enrichment analysis in Python.
- **g:Profiler**: Raudvere et al. (2019). g:Profiler: a web server for functional enrichment analysis.

## License

This pipeline is provided under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the log files for detailed error messages
3. Ensure your input data matches the expected format
