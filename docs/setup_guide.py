# Step-by-Step Setup Guide
# Spectral Analysis of Indigenous Social Networks
# ================================================

# ---------------------------------------------------------------
# PHASE 1: LOCAL SETUP IN VS CODE
# ---------------------------------------------------------------

# STEP 1: Install prerequisites (do this once)
# --------------------------------------------
# a) Python 3.10+  →  https://www.python.org/downloads/
# b) Git           →  https://git-scm.com/downloads
# c) VS Code       →  https://code.visualstudio.com/
# d) In VS Code, install extensions (Ctrl+Shift+X):
#      - Python  (Microsoft)
#      - Pylance (Microsoft)
#      - Jupyter (Microsoft)
#      - GitLens
#      - Git Graph
#      - GitHub Pull Requests


# STEP 2: Create and open the project folder
# ------------------------------------------
# Copy the downloaded project folder anywhere on your machine, e.g.:
#   C:\Users\Apurva\Projects\spectral-iks\          (Windows)
#   /Users/apurva/Projects/spectral-iks/             (Mac/Linux)
#
# In VS Code: File → Open Workspace from File →
#             select  spectral-iks.code-workspace


# STEP 3: Create a Python virtual environment
# -------------------------------------------
# Open the VS Code integrated terminal (Ctrl+` or View → Terminal)

# Windows:
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux:
python3 -m venv .venv
source .venv/bin/activate

# You should now see (.venv) at the start of your terminal prompt.


# STEP 4: Install dependencies
# ----------------------------
pip install -r requirements.txt
# This installs: networkx, numpy, pandas, scipy, scikit-learn,
#                matplotlib, plotly, jupyterlab


# STEP 5: Select the Python interpreter in VS Code
# -------------------------------------------------
# Press Ctrl+Shift+P → "Python: Select Interpreter"
# Choose the one that shows .venv in the path


# STEP 6: Run the analysis
# ------------------------
# Option A — from the terminal:
python src/spectral_analysis.py

# Option B — press F5 (uses the launch config in the workspace file)
# Option C — click the ▶ Run button at top-right when spectral_analysis.py
#             is open in the editor


# STEP 7: Verify outputs
# ----------------------
# After running, check these files exist:
#   figures/fig3_spectral_clustering.png
#   figures/fig5_network_overview.png
#   figures/fig6_laplacian_spectrum.png
#   figures/fig8_diffusion_dynamics.png
#   figures/fig9_resilience.png
#   data/nodes.csv
#   data/edges.csv


# ---------------------------------------------------------------
# PHASE 2: CREATE GITHUB REPOSITORY
# ---------------------------------------------------------------

# STEP 8: Create a GitHub account (if you don't have one)
# -------------------------------------------------------
# Go to https://github.com → Sign Up
# Suggested username: apurvamehta-ddu  or  apurvamehta-ce


# STEP 9: Create a new repository on GitHub
# ------------------------------------------
# a) Log in to GitHub
# b) Click the "+" icon (top-right) → "New repository"
# c) Fill in:
#      Repository name:  spectral-iks
#      Description:      Spectral analysis of indigenous social networks
#                        (IJKMS paper prototype)
#      Visibility:       Private  (change to Public when paper is accepted)
#      ✗ Do NOT initialise with README (we already have one)
# d) Click "Create repository"
# e) GitHub will show you a URL like:
#      https://github.com/YOUR_USERNAME/spectral-iks.git
#    Copy this URL.


# STEP 10: Initialise Git in your local project folder
# ----------------------------------------------------
# In the VS Code terminal (make sure you are in the project root):
git init
git add .
git commit -m "Initial commit: principled synthetic network + all analysis figures"


# STEP 11: Connect local repo to GitHub and push
# -----------------------------------------------
# Replace YOUR_USERNAME with your actual GitHub username:
git remote add origin https://github.com/YOUR_USERNAME/spectral-iks.git
git branch -M main
git push -u origin main

# VS Code will pop up a GitHub login window — sign in.
# After this, your code is live on GitHub.


# ---------------------------------------------------------------
# PHASE 3: VERSION CONTROL WORKFLOW (daily use)
# ---------------------------------------------------------------

# Every time you make changes to the code:

# STEP 12: See what changed
git status
git diff src/spectral_analysis.py   # see line-by-line changes

# STEP 13: Stage and commit your changes
git add src/spectral_analysis.py
git commit -m "Describe what you changed, e.g.: Add sensitivity analysis for lambda2"

# STEP 14: Push to GitHub
git push

# That's it. Your changes are now versioned and backed up.


# ---------------------------------------------------------------
# PHASE 4: BRANCHING (for trying new experiments safely)
# ---------------------------------------------------------------

# Create a branch before trying something experimental:
git checkout -b experiment/real-data-test

# Make your changes, run the script, check results.
# If happy: merge back to main
git checkout main
git merge experiment/real-data-test

# If not happy: discard the branch
git checkout main
git branch -D experiment/real-data-test


# ---------------------------------------------------------------
# SUGGESTED BRANCH STRUCTURE FOR THIS PAPER
# ---------------------------------------------------------------
#
#   main                      ← clean, working code always
#   ├── experiment/proxy-dataset    ← Option A (real proxy dataset)
#   ├── experiment/gond-simulation  ← Option B (Gond-specific model)
#   └── revision/ijkms-v1           ← manuscript revision branch
#


# ---------------------------------------------------------------
# USEFUL VS CODE SHORTCUTS
# ---------------------------------------------------------------
#
#   Ctrl+`          Open/close terminal
#   Ctrl+Shift+P    Command palette (search any VS Code action)
#   F5              Run with debugger
#   Ctrl+Shift+G    Open Source Control panel (see all changes visually)
#   Ctrl+Z          Undo (works inside files, not Git commits)
#
# In Source Control panel (Ctrl+Shift+G):
#   Click "+"       Stage a file (like `git add`)
#   Enter message   Type commit message
#   Ctrl+Enter      Commit
#   "..." menu      Push, Pull, Branch operations
