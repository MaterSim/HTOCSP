# Fig. 2 (CSV-based)
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 14})  # Set the default font size for all plots

# Mapping from system folder/key -> nice name
system_pretty = {
    'BDDC':  'ZJU-HOF-62',
    'EBDC':  'ZJU-HOF-60',
    'TCF':   'TCF-1',
    'TTBI':  'TTBI',
    'HOF5a': 'HOF-5a',
}

# DFS CSV filenames for each system (in the current directory)
dfs_files = {
    'BDDC':  'BDDC_DFS_gaff.csv',
    'EBDC':  'EBDC_DFS_gaff.csv',
    'TCF':   'TCF-1_DFS_gaff.csv',
    'TTBI':  'TTBI_DFS_gaff.csv',
    'HOF5a': 'HOF5a_DFS_gaff.csv',
}

Ecut = 200.0  # (not used directly here but you can use for filters if needed)

fig = plt.figure(figsize=(18, 8))
gs = fig.add_gridspec(2, 3)
axs = [
    fig.add_subplot(gs[0, 0]),   # index 0
    fig.add_subplot(gs[0, 1]),   # index 1
    fig.add_subplot(gs[1, 0]),   # index 2
    fig.add_subplot(gs[1, 1]),   # index 3
    fig.add_subplot(gs[:, 2]),   # index 4 (HOF5a spans both rows, 3rd column)
]

panel_labels = ["a", "b", "c", "d", "e"]

# Order of systems to plot (must match axs indexing)
systems = ['BDDC', 'EBDC', 'TCF', 'TTBI', 'HOF5a']

for i, sys_name in enumerate(systems):
    ax = axs[i]

    # ---------- Load DFS data (RAW energy in kJ/mol) ----------
    dfs_csv = dfs_files[sys_name]
    if not os.path.exists(dfs_csv):
        raise FileNotFoundError(f"{sys_name}: DFS CSV not found: {dfs_csv}")

    df = pd.read_csv(dfs_csv)

    # Expecting columns: id, Density_g_cm3, Space_group, Energy_kJ_mol
    for col in ["Density_g_cm3", "Space_group", "Energy_kJ_mol"]:
        if col not in df.columns:
            raise KeyError(f"{sys_name}: column '{col}' not in {dfs_csv}")

    df["Density_g_cm3"] = df["Density_g_cm3"].astype(float)
    df["Space_group"]   = df["Space_group"].astype(int)
    df["Energy_kJ_mol"] = df["Energy_kJ_mol"].astype(float)

    # Convert raw energy → ΔU = E - E_min
    df["Energy_kJ_mol"] -= df["Energy_kJ_mol"].min()
    df = df.sort_values("Energy_kJ_mol").reset_index(drop=True)

    # ---------- Base scatter (DFS search) ----------
    ax.scatter(
        df["Density_g_cm3"],
        df["Energy_kJ_mol"],
        s=10,
        alpha=0.5,
    )

    ax.set_xlabel('Density (g/cm$^3$)')
    ax.set_ylabel('$\\Delta U$ (kJ/mol)')

    if sys_name == 'HOF5a':
        ax.set_ylim(-20, 250)
    else:
        ax.set_ylim(-20, 150)

    ax.set_xlim(0.25, 1.8)

    ax.set_title(f'({panel_labels[i]}) {system_pretty[sys_name]} ({len(df)})')

    # ---------- Matched structures (already relative ΔU) ----------
    if sys_name == 'TTBI':
        match_files = [
            "TTBI_Matched_alpha.csv",
            "TTBI_Matched_beta.csv",
            "TTBI_Matched_gamma.csv",
        ]
    elif sys_name == 'TCF':
        match_files = [
            "TCF-1_Matched_Dense.csv",
            "TCF-1_Matched_Porous.csv",
        ]
    else:
        match_files = [f"{sys_name}_Matched.csv"]

    # Colors for different matched sets
    match_colors = {
        "alpha":   "coral",
        "beta":    "green",
        "gamma":   "red",
        "Dense":   "coral",
        "Porous":  "green",
        "Matched": "coral",
    }

    for match_file in match_files:
        if not os.path.exists(match_file):
            print(f"[WARNING] {sys_name}: matched CSV not found: {match_file}")
            continue

        mdf = pd.read_csv(match_file)

        # Expect columns: id,Density_g_cm3,Space_group,Reletive_Energy_kJ_mol
        for col in ["Density_g_cm3", "Reletive_Energy_kJ_mol"]:
            if col not in mdf.columns:
                raise KeyError(f"{match_file}: missing column '{col}'")

        match_density = mdf["Density_g_cm3"].astype(float).values
        # Already ΔU (relative energies)
        match_energy  = mdf["Reletive_Energy_kJ_mol"].astype(float).values

        match = np.column_stack([match_density, match_energy])
        if match.shape[0] == 0:
            print(f"[INFO] {sys_name}: no rows in {match_file}")
            continue

        base = os.path.splitext(os.path.basename(match_file))[0]
        suffix = base.split("_")[-1]  # 'Matched', 'alpha', 'Dense', etc.

        # Legend labels similar to your old style
        if suffix in ['alpha', 'beta', 'gamma']:
            label = f"{suffix} ({match.shape[0]} matches)"
        elif suffix in ['Dense', 'Porous', 'dense', 'porous']:
            label = f"{suffix} ({match.shape[0]} matches)"
        else:
            # e.g. BDDC_Matched.csv, EBDC_Matched.csv, HOF5a_Matched.csv
            label = f"Exp. ({match.shape[0]} matches)"

        color = match_colors.get(suffix, "coral")

        ax.scatter(
            match[:, 0],
            match[:, 1],
            marker='*',
            s=100,
            color=color,
            label=label,
        )

    if len(ax.get_legend_handles_labels()[0]) > 0:
        ax.legend(loc=3, frameon=False)

plt.tight_layout()
plt.savefig('Fig2.png', dpi=300)
plt.close()

