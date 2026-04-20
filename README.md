# Spectral Analysis of Indigenous Social Networks

> **Paper:** *Spectral Analysis of Indigenous Social Networks: Mapping Traditional Knowledge Sharing*
> **Authors:** Apurva Mehta, Chintan Chatterjee, Malay Bhatt
> **Institution:** Dharmsinh Desai University, Nadiad, India; Charutar Vidya Mandal University

---

## Overview

This repository contains the full Python implementation for the computational prototype described in the paper. The project applies **spectral graph theory** and **social network analysis (SNA)** to model knowledge-sharing dynamics in indigenous communities, operationalising cultural concepts such as relational harmony, cohesion, and resilience through formal network metrics.

The prototype uses a **principled synthetic dataset** grounded in ethnographic literature on Indian tribal communities (Gond, Bhil, Irula), with all parameters explicitly cited and justified.

---

## Project Structure

```
spectral_iks_project/
│
├── src/
│   └── spectral_analysis.py     # Main analysis script (all figures + metrics)
│
├── data/
│   ├── nodes.csv                # Node-level dataset (role, degree, weighted degree)
│   ├── edges.csv                # Edge-level dataset (source, target, weight, type)
│   ├── sna_metrics.csv          # Betweenness, closeness, clustering per node
│   └── summary_statistics.csv   # Network-level summary table
│
├── figures/                     # All publication figures (300 DPI PNG)
│   ├── fig3_spectral_clustering.png
│   ├── fig5_network_overview.png
│   ├── fig6_laplacian_spectrum.png
│   ├── fig8_diffusion_dynamics.png
│   └── fig9_resilience.png
│
├── docs/
│   └── dataset_rationale.md     # Full parameter justification with citations
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/spectral-iks.git
cd spectral-iks
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the analysis
```bash
python src/spectral_analysis.py
```

Figures are saved to `figures/` and data outputs to `outputs/`.

---

## Dataset

The synthetic network encodes a 25-node, 5-role indigenous community:

| Role | Count | Description |
|------|-------|-------------|
| Elder | 7 | Senior knowledge keepers |
| Healer | 5 | Specialist practitioners |
| Youth | 6 | Learners and cultural carriers |
| Council | 4 | Governance bridge nodes |
| Mediator | 3 | Cross-domain connectors |

**Edge weights** encode relational strength:
- Intra-group ties: `Beta(5,2)` distribution → mean ≈ 0.71 (strong/frequent)
- Inter-group ties: `Beta(2,5)` distribution → mean ≈ 0.29 (weak/occasional)

See `docs/dataset_rationale.md` for full parameter justification and citations.

---

## Key Outputs

| Metric | Value |
|--------|-------|
| Nodes (N) | 25 |
| Edges | 63 |
| Algebraic Connectivity (λ₂) | 0.2095 |
| Avg Clustering Coefficient | 0.2226 |
| Avg Shortest Path Length | 2.153 |
| Network Diameter | 4 |

---

## Reproducibility

All random operations use `SEED = 42`. Running `src/spectral_analysis.py` will reproduce all figures and tables exactly.

---

## Citation

If you use this code, please cite:

```
Mehta, A., Chatterjee, C., & Bhatt, M. (2025). Spectral Analysis of Indigenous
Social Networks: Mapping Traditional Knowledge Sharing. [Journal Name].
```

---

## License

MIT License — see `LICENSE` for details.

---

## Contact

**Apurva Mehta** — apurvamehta.ce@ddu.ac.in
