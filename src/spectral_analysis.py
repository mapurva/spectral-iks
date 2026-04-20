# -*- coding: utf-8 -*-
"""
Spectral Analysis of Indigenous Social Networks: Mapping Traditional Knowledge Sharing
=======================================================================================
Authors : Apurva Mehta, Chintan Chatterjee, Malay Bhatt
Version : 2.0  (publication-ready prototype)
Dataset : Principled synthetic network grounded in ethnographic literature on
          Indian tribal communities (Gond, Bhil, Irula) — see Section 3 of paper
          and dataset_rationale.md for parameter justification.

Sections
--------
0. Imports and global style
1. Culturally grounded network construction
2. Dataset export (nodes.csv / edges.csv)
3. Social Network Analysis (SNA) metrics
4. Spectral analysis — Laplacian spectrum & algebraic connectivity
5. Spectral embedding + k-means clustering (Figure 3 — Panels A/B/C)
6. Knowledge diffusion simulation (Figure 8)
7. Resilience analysis — node removal (Figure 9)
8. Summary statistics table
"""

# =============================================================================
# 0. Imports and global plotting style
# =============================================================================
import random
from copy import deepcopy

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import networkx as nx
from scipy import sparse
from scipy.sparse.linalg import eigsh
from sklearn.cluster import KMeans

# --- Reproducibility ---------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# --- Publication-quality plot defaults ---------------------------------------
matplotlib.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

OUTPUT_DIR = "/mnt/user-data/outputs/"

# =============================================================================
# 1. Culturally grounded network construction
# =============================================================================
"""
Parameter rationale (see dataset_rationale.md for full citations):

Role groups and sizes
---------------------
  Elders        (7)  — Senior knowledge keepers; high internal cohesion,
                        consistent with Cajete & Little Bear (2000) and
                        Berkes (2017) on elder-centric governance in IKS.
  Healers       (5)  — Specialist practitioners; moderately cohesive, frequent
                        cross-group ties to youth (apprenticeship) and elders
                        (validation). Based on Watts (Lancet 2022) on Amazonian
                        healer networks and Irula healer documentation
                        (Meena & Prasad 2021).
  Youth         (6)  — Learners and cultural carriers; lower internal cohesion,
                        high receptivity. Role consistent with Negi et al. (2022)
                        on Indian agricultural knowledge diffusion.
  Council Mbrs  (4)  — Governance bridge nodes; relatively small group with
                        broad inter-group ties reflecting panchayat-style
                        governance (Meena & Prasad 2021).
  Mediators     (3)  — Cross-domain connectors (e.g., NGO liaisons, teachers);
                        smallest group, highest betweenness by design,
                        consistent with Granovetter (1973) weak-tie theory.

Intra/Inter-group connection probabilities (p_in, p_out)
---------------------------------------------------------
  Derived from the stochastic block model parameterisation used in
  Cámara-Leret, Fortuna & Bascompte (PNAS 2019, Ref [19] in paper),
  adapted for a smaller single-village network (~25 nodes) representative
  of a Gond or Bhil hamlet (Census of India 2011 tribal hamlet size data).

  p_in  = 0.70 for Elders (tight elder council)
        = 0.65 for Healers
        = 0.55 for Youth  (peer groups but with more turnover)
        = 0.60 for Council
        = 0.50 for Mediators (bridgers: many weak ties externally)

  p_out = 0.10 (Elder-Healer, Elder-Council — high cross-group trust)
        = 0.15 (Healer-Youth — apprenticeship links)
        = 0.08 (default cross-group)

Edge weights encode relational strength on [0,1]:
  intra-group edges: Beta(5,2) => mean ~0.71 (strong, frequent interaction)
  inter-group edges: Beta(2,5) => mean ~0.29 (weaker, occasional interaction)
  This reflects Granovetter's (1973) weak/strong tie distinction.
"""

ROLES = ["Elder", "Healer", "Youth", "Council", "Mediator"]
ROLE_SIZES = [7, 5, 6, 4, 3]          # total N = 25
N = sum(ROLE_SIZES)

# Role colour palette (colour-blind friendly)
ROLE_COLORS = {
    "Elder":    "#1b6ca8",   # deep blue
    "Healer":   "#c0392b",   # red
    "Youth":    "#27ae60",   # green
    "Council":  "#8e44ad",   # purple
    "Mediator": "#e67e22",   # orange
}

# Intra-group connection probability matrix (5×5)
P_MATRIX = np.array([
    #  El    He    Yo    Co    Me
    [0.70, 0.10, 0.08, 0.10, 0.08],  # Elder
    [0.10, 0.65, 0.15, 0.08, 0.10],  # Healer
    [0.08, 0.15, 0.55, 0.08, 0.12],  # Youth
    [0.10, 0.08, 0.08, 0.60, 0.15],  # Council
    [0.08, 0.10, 0.12, 0.15, 0.50],  # Mediator
])


def build_network() -> nx.Graph:
    """
    Construct a principled synthetic indigenous knowledge-sharing network.

    Returns
    -------
    G : nx.Graph
        Weighted undirected graph with node attributes:
          - role  : str   (Elder / Healer / Youth / Council / Mediator)
          - label : str   (role abbreviation + index, e.g. 'El-1')
        Edge attributes:
          - weight : float in (0,1), encoding relational strength
          - type   : str ('intra' or 'inter')
    """
    rng = np.random.default_rng(SEED)

    # Assign role labels to node indices 0..N-1
    node_roles = []
    for role, size in zip(ROLES, ROLE_SIZES):
        node_roles.extend([role] * size)

    # Build base graph from stochastic block model
    sizes = ROLE_SIZES
    probs = P_MATRIX.tolist()
    G_raw = nx.stochastic_block_model(sizes, probs, seed=SEED)

    # Relabel nodes to meaningful labels
    mapping = {}
    counters = {r: 1 for r in ROLES}
    for i in range(N):
        role = node_roles[i]
        mapping[i] = f"{role[:2]}-{counters[role]}"
        counters[role] += 1

    G = nx.relabel_nodes(G_raw, mapping)

    # Set node attributes
    for i, (old, new) in enumerate(mapping.items()):
        G.nodes[new]["role"]  = node_roles[i]
        G.nodes[new]["label"] = new

    # Set edge weights and types
    for u, v in G.edges():
        role_u = G.nodes[u]["role"]
        role_v = G.nodes[v]["role"]
        if role_u == role_v:
            # Intra-group: strong ties ~ Beta(5,2)
            w = float(rng.beta(5, 2))
            G[u][v]["type"] = "intra"
        else:
            # Inter-group: weak ties ~ Beta(2,5)
            w = float(rng.beta(2, 5))
            G[u][v]["type"] = "inter"
        G[u][v]["weight"] = round(w, 3)

    return G


G = build_network()
print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print(f"Density: {nx.density(G):.4f}")
print(f"Connected: {nx.is_connected(G)}")


# =============================================================================
# 2. Export dataset (nodes.csv and edges.csv)
# =============================================================================
nodes_df = pd.DataFrame([
    {"node_id": n,
     "role": G.nodes[n]["role"],
     "degree": G.degree(n),
     "weighted_degree": round(sum(d["weight"] for _, _, d in G.edges(n, data=True)), 3)}
    for n in G.nodes()
])

edges_df = pd.DataFrame([
    {"source": u, "target": v,
     "weight": d["weight"],
     "type": d["type"]}
    for u, v, d in G.edges(data=True)
])

nodes_df.to_csv(OUTPUT_DIR + "nodes.csv", index=False)
edges_df.to_csv(OUTPUT_DIR + "edges.csv", index=False)
print(f"\nDataset exported: {len(nodes_df)} nodes, {len(edges_df)} edges")
print(nodes_df.groupby("role")[["degree", "weighted_degree"]].mean().round(3))


# =============================================================================
# 3. Social Network Analysis (SNA) metrics
# =============================================================================
def compute_sna(G: nx.Graph) -> pd.DataFrame:
    deg   = nx.degree_centrality(G)
    btwn  = nx.betweenness_centrality(G, weight="weight", normalized=True)
    close = nx.closeness_centrality(G)
    clust = nx.clustering(G, weight="weight")

    rows = []
    for n in G.nodes():
        rows.append({
            "node":        n,
            "role":        G.nodes[n]["role"],
            "degree_c":    round(deg[n],   4),
            "betweenness": round(btwn[n],  4),
            "closeness":   round(close[n], 4),
            "clustering":  round(clust[n], 4),
        })
    return pd.DataFrame(rows).sort_values("betweenness", ascending=False)

sna_df = compute_sna(G)
sna_df.to_csv(OUTPUT_DIR + "sna_metrics.csv", index=False)
print("\nTop 8 nodes by betweenness centrality:")
print(sna_df.head(8).to_string(index=False))


# =============================================================================
# 4. Spectral analysis — Laplacian spectrum & algebraic connectivity (Figure 6)
# =============================================================================
def laplacian_spectrum(G: nx.Graph, k: int = 8):
    """Return sorted eigenvalues and eigenvectors of the weighted Laplacian."""
    L = nx.laplacian_matrix(G, weight="weight").astype(float)
    vals, vecs = eigsh(L, k=k, which="SM")
    order = np.argsort(vals)
    return vals[order], vecs[:, order]


vals, vecs = laplacian_spectrum(G, k=8)
lambda2 = vals[1]
print(f"\nAlgebraic Connectivity (λ₂) = {lambda2:.4f}")
print(f"Eigenvalues (first 8):        {np.round(vals, 4)}")

# --- Figure 6: Laplacian spectrum -------------------------------------------
fig6, ax6 = plt.subplots(figsize=(6, 4))
ax6.plot(range(len(vals)), vals, marker="o", linewidth=2,
         color="#1b6ca8", markersize=7, markerfacecolor="white",
         markeredgewidth=2)
ax6.axhline(y=lambda2, color="#c0392b", linestyle="--", linewidth=1.2,
            label=f"λ₂ = {lambda2:.3f}  (algebraic connectivity)")
ax6.set_xlabel("Eigenvalue Index")
ax6.set_ylabel("λ Value")
ax6.set_title("Figure 6: Laplacian Spectrum of the Knowledge Network")
ax6.legend()
ax6.set_xticks(range(len(vals)))
plt.tight_layout()
fig6.savefig(OUTPUT_DIR + "fig6_laplacian_spectrum.png", bbox_inches="tight")
plt.close(fig6)
print("Saved: fig6_laplacian_spectrum.png")


# =============================================================================
# 5. Spectral embedding + k-means clustering — Figure 3 (Panels A / B / C)
# =============================================================================
def get_layout(G):
    """Deterministic spring layout seeded for reproducibility."""
    return nx.spring_layout(G, weight="weight", seed=SEED)

pos = get_layout(G)

# Node colour lists for drawing
node_list   = list(G.nodes())
role_colors = [ROLE_COLORS[G.nodes[n]["role"]] for n in node_list]

# Spectral embedding (eigenvectors 1 and 2 of normalised Laplacian)
L_norm = nx.normalized_laplacian_matrix(G, weight="weight").toarray()
eig_vals, eig_vecs = np.linalg.eigh(L_norm)
embedding = eig_vecs[:, 1:3]          # Fiedler vector + next

# K-means on embedding
kmeans  = KMeans(n_clusters=5, random_state=SEED, n_init=20)
km_labels = kmeans.fit_predict(embedding)
cluster_colors = [plt.cm.tab10(l) for l in km_labels]

# --- Figure 3 (3 panels) ----------------------------------------------------
fig3, axes = plt.subplots(1, 3, figsize=(14, 5))

# Panel A — Original network
ax = axes[0]
nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35, edge_color="grey",
                       width=[G[u][v]["weight"] * 2 for u, v in G.edges()])
nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=node_list,
                       node_color=role_colors, node_size=220)
nx.draw_networkx_labels(G, pos, ax=ax, font_size=6, font_color="white",
                        font_weight="bold")
ax.set_title("A: Original Relational Network", pad=10)
ax.axis("off")
# Legend
patches = [mpatches.Patch(color=c, label=r)
           for r, c in ROLE_COLORS.items()]
ax.legend(handles=patches, loc="upper left", fontsize=7,
          framealpha=0.8, title="Role")

# Panel B — Spectral embedding
ax = axes[1]
for role, color in ROLE_COLORS.items():
    mask = [G.nodes[n]["role"] == role for n in node_list]
    idx  = [i for i, m in enumerate(mask) if m]
    ax.scatter(embedding[idx, 0], embedding[idx, 1],
               c=color, s=80, label=role, zorder=3, edgecolors="white",
               linewidths=0.5)
ax.set_xlabel("Fiedler Vector (v₂)")
ax.set_ylabel("Third Eigenvector (v₃)")
ax.set_title("B: Laplacian Eigenvector Embedding", pad=10)
ax.legend(fontsize=7, framealpha=0.8)

# Panel C — Spectral clustering result
ax = axes[2]
nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, edge_color="grey",
                       width=[G[u][v]["weight"] * 2 for u, v in G.edges()])
nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=node_list,
                       node_color=cluster_colors, node_size=220)
nx.draw_networkx_labels(G, pos, ax=ax, font_size=6, font_color="white",
                        font_weight="bold")
ax.set_title("C: Spectral Clustering Result", pad=10)
ax.axis("off")

fig3.suptitle(
    "Figure 3: Spectral Clustering of Indigenous Knowledge Networks\n"
    "(A) Original network; (B) Laplacian eigenvector embedding; "
    "(C) Clustered communities",
    fontsize=10, y=1.01
)
plt.tight_layout()
fig3.savefig(OUTPUT_DIR + "fig3_spectral_clustering.png", bbox_inches="tight")
plt.close(fig3)
print("Saved: fig3_spectral_clustering.png")


# =============================================================================
# 6. Knowledge diffusion simulation — Figure 8
# =============================================================================
def simulate_diffusion(G: nx.Graph, seeds: list, steps: int = 8,
                       base_prob: float = 0.35) -> list:
    """
    Independent-cascade diffusion with edge weights as transmission probability
    modifiers: P(u→v) = base_prob × weight(u,v).

    Returns list of informed-node counts per time step.
    """
    informed = set(seeds)
    history  = [len(informed)]
    rng_d    = np.random.default_rng(SEED)

    for _ in range(steps):
        newly_informed = set()
        for u in informed:
            for v in G.neighbors(u):
                if v in informed:
                    continue
                w = G[u][v].get("weight", 1.0)
                if rng_d.random() < base_prob * w:
                    newly_informed.add(v)
        informed |= newly_informed
        history.append(len(informed))

    return history


# Seed from highest-betweenness Elder (most culturally realistic)
top_node = sna_df[sna_df["role"] == "Elder"].iloc[0]["node"]
diff_history = simulate_diffusion(G, seeds=[top_node], steps=8)

# --- Figure 8: Diffusion curve ----------------------------------------------
fig8, ax8 = plt.subplots(figsize=(6, 4))
ax8.plot(range(len(diff_history)), diff_history,
         marker="o", linewidth=2, color="#27ae60",
         markersize=8, markerfacecolor="white", markeredgewidth=2)
ax8.fill_between(range(len(diff_history)), diff_history,
                 alpha=0.12, color="#27ae60")
ax8.set_xlabel("Diffusion Step")
ax8.set_ylabel("Cumulative Informed Nodes")
ax8.set_title(f"Figure 8: Knowledge Diffusion Dynamics\n"
              f"(Seed: {top_node}, λ₂ = {lambda2:.3f}, "
              f"N = {G.number_of_nodes()})")
ax8.set_xticks(range(len(diff_history)))
ax8.set_xlim(-0.2, len(diff_history) - 0.8)
ax8.set_ylim(0, G.number_of_nodes() + 1)
plt.tight_layout()
fig8.savefig(OUTPUT_DIR + "fig8_diffusion_dynamics.png", bbox_inches="tight")
plt.close(fig8)
print("Saved: fig8_diffusion_dynamics.png")


# =============================================================================
# 7. Resilience analysis — node removal impact on λ₂  (Figure 9)
# =============================================================================
def node_removal_impact(G: nx.Graph) -> pd.DataFrame:
    """
    Remove each node in turn and measure the drop in algebraic connectivity.
    Returns a DataFrame sorted by impact (largest drop first).
    """
    base_ac = nx.algebraic_connectivity(G, weight="weight", seed=SEED)
    records = []
    for n in G.nodes():
        H = deepcopy(G)
        H.remove_node(n)
        if nx.is_connected(H):
            new_ac = nx.algebraic_connectivity(H, weight="weight", seed=SEED)
        else:
            new_ac = 0.0
        records.append({
            "node":   n,
            "role":   G.nodes[n]["role"],
            "impact": round(base_ac - new_ac, 5),
        })
    return pd.DataFrame(records).sort_values("impact", ascending=False)

impact_df = node_removal_impact(G)
impact_df.to_csv(OUTPUT_DIR + "resilience_impact.csv", index=False)

# --- Figure 9: Horizontal bar chart -----------------------------------------
fig9, ax9 = plt.subplots(figsize=(7, 7))

bar_colors = [ROLE_COLORS[r] for r in impact_df["role"]]
ax9.barh(impact_df["node"], impact_df["impact"],
         color=bar_colors, edgecolor="white", height=0.7)
ax9.invert_yaxis()
ax9.set_xlabel("Decrease in Algebraic Connectivity (Δλ₂)")
ax9.set_title("Figure 9: Impact of Node Removal on Network Cohesion\n"
              "(Larger bar = greater loss of collective resilience)")
ax9.axvline(x=0, color="grey", linewidth=0.8)

# Role legend on bar chart
patches = [mpatches.Patch(color=c, label=r)
           for r, c in ROLE_COLORS.items()]
ax9.legend(handles=patches, loc="lower right", fontsize=8,
           title="Role", framealpha=0.85)

plt.tight_layout()
fig9.savefig(OUTPUT_DIR + "fig9_resilience.png", bbox_inches="tight")
plt.close(fig9)
print("Saved: fig9_resilience.png")

# --- Figure 5: Network overview (publication figure) ------------------------
fig5, ax5 = plt.subplots(figsize=(8, 7))
edge_widths = [G[u][v]["weight"] * 3 for u, v in G.edges()]
edge_alphas = [0.6 if G[u][v]["type"] == "intra" else 0.25 for u, v in G.edges()]

nx.draw_networkx_edges(G, pos, ax=ax5, width=edge_widths,
                       edge_color=["#555" if G[u][v]["type"] == "intra"
                                   else "#aaa" for u, v in G.edges()],
                       alpha=0.5)
nx.draw_networkx_nodes(G, pos, ax=ax5, nodelist=node_list,
                       node_color=role_colors, node_size=350)
nx.draw_networkx_labels(G, pos, ax=ax5, font_size=7,
                        font_color="white", font_weight="bold")

patches = [mpatches.Patch(color=c, label=r) for r, c in ROLE_COLORS.items()]
ax5.legend(handles=patches, loc="upper left", fontsize=9,
           title="Community Role", framealpha=0.9)
ax5.set_title("Figure 5: Principled Synthetic Indigenous Knowledge-Sharing Network\n"
              f"(N={N}, Edges={G.number_of_edges()}, λ₂={lambda2:.3f})")
ax5.axis("off")
plt.tight_layout()
fig5.savefig(OUTPUT_DIR + "fig5_network_overview.png", bbox_inches="tight")
plt.close(fig5)
print("Saved: fig5_network_overview.png")


# =============================================================================
# 8. Summary statistics table
# =============================================================================
summary = {
    "Nodes (N)":                       N,
    "Edges":                           G.number_of_edges(),
    "Network Density":                 round(nx.density(G), 4),
    "Avg Clustering Coefficient":      round(nx.average_clustering(G, weight="weight"), 4),
    "Algebraic Connectivity (λ₂)":     round(lambda2, 4),
    "Avg Shortest Path Length":        round(nx.average_shortest_path_length(G), 4),
    "Diameter":                        nx.diameter(G),
    "Avg Degree":                      round(np.mean([d for _, d in G.degree()]), 2),
    "Avg Intra-group Weight":          round(edges_df[edges_df["type"]=="intra"]["weight"].mean(), 3),
    "Avg Inter-group Weight":          round(edges_df[edges_df["type"]=="inter"]["weight"].mean(), 3),
    "Seed Node (Diffusion)":           top_node,
    "Final Reach (8 steps)":           diff_history[-1],
    "Seed (reproducibility)":          SEED,
}

print("\n" + "="*55)
print("SUMMARY STATISTICS")
print("="*55)
for k, v in summary.items():
    print(f"  {k:<40} {v}")

summary_df = pd.DataFrame(summary.items(), columns=["Metric", "Value"])
summary_df.to_csv(OUTPUT_DIR + "summary_statistics.csv", index=False)
print("\nAll outputs saved to:", OUTPUT_DIR)
