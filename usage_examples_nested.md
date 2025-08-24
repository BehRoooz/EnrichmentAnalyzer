# Usage Examples for Nested Directory Structure with DEG Files

## Your Directory Structure
```
your_project_folder/
├── hypoxia_treatment/
│   └── DEGs_hypoxia_vs_control.xlsx
├── heat_shock/
│   └── DEGs_heat_shock_results.xlsx
├── drug_treatment_A/
│   └── DEGs_drug_A_analysis.xlsx
├── drug_treatment_B/
│   └── DEGs_drug_B_comparison.xlsx
└── time_course/
    ├── DEGs_6h_vs_0h.xlsx
    └── DEGs_24h_vs_0h.xlsx
```

## Method 1: Super Easy GUI
```bash
python launcher.py
# Select option 1 (GUI)
# Choose "batch" analysis
# Browse to select your_project_folder/
# Click "Run Analysis"
```

## Method 2: Simple Command Line
```bash
# Quick batch analysis
python batch_script.py batch your_project_folder/ --output my_results

# The script will automatically:
# - Find all DEGs*.xlsx files in subfolders
# - Create sample names like: hypoxia_treatment_hypoxia_vs_control
# - Generate organized results
```

## Method 3: Advanced Command Line
```bash
# Full control with the main pipeline
python enrichment_pipeline.py \
    --input your_project_folder/ \
    --batch \
    --organism Zebrafish \
    --output comprehensive_results \
    --p-threshold 0.05
```

## Method 4: Interactive Wizard
```bash
python launcher.py
# Select option 2 (Command line wizard)
# Choose 'b' for batch analysis
# Enter: your_project_folder/
# Follow the prompts
```

## What Happens During Processing

### 1. File Discovery
The script searches for files matching `DEGs*.xlsx` pattern:
```
Searching for DEG files in: your_project_folder/
Looking for files matching pattern: DEGs*.xlsx

  Found 1 DEG file(s) in hypoxia_treatment/
    - DEGs_hypoxia_vs_control.xlsx
  Found 1 DEG file(s) in heat_shock/
    - DEGs_heat_shock_results.xlsx
  Found 1 DEG file(s) in drug_treatment_A/
    - DEGs_drug_A_analysis.xlsx
  Found 1 DEG file(s) in drug_treatment_B/
    - DEGs_drug_B_comparison.xlsx
  Found 2 DEG file(s) in time_course/
    - DEGs_6h_vs_0h.xlsx
    - DEGs_24h_vs_0h.xlsx

Total DEG files found: 6
```

### 2. Sample Naming
The script creates meaningful sample names:
- `hypoxia_treatment/DEGs_hypoxia_vs_control.xlsx` → `hypoxia_treatment_hypoxia_vs_control`
- `heat_shock/DEGs_heat_shock_results.xlsx` → `heat_shock_heat_shock_results`
- `drug_treatment_A/DEGs_drug_A_analysis.xlsx` → `drug_treatment_A_drug_A_analysis`
- `time_course/DEGs_6h_vs_0h.xlsx` → `time_course_6h_vs_0h`
- `time_course/DEGs_24h_vs_0h.xlsx` → `time_course_24h_vs_0h`

### 3. Analysis Progress
```
[1/6] Processing: hypoxia_treatment/DEGs_hypoxia_vs_control.xlsx
Sample name: hypoxia_treatment_hypoxia_vs_control
✓ Completed: 45 up, 67 down genes

[2/6] Processing: heat_shock/DEGs_heat_shock_results.xlsx
Sample name: heat_shock_heat_shock_results
✓ Completed: 23 up, 34 down genes

... and so on
```

## Output Structure
```
my_results/
├── plots/                                    # Comparison plots
│   ├── hypoxia_treatment_hypoxia_vs_control_GO_biological_process_significant.png
│   ├── heat_shock_heat_shock_results_kegg_pathways_significant.png
│   └── ...
├── go_results/                              # GO enrichment results
│   ├── hypoxia_treatment_hypoxia_vs_control_up_GO_Biological_Process.xlsx
│   ├── heat_shock_heat_shock_results_down_GO_Molecular_Function.xlsx
│   └── ...
├── pathway_results/                         # Pathway enrichment results
│   ├── drug_treatment_A_drug_A_analysis_up_WikiPathways.xlsx
│   ├── time_course_6h_vs_0h_down_KEGG.xlsx
│   └── ...
├── summary/
│   └── batch_analysis_summary.xlsx          # Overview of all analyses
└── enrichment_analysis.log                 # Detailed log
```

## Summary Report Example
The `batch_analysis_summary.xlsx` will contain:

| sample_name | folder | original_filename | status | up_genes_count | down_genes_count | go_biological_process_up_significant | kegg_up_significant |
|-------------|--------|------------------|--------|----------------|------------------|-------------------------------------|-------------------|
| hypoxia_treatment_hypoxia_vs_control | hypoxia_treatment | DEGs_hypoxia_vs_control.xlsx | success | 45 | 67 | 12 | 5 |
| heat_shock_heat_shock_results | heat_shock | DEGs_heat_shock_results.xlsx | success | 23 | 34 | 8 | 3 |
| drug_treatment_A_drug_A_analysis | drug_treatment_A | DEGs_drug_A_analysis.xlsx | success | 67 | 89 | 15 | 7 |

## Custom Column Names
If your XLSX files have different column names:
```bash
python batch_script.py batch your_project_folder/ \
    --output my_results \
    --gene-col "GeneName" \
    --regulation-col "Direction"
```

## Filtering and Quality Control
The script automatically handles:
- Empty gene lists (skips analysis)
- Network timeouts (retries)
- Invalid file formats (logs error, continues)
- Missing columns (clear error message)

## Troubleshooting

### No files found?
```bash
# Check if files actually start with "DEGs"
ls your_project_folder/*/DEGs*.xlsx

# If files have different naming, you can modify the pattern
python enrichment_pipeline.py --input your_project_folder/ --batch --pattern "*DEG*.xlsx"
```

### Files found but analysis fails?
Check the log file for details:
```bash
tail -f enrichment_analysis.log
```

Common issues:
- Column names don't match (`gene` vs `GeneName`)
- Regulation values aren't "Upregulated"/"Downregulated" 
- Internet connection issues (enrichment APIs need web access)

## Performance Tips

### For large datasets (100+ files):
1. **Run overnight**: Large batch jobs can take several hours
2. **Check internet**: APIs may have rate limits
3. **Monitor progress**: Watch the log file
4. **Resume failed analyses**: The script continues even if some files fail

### Memory usage:
- Each file analysis uses ~200MB RAM
- For 50+ files, ensure you have 4GB+ available
- Results are saved incrementally (won't lose progress)

## Integration with Your Workflow

### 1. Automated Pipeline
```bash
#!/bin/bash
# Process new DEG files automatically
python batch_script.py batch /path/to/new_analyses/ --output daily_results_$(date +%Y%m%d)
```

### 2. Compare Across Conditions
After analysis, you can compare results programmatically:
```python
import pandas as pd

# Load summary
summary = pd.read_excel('my_results/summary/batch_analysis_summary.xlsx')

# Find conditions with most upregulated genes
top_up = summary.nlargest(5, 'up_genes_count')
print("Top conditions by upregulated genes:")
print(top_up[['sample_name', 'up_genes_count']])
```

### 3. Generate Report
```python
# Load GO results for comparison
import pandas as pd
import matplotlib.pyplot as plt

# Compare biological processes across conditions
bp_files = [
    'my_results/go_results/hypoxia_treatment_hypoxia_vs_control_up_GO_Biological_Process.xlsx',
    'my_results/go_results/heat_shock_heat_shock_results_up_GO_Biological_Process.xlsx'
]

for file in bp_files:
    df = pd.read_excel(file)
    significant = df[df['Adjusted P-value'] < 0.05]
    print(f"\n{file.split('/')[-1]}:")
    print(significant[['Term', 'Adjusted P-value']].head())
```

This setup makes it incredibly easy to process your nested directory structure with minimal manual intervention while maintaining full traceability and organized outputs.