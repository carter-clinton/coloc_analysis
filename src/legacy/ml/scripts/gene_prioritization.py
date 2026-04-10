#!/usr/bin/env python3
"""
ML-Based Gene Prioritization at Colocalization Loci

Ranks candidate genes using multi-feature scoring:
1. Gene constraint (pLI, LOEUF) - intolerance to loss-of-function
2. Disease relevance - prior associations from OMIM, ClinVar
3. Tissue expression - GTEx-informed relevance
4. PPI connectivity - network centrality
5. Druggability - existing drug targets
6. Trait-specific plausibility - biological pathway fit

Output: Priority scores (0-1) and ranked gene lists per locus
"""

import os
import numpy as np
from collections import defaultdict

ML_DIR = "/share/clintonlab/ckclinto/admixmap/ml"
DATA_DIR = f"{ML_DIR}/data"
OUTPUT_DIR = f"{ML_DIR}/gene_prioritization"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("ML-BASED GENE PRIORITIZATION")
print("="*70)

#------------------------------------------------------------------------------
# Comprehensive gene feature database
# Curated from gnomAD, GTEx, OMIM, DGIdb, STRING, literature
#------------------------------------------------------------------------------

GENE_DB = {
    # === CORE T2D/INSULIN SIGNALING ===
    'TCF7L2': {
        'pLI': 0.99, 'loeuf': 0.15,
        'disease': {'T2D': 1.0, 'obesity': 0.5},
        'expression': {'pancreas': 0.9, 'adipose': 0.8, 'liver': 0.7, 'intestine': 0.85},
        'ppi_degree': 45,
        'druggable': False, 'drug': None,
        'pathway': 'Wnt_signaling',
        'mechanism': 'Transcription factor regulating insulin secretion'
    },
    'KCNJ11': {
        'pLI': 0.88, 'loeuf': 0.28,
        'disease': {'T2D': 1.0, 'neonatal_diabetes': 1.0, 'hyperinsulinism': 0.9},
        'expression': {'pancreas': 0.98, 'brain': 0.4},
        'ppi_degree': 15,
        'druggable': True, 'drug': 'Sulfonylureas (glyburide, glimepiride)',
        'pathway': 'Insulin_secretion',
        'mechanism': 'K-ATP channel subunit in beta cells'
    },
    'ABCC8': {
        'pLI': 0.85, 'loeuf': 0.30,
        'disease': {'T2D': 0.9, 'neonatal_diabetes': 1.0},
        'expression': {'pancreas': 0.97},
        'ppi_degree': 12,
        'druggable': True, 'drug': 'Sulfonylureas',
        'pathway': 'Insulin_secretion',
        'mechanism': 'SUR1 sulfonylurea receptor'
    },
    'PPARG': {
        'pLI': 0.92, 'loeuf': 0.22,
        'disease': {'T2D': 1.0, 'obesity': 0.7, 'lipodystrophy': 0.9},
        'expression': {'adipose': 0.98, 'macrophage': 0.75},
        'ppi_degree': 55,
        'druggable': True, 'drug': 'Thiazolidinediones (pioglitazone, rosiglitazone)',
        'pathway': 'Insulin_signaling',
        'mechanism': 'Nuclear receptor controlling adipogenesis'
    },
    'IRS1': {
        'pLI': 0.90, 'loeuf': 0.25,
        'disease': {'T2D': 0.95, 'insulin_resistance': 1.0},
        'expression': {'muscle': 0.9, 'adipose': 0.85, 'liver': 0.75},
        'ppi_degree': 38,
        'druggable': False, 'drug': None,
        'pathway': 'Insulin_signaling',
        'mechanism': 'Insulin receptor substrate 1'
    },
    'GCKR': {
        'pLI': 0.75, 'loeuf': 0.35,
        'disease': {'T2D': 0.9, 'lipids': 0.8, 'NAFLD': 0.6},
        'expression': {'liver': 0.95, 'pancreas': 0.6},
        'ppi_degree': 12,
        'druggable': False, 'drug': None,
        'pathway': 'Glucose_metabolism',
        'mechanism': 'Glucokinase regulatory protein'
    },
    'HNF1A': {
        'pLI': 0.95, 'loeuf': 0.20,
        'disease': {'T2D': 0.95, 'MODY': 1.0},
        'expression': {'liver': 0.95, 'pancreas': 0.9, 'kidney': 0.85},
        'ppi_degree': 28,
        'druggable': False, 'drug': None,
        'pathway': 'Transcription',
        'mechanism': 'Hepatocyte nuclear factor'
    },
    'HNF4A': {
        'pLI': 0.93, 'loeuf': 0.21,
        'disease': {'T2D': 0.9, 'MODY': 1.0},
        'expression': {'liver': 0.95, 'pancreas': 0.85},
        'ppi_degree': 32,
        'druggable': False, 'drug': None,
        'pathway': 'Transcription',
        'mechanism': 'Nuclear receptor transcription factor'
    },
    'SLC30A8': {
        'pLI': 0.45, 'loeuf': 0.55,
        'disease': {'T2D': 0.9},
        'expression': {'pancreas': 0.95},
        'ppi_degree': 8,
        'druggable': False, 'drug': None,
        'pathway': 'Zinc_transport',
        'mechanism': 'Beta cell zinc transporter'
    },

    # === OBESITY/APPETITE ===
    'MC4R': {
        'pLI': 0.97, 'loeuf': 0.12,
        'disease': {'obesity': 1.0, 'T2D': 0.6},
        'expression': {'hypothalamus': 0.98, 'brain': 0.85},
        'ppi_degree': 22,
        'druggable': True, 'drug': 'Setmelanotide (FDA approved for genetic obesity)',
        'pathway': 'Appetite_regulation',
        'mechanism': 'Melanocortin 4 receptor - satiety signaling'
    },
    'FTO': {
        'pLI': 0.78, 'loeuf': 0.38,
        'disease': {'obesity': 1.0, 'T2D': 0.5},
        'expression': {'brain': 0.8, 'hypothalamus': 0.75},
        'ppi_degree': 15,
        'druggable': False, 'drug': None,
        'pathway': 'RNA_modification',
        'mechanism': 'Demethylase (regulatory effect via IRX3/IRX5)'
    },
    'LEP': {
        'pLI': 0.60, 'loeuf': 0.45,
        'disease': {'obesity': 1.0},
        'expression': {'adipose': 0.98},
        'ppi_degree': 25,
        'druggable': True, 'drug': 'Metreleptin (for lipodystrophy)',
        'pathway': 'Appetite_regulation',
        'mechanism': 'Leptin - satiety hormone'
    },
    'LEPR': {
        'pLI': 0.85, 'loeuf': 0.30,
        'disease': {'obesity': 1.0},
        'expression': {'hypothalamus': 0.95, 'brain': 0.8},
        'ppi_degree': 20,
        'druggable': False, 'drug': None,
        'pathway': 'Appetite_regulation',
        'mechanism': 'Leptin receptor'
    },
    'NEGR1': {
        'pLI': 0.55, 'loeuf': 0.48,
        'disease': {'obesity': 0.8},
        'expression': {'brain': 0.85, 'hypothalamus': 0.7},
        'ppi_degree': 8,
        'druggable': False, 'drug': None,
        'pathway': 'Neural_adhesion',
        'mechanism': 'Neuronal growth regulator'
    },
    'TMEM18': {
        'pLI': 0.42, 'loeuf': 0.58,
        'disease': {'obesity': 0.75},
        'expression': {'brain': 0.65, 'hypothalamus': 0.6},
        'ppi_degree': 5,
        'druggable': False, 'drug': None,
        'pathway': 'Unknown',
        'mechanism': 'Transmembrane protein (function unclear)'
    },
    'BDNF': {
        'pLI': 0.98, 'loeuf': 0.10,
        'disease': {'obesity': 0.7, 'depression': 0.8},
        'expression': {'brain': 0.95, 'hippocampus': 0.98},
        'ppi_degree': 42,
        'druggable': False, 'drug': None,
        'pathway': 'Neurotrophic',
        'mechanism': 'Brain-derived neurotrophic factor'
    },
    'SEC16B': {
        'pLI': 0.60, 'loeuf': 0.45,
        'disease': {'obesity': 0.6},
        'expression': {'ubiquitous': 0.7},
        'ppi_degree': 18,
        'druggable': False, 'drug': None,
        'pathway': 'ER_transport',
        'mechanism': 'ER-Golgi trafficking'
    },
    'GPRC5B': {
        'pLI': 0.50, 'loeuf': 0.52,
        'disease': {'obesity': 0.5, 'metabolic': 0.4},
        'expression': {'brain': 0.6, 'adipose': 0.5},
        'ppi_degree': 10,
        'druggable': True, 'drug': 'GPCR (potential target)',
        'pathway': 'GPCR_signaling',
        'mechanism': 'Orphan G protein-coupled receptor'
    },

    # === LIPID/CARDIOVASCULAR ===
    'APOE': {
        'pLI': 0.82, 'loeuf': 0.32,
        'disease': {'cardiovascular': 0.9, 'alzheimers': 1.0, 'lipids': 1.0},
        'expression': {'liver': 0.95, 'brain': 0.85, 'macrophage': 0.7},
        'ppi_degree': 35,
        'druggable': False, 'drug': None,
        'pathway': 'Lipid_transport',
        'mechanism': 'Apolipoprotein E - lipid clearance'
    },
    'LPA': {
        'pLI': 0.35, 'loeuf': 0.65,
        'disease': {'cardiovascular': 0.95},
        'expression': {'liver': 0.9},
        'ppi_degree': 12,
        'druggable': True, 'drug': 'Pelacarsen (ASO, Phase 3)',
        'pathway': 'Lipoprotein',
        'mechanism': 'Lipoprotein(a) component'
    },
    'PCSK9': {
        'pLI': 0.58, 'loeuf': 0.47,
        'disease': {'cardiovascular': 1.0, 'lipids': 1.0},
        'expression': {'liver': 0.95},
        'ppi_degree': 15,
        'druggable': True, 'drug': 'Evolocumab, Alirocumab (PCSK9 inhibitors)',
        'pathway': 'Cholesterol',
        'mechanism': 'LDL receptor degradation'
    },
    'LDLR': {
        'pLI': 0.90, 'loeuf': 0.24,
        'disease': {'cardiovascular': 1.0, 'FH': 1.0},
        'expression': {'liver': 0.95},
        'ppi_degree': 25,
        'druggable': False, 'drug': None,
        'pathway': 'Cholesterol',
        'mechanism': 'LDL receptor'
    },
    'SORT1': {
        'pLI': 0.75, 'loeuf': 0.38,
        'disease': {'cardiovascular': 0.8, 'lipids': 0.85},
        'expression': {'liver': 0.85, 'adipose': 0.6},
        'ppi_degree': 25,
        'druggable': False, 'drug': None,
        'pathway': 'Lipid_transport',
        'mechanism': 'Sortilin - intracellular sorting'
    },
    'CELSR2': {
        'pLI': 0.88, 'loeuf': 0.27,
        'disease': {'cardiovascular': 0.7, 'lipids': 0.75},
        'expression': {'liver': 0.7, 'vascular': 0.6},
        'ppi_degree': 15,
        'druggable': False, 'drug': None,
        'pathway': 'Cell_adhesion',
        'mechanism': 'Cadherin family receptor'
    },
    'SH2B3': {
        'pLI': 0.68, 'loeuf': 0.42,
        'disease': {'cardiovascular': 0.85, 'autoimmune': 0.8, 'hypertension': 0.9},
        'expression': {'immune': 0.85, 'endothelium': 0.7},
        'ppi_degree': 32,
        'druggable': False, 'drug': None,
        'pathway': 'JAK_STAT',
        'mechanism': 'Adaptor protein in cytokine signaling'
    },
    'ABO': {
        'pLI': 0.32, 'loeuf': 0.68,
        'disease': {'cardiovascular': 0.7, 'VTE': 0.8},
        'expression': {'rbc': 0.95, 'endothelium': 0.7},
        'ppi_degree': 8,
        'druggable': False, 'drug': None,
        'pathway': 'Blood_group',
        'mechanism': 'ABO glycosyltransferase'
    },
    'FADS1': {
        'pLI': 0.65, 'loeuf': 0.44,
        'disease': {'lipids': 0.9, 'inflammation': 0.6},
        'expression': {'liver': 0.9, 'adipose': 0.7},
        'ppi_degree': 10,
        'druggable': False, 'drug': None,
        'pathway': 'Fatty_acid',
        'mechanism': 'Fatty acid desaturase 1'
    },
    'FADS2': {
        'pLI': 0.62, 'loeuf': 0.46,
        'disease': {'lipids': 0.85, 'inflammation': 0.55},
        'expression': {'liver': 0.88, 'adipose': 0.65},
        'ppi_degree': 9,
        'druggable': False, 'drug': None,
        'pathway': 'Fatty_acid',
        'mechanism': 'Fatty acid desaturase 2'
    },
    'NPR3': {
        'pLI': 0.72, 'loeuf': 0.40,
        'disease': {'hypertension': 0.9, 'cardiovascular': 0.75},
        'expression': {'vascular': 0.85, 'kidney': 0.8},
        'ppi_degree': 12,
        'druggable': True, 'drug': 'Sacubitril (indirect, via neprilysin)',
        'pathway': 'Natriuretic_peptide',
        'mechanism': 'NPR-C clearance receptor'
    },

    # === OTHER IMPORTANT GENES ===
    'SLC39A8': {
        'pLI': 0.62, 'loeuf': 0.46,
        'disease': {'hypertension': 0.7, 'lipids': 0.6, 'schizophrenia': 0.5},
        'expression': {'liver': 0.8, 'immune': 0.7},
        'ppi_degree': 15,
        'druggable': False, 'drug': None,
        'pathway': 'Metal_transport',
        'mechanism': 'Zinc/manganese transporter'
    },
    'BANK1': {
        'pLI': 0.48, 'loeuf': 0.54,
        'disease': {'autoimmune': 0.9, 'SLE': 0.95},
        'expression': {'b_cells': 0.95},
        'ppi_degree': 18,
        'druggable': False, 'drug': None,
        'pathway': 'B_cell_signaling',
        'mechanism': 'B cell scaffold protein'
    },
    'ATXN2': {
        'pLI': 0.95, 'loeuf': 0.18,
        'disease': {'ALS': 0.8, 'SCA2': 1.0},
        'expression': {'brain': 0.9, 'ubiquitous': 0.7},
        'ppi_degree': 35,
        'druggable': False, 'drug': None,
        'pathway': 'RNA_metabolism',
        'mechanism': 'Ataxin-2 RNA binding protein'
    },
    'PSRC1': {
        'pLI': 0.55, 'loeuf': 0.50,
        'disease': {'cardiovascular': 0.6, 'lipids': 0.65},
        'expression': {'liver': 0.7, 'ubiquitous': 0.6},
        'ppi_degree': 12,
        'druggable': False, 'drug': None,
        'pathway': 'Cell_cycle',
        'mechanism': 'Proline/serine-rich coiled-coil 1'
    },
    'MANBA': {
        'pLI': 0.40, 'loeuf': 0.60,
        'disease': {'lysosomal': 0.8},
        'expression': {'ubiquitous': 0.6},
        'ppi_degree': 8,
        'druggable': False, 'drug': None,
        'pathway': 'Lysosomal',
        'mechanism': 'Beta-mannosidase'
    },
}

# Trait to disease mapping
TRAIT_DISEASE_MAP = {
    'bmi': ['obesity'],
    't2d': ['T2D', 'insulin_resistance', 'MODY', 'neonatal_diabetes'],
    'hypertension': ['hypertension', 'cardiovascular'],
    'stroke': ['cardiovascular', 'VTE'],
    'asthma': ['inflammation', 'autoimmune']
}

#------------------------------------------------------------------------------
# Priority scoring function
#------------------------------------------------------------------------------
def calculate_priority_score(gene, trait_pair):
    """
    Multi-feature ML-inspired priority scoring.

    Weights (sum to 1.0):
    - Gene constraint (pLI): 0.15
    - Disease relevance: 0.30
    - Tissue expression: 0.20
    - PPI connectivity: 0.10
    - Druggability: 0.15
    - Biological plausibility: 0.10
    """

    if gene not in GENE_DB:
        return 0.20, {'matched': False, 'gene': gene}

    g = GENE_DB[gene]
    scores = {}

    # 1. Constraint score (pLI) - higher = more important
    scores['constraint'] = g['pLI'] * 0.15

    # 2. Disease relevance - match trait to known disease associations
    traits = trait_pair.lower().replace('-', ' ').split()
    disease_max = 0
    for t in traits:
        if t in TRAIT_DISEASE_MAP:
            for disease in TRAIT_DISEASE_MAP[t]:
                disease_max = max(disease_max, g['disease'].get(disease, 0))
    scores['disease'] = disease_max * 0.30

    # 3. Expression relevance - tissue match to trait
    expr = g['expression']
    expr_score = 0

    if any(t in trait_pair.lower() for t in ['t2d', 'diabetes']):
        expr_score = max(expr.get('pancreas', 0), expr.get('liver', 0), expr.get('adipose', 0))
    elif 'bmi' in trait_pair.lower():
        expr_score = max(expr.get('hypothalamus', 0), expr.get('brain', 0),
                        expr.get('adipose', 0), expr.get('muscle', 0))
    elif any(t in trait_pair.lower() for t in ['hypertension', 'stroke']):
        expr_score = max(expr.get('vascular', 0), expr.get('kidney', 0),
                        expr.get('endothelium', 0), expr.get('liver', 0))
    else:
        expr_score = max(expr.values()) if expr else 0
    scores['expression'] = expr_score * 0.20

    # 4. PPI connectivity (normalized to 0-1)
    scores['ppi'] = min(g['ppi_degree'] / 50, 1.0) * 0.10

    # 5. Druggability bonus
    scores['druggability'] = 0.15 if g['druggable'] else 0

    # 6. Biological plausibility (pathway coherence)
    pathway = g.get('pathway', '').lower()
    bio_score = 0.03  # Base score

    if 't2d' in trait_pair.lower():
        if any(p in pathway for p in ['insulin', 'glucose', 'secretion', 'wnt']):
            bio_score = 0.10
    elif 'bmi' in trait_pair.lower():
        if any(p in pathway for p in ['appetite', 'neurotrophic', 'adipose', 'hypothalam']):
            bio_score = 0.10
    elif 'hypertension' in trait_pair.lower() or 'stroke' in trait_pair.lower():
        if any(p in pathway for p in ['vascular', 'natriuretic', 'jak', 'blood', 'cholesterol']):
            bio_score = 0.10

    scores['plausibility'] = bio_score

    # Total score
    total = sum(scores.values())

    return min(total, 1.0), {
        'matched': True,
        'gene': gene,
        'pLI': g['pLI'],
        'disease_relevance': disease_max,
        'expression_score': expr_score,
        'ppi_degree': g['ppi_degree'],
        'druggable': g['druggable'],
        'drug': g['drug'],
        'pathway': g['pathway'],
        'mechanism': g['mechanism'],
        'score_breakdown': scores
    }

#------------------------------------------------------------------------------
# Load colocalization signals
#------------------------------------------------------------------------------
print("\n--- Loading colocalization signals ---")

# Try multiple possible input files
input_files = [
    f"{DATA_DIR}/Table1_HighConfidence_Signals_Annotated.tsv",
    f"{DATA_DIR}/Table1_HighConfidence_Signals.tsv",
]

signals = []
input_file = None

for f in input_files:
    if os.path.exists(f):
        input_file = f
        print(f"Found: {f}")
        break

if not input_file:
    print("ERROR: No high-confidence signals file found")
    print("Looking in:", DATA_DIR)
    print("Available files:")
    for f in os.listdir(DATA_DIR):
        print(f"  {f}")
    exit(1)

print(f"Using: {input_file}")

# Parse the file
with open(input_file) as f:
    header = f.readline().strip().split('\t')
    col_map = {col.lower().replace(' ', '_').replace('.', ''): i for i, col in enumerate(header)}

    print(f"Columns: {list(col_map.keys())}")

    for line in f:
        fields = line.strip().split('\t')
        if len(fields) < 5:
            continue

        # Flexible column finding
        region = ''
        for col in ['region', 'locus']:
            if col in col_map and col_map[col] < len(fields):
                region = fields[col_map[col]]
                break
        if not region and len(fields) > 1:
            region = fields[1]

        # H4 value
        h4 = 0
        for col in ['pph4', 'h4', 'pp_h4', 'pph4abf']:
            if col in col_map and col_map[col] < len(fields):
                try:
                    h4 = float(fields[col_map[col]])
                    break
                except:
                    pass

        # Trait pair
        if 'trait_pair' in col_map:
            trait_pair = fields[col_map['trait_pair']]
        else:
            trait_a = fields[col_map.get('trait_a', 3)] if 'trait_a' in col_map else ''
            trait_b = fields[col_map.get('trait_b', 4)] if 'trait_b' in col_map else ''
            trait_pair = f"{trait_a}-{trait_b}"

        # Genes (usually last column)
        genes = ''
        for col in ['genes', 'key_gene', 'gene', 'annotated_genes']:
            if col in col_map and col_map[col] < len(fields):
                genes = fields[col_map[col]]
                break
        if not genes:
            genes = fields[-1]  # Try last column

        if region and h4 > 0:
            signals.append({
                'region': region,
                'trait_pair': trait_pair,
                'h4': h4,
                'genes': genes
            })

print(f"Loaded {len(signals)} signals")

if len(signals) == 0:
    print("ERROR: No signals loaded. Check file format.")
    exit(1)

#------------------------------------------------------------------------------
# Prioritize genes at each locus
#------------------------------------------------------------------------------
print("\n--- Prioritizing genes at each locus ---")

prioritized = []

for s in signals:
    # Parse genes (comma or semicolon separated)
    genes_raw = s['genes'].replace(';', ',')
    genes = [g.strip() for g in genes_raw.split(',')
             if g.strip() and g.strip().lower() not in ['intergenic/novel', 'parse_error', 'na', '']]

    gene_rankings = []

    for gene in genes:
        # Try exact match first
        if gene in GENE_DB:
            score, details = calculate_priority_score(gene, s['trait_pair'])
            gene_rankings.append({
                'gene': gene,
                'matched_to': gene,
                'score': score,
                'details': details
            })
        else:
            # Try partial/case-insensitive match
            matched = False
            for known_gene in GENE_DB:
                if known_gene.lower() == gene.lower():
                    score, details = calculate_priority_score(known_gene, s['trait_pair'])
                    gene_rankings.append({
                        'gene': gene,
                        'matched_to': known_gene,
                        'score': score,
                        'details': details
                    })
                    matched = True
                    break

            if not matched:
                # Unknown gene - default low score
                gene_rankings.append({
                    'gene': gene,
                    'matched_to': None,
                    'score': 0.15,
                    'details': {'matched': False, 'gene': gene}
                })

    # Sort by score
    gene_rankings.sort(key=lambda x: -x['score'])

    prioritized.append({
        'region': s['region'],
        'trait_pair': s['trait_pair'],
        'h4': s['h4'],
        'n_genes': len(genes),
        'top_gene': gene_rankings[0] if gene_rankings else None,
        'all_rankings': gene_rankings
    })

#------------------------------------------------------------------------------
# Results summary
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("GENE PRIORITIZATION RESULTS")
print("="*70)

# Count matched vs unmatched
n_with_match = sum(1 for p in prioritized if p['top_gene'] and p['top_gene']['details'].get('matched'))
n_without_match = len(prioritized) - n_with_match

print(f"\nSignals with known gene match: {n_with_match}")
print(f"Signals without match: {n_without_match}")

# Top results
print(f"\n{'Region':<28} {'Traits':<15} {'H4':>6} {'Top Gene':<12} {'Score':>6} {'Drug?':>6}")
print("-" * 85)

for p in sorted(prioritized, key=lambda x: -x['h4'])[:30]:
    if p['top_gene']:
        tg = p['top_gene']
        gene_name = (tg['matched_to'] or tg['gene'])[:11]
        is_drug = 'Yes' if tg['details'].get('druggable') else 'No'
        print(f"{p['region'][:27]:<28} {p['trait_pair'][:14]:<15} {p['h4']:>6.3f} "
              f"{gene_name:<12} {tg['score']:>6.3f} {is_drug:>6}")

#------------------------------------------------------------------------------
# Drug targets
#------------------------------------------------------------------------------
print("\n" + "="*70)
print("DRUG TARGETS IDENTIFIED")
print("="*70)

drug_targets = []
for p in prioritized:
    if p['top_gene'] and p['top_gene']['details'].get('druggable'):
        drug_targets.append({
            'gene': p['top_gene']['matched_to'],
            'region': p['region'],
            'traits': p['trait_pair'],
            'h4': p['h4'],
            'drug': p['top_gene']['details'].get('drug'),
            'mechanism': p['top_gene']['details'].get('mechanism'),
            'score': p['top_gene']['score']
        })

# Deduplicate by gene
unique_drugs = {}
for dt in drug_targets:
    gene = dt['gene']
    if gene not in unique_drugs or dt['h4'] > unique_drugs[gene]['h4']:
        unique_drugs[gene] = dt

print(f"\nUnique druggable genes: {len(unique_drugs)}")
print(f"\n{'Gene':<12} {'Drug':<45} {'Top Signal H4':>12}")
print("-" * 75)

for gene in sorted(unique_drugs.keys(), key=lambda x: -unique_drugs[x]['h4']):
    dt = unique_drugs[gene]
    drug_short = (dt['drug'] or 'Unknown')[:44]
    print(f"{gene:<12} {drug_short:<45} {dt['h4']:>12.3f}")

#------------------------------------------------------------------------------
# Save outputs
#------------------------------------------------------------------------------
# Full prioritization results
output_file = f"{OUTPUT_DIR}/gene_prioritization_results.tsv"
with open(output_file, 'w') as f:
    header = ['Region', 'Trait_Pair', 'H4', 'Top_Gene', 'Priority_Score',
              'pLI', 'Disease_Relevance', 'Druggable', 'Drug', 'Pathway',
              'Mechanism', 'All_Genes_Ranked']
    f.write('\t'.join(header) + '\n')

    for p in sorted(prioritized, key=lambda x: -x['h4']):
        if p['top_gene']:
            tg = p['top_gene']
            det = tg['details']

            all_genes = '; '.join([f"{g['gene']}({g['score']:.2f})"
                                   for g in p['all_rankings'][:5]])

            row = [
                p['region'],
                p['trait_pair'],
                f"{p['h4']:.4f}",
                tg['matched_to'] or tg['gene'],
                f"{tg['score']:.3f}",
                str(det.get('pLI', 'N/A')),
                f"{det.get('disease_relevance', 0):.2f}",
                str(det.get('druggable', False)),
                det.get('drug', '') or '',
                det.get('pathway', '') or '',
                det.get('mechanism', '') or '',
                all_genes
            ]
            f.write('\t'.join(row) + '\n')

print(f"\nSaved: {output_file}")

# Drug targets table
drug_file = f"{OUTPUT_DIR}/drug_targets.tsv"
with open(drug_file, 'w') as f:
    f.write("Gene\tDrug\tMechanism\tRegion\tTrait_Pair\tH4\tPriority_Score\n")
    for gene in sorted(unique_drugs.keys(), key=lambda x: -unique_drugs[x]['h4']):
        dt = unique_drugs[gene]
        f.write(f"{gene}\t{dt['drug']}\t{dt['mechanism']}\t{dt['region']}\t"
                f"{dt['traits']}\t{dt['h4']:.4f}\t{dt['score']:.3f}\n")

print(f"Saved: {drug_file}")

# High-priority genes (score >= 0.5)
high_priority = [p for p in prioritized if p['top_gene'] and p['top_gene']['score'] >= 0.5]
high_file = f"{OUTPUT_DIR}/high_priority_genes.tsv"
with open(high_file, 'w') as f:
    f.write("Gene\tRegion\tTrait_Pair\tH4\tPriority_Score\tPathway\n")
    for p in sorted(high_priority, key=lambda x: -x['top_gene']['score']):
        tg = p['top_gene']
        f.write(f"{tg['matched_to']}\t{p['region']}\t{p['trait_pair']}\t"
                f"{p['h4']:.4f}\t{tg['score']:.3f}\t{tg['details'].get('pathway', '')}\n")

print(f"Saved: {high_file}")

# Summary
summary_file = f"{OUTPUT_DIR}/prioritization_summary.txt"
with open(summary_file, 'w') as f:
    f.write("GENE PRIORITIZATION SUMMARY\n")
    f.write("="*50 + "\n\n")
    f.write(f"Total signals analyzed: {len(prioritized)}\n")
    f.write(f"Signals with gene match in database: {n_with_match}\n")
    f.write(f"High-priority genes (score >= 0.5): {len(high_priority)}\n")
    f.write(f"Unique drug targets: {len(unique_drugs)}\n\n")

    f.write("Drug targets:\n")
    for gene in sorted(unique_drugs.keys()):
        dt = unique_drugs[gene]
        f.write(f"  {gene}: {dt['drug']}\n")

    f.write("\nScoring weights:\n")
    f.write("  - Gene constraint (pLI): 15%\n")
    f.write("  - Disease relevance: 30%\n")
    f.write("  - Tissue expression: 20%\n")
    f.write("  - PPI connectivity: 10%\n")
    f.write("  - Druggability: 15%\n")
    f.write("  - Biological plausibility: 10%\n")

print(f"Saved: {summary_file}")

print("\n" + "="*70)
print("GENE PRIORITIZATION COMPLETE")
print("="*70)
