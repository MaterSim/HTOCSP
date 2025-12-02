import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.gridspec as gridspec

plt.rcParams.update({'font.size': 14})

# Pretty names for titles
name_map = {
    "EBDC":  "ZJU-HOF-60",
    "BDDC":  "ZJU-HOF-62",
    "TCF-1": "TCF-1",
    "HOF5a": "HOF-5a",
    "TTBI":  "TTBI",
}

# Systems and corresponding DFS CSV filenames
systems = ["EBDC", "BDDC", "TCF-1", "HOF5a", "TTBI"]
dfs_files = {
    "EBDC":  "EBDC_DFS_openff.csv",
    "BDDC":  "BDDC_DFS_openff.csv",
    "TCF-1": "TCF-1_DFS_gaff.csv",
    "HOF5a": "HOF5a_DFS_gaff.csv",
    "TTBI":  "TTBI_DFS_gaff.csv",
}

# Font sizes
FS_TITLE = 16
FS_AXIS_LABEL = 14
FS_TICKS = 14
FS_LEGEND = 14
FS_COLORBAR = 12
FS_BAR_TEXT = 10

fig = plt.figure(figsize=(20, 12))
gs = gridspec.GridSpec(
    6, 2,
    height_ratios=[2.5, 1.2, 2.5, 1.2, 2.5, 1.2]
)
panel_labels = ["a", "b", "c", "d", "e"]

def get_axes_for_system(idx):
    if idx == 0:      # EBDC
        return fig.add_subplot(gs[0,0]), fig.add_subplot(gs[1,0])
    if idx == 1:      # BDDC
        return fig.add_subplot(gs[0,1]), fig.add_subplot(gs[1,1])
    if idx == 2:      # TCF-1
        return fig.add_subplot(gs[2,0]), fig.add_subplot(gs[3,0])
    if idx == 3:      # HOF5a
        return fig.add_subplot(gs[2,1]), fig.add_subplot(gs[3,1])
    if idx == 4:      # TTBI
        return fig.add_subplot(gs[4, :]), fig.add_subplot(gs[5, :])

# ======================= MAIN LOOP ==========================
for i, sys_name in enumerate(systems):
    scatter_ax, hist_ax = get_axes_for_system(i)

    # ---------- Load DFS data (RAW energy) ----------
    csv_file = dfs_files[sys_name]
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"{sys_name}: CSV not found: {csv_file}")
    print(f"[{sys_name}] Using DFS CSV file: {csv_file}")

    df = pd.read_csv(csv_file)

    # Columns are exactly: id, Density_g_cm3, Space_group, Energy_kJ_mol
    for col in ["Density_g_cm3", "Space_group", "Energy_kJ_mol"]:
        if col not in df.columns:
            raise KeyError(f"{sys_name}: column '{col}' not found in {csv_file}")

    df["Density_g_cm3"] = df["Density_g_cm3"].astype(float)
    df["Space_group"]   = df["Space_group"].astype(int)
    df["Energy_kJ_mol"] = df["Energy_kJ_mol"].astype(float)

    print("Total number of structures:", len(df), sys_name)

    # Convert RAW energy → ΔU (kJ/mol), min = 0
    df["Energy_kJ_mol"] -= df["Energy_kJ_mol"].min()
    df = df.sort_values("Energy_kJ_mol").reset_index(drop=True)

    # ================= TOP: SCATTER =================
    sc = scatter_ax.scatter(
        df["Density_g_cm3"],
        df["Energy_kJ_mol"],
        c=df["Space_group"],
        s=12,
        alpha=0.5,
        cmap="Blues",
    )

    # y-limits (you can tweak these)
    if sys_name == "HOF5a":
        scatter_ax.set_ylim(-5, 250)
    else:
        scatter_ax.set_ylim(-5, 150)
    scatter_ax.set_xlim(0.35, 1.8)

    scatter_ax.set_title(
        f"({panel_labels[i]}) {name_map[sys_name]} ({len(df)})",
        fontsize=FS_TITLE,
    )
    scatter_ax.tick_params(axis="both", which="major", labelsize=FS_TICKS)

    # ---------- Add matched structures (already ΔU) ----------
    if sys_name == "TTBI":
        match_files = [
            "TTBI_Matched_alpha.csv",
            "TTBI_Matched_beta.csv",
            "TTBI_Matched_gamma.csv",
        ]
    elif sys_name == "TCF-1":
        match_files = [
            "TCF-1_Matched_Dense.csv",
            "TCF-1_Matched_Porous.csv",
        ]
    else:
        match_files = [f"{sys_name}_Matched.csv"]

    match_colors = {
        "alpha":  "coral",
        "beta":   "green",
        "gamma":  "red",
        "Dense":  "coral",
        "Porous": "green",
        "Matched":"coral",
    }

    for match_file in match_files:
        if not os.path.exists(match_file):
            print(f"[WARNING] {sys_name}: match file not found: {match_file}")
            continue

        mdf = pd.read_csv(match_file)

        # Columns: id, Density_g_cm3, Space_group, Reletive_Energy_kJ_mol
        for col in ["Density_g_cm3", "Reletive_Energy_kJ_mol"]:
            if col not in mdf.columns:
                raise KeyError(f"{match_file}: missing column '{col}'")

        match_density = mdf["Density_g_cm3"].astype(float).values
        # IMPORTANT: already relative ΔU
        match_energy  = mdf["Reletive_Energy_kJ_mol"].astype(float).values

        match = np.column_stack([match_density, match_energy])
        if match.shape[0] == 0:
            print(f"[INFO] {sys_name}: no matched entries in {match_file}")
            continue

        base   = os.path.splitext(os.path.basename(match_file))[0]
        suffix = base.split("_")[-1]  # 'Matched', 'alpha', 'Dense', etc.

        # label text
        if suffix in ["alpha", "beta", "gamma"]:
            label = f"{suffix} ({match.shape[0]} matches)"
        elif suffix in ["Dense", "Porous"]:
            label = f"{suffix} ({match.shape[0]} matches)"
        else:
            label = f"Exp. ({match.shape[0]} matches)"

        color = match_colors.get(suffix, "coral")

        scatter_ax.scatter(
            match[:, 0],
            match[:, 1],
            marker="*",
            s=100,
            color=color,
            label=label,
        )

    if len(scatter_ax.get_legend_handles_labels()[0]) > 0:
        scatter_ax.legend(loc=3, frameon=False, fontsize=FS_LEGEND, ncol=3)
    if i % 2 == 0:
        scatter_ax.set_ylabel("$\\Delta U$ (kJ/mol)", fontsize=FS_AXIS_LABEL)
    scatter_ax.set_xlabel("Density (g/cm$^3$)", fontsize=FS_AXIS_LABEL)

    # Color bar for TTBI SG
    if sys_name == "TTBI":
        divider_sc = make_axes_locatable(scatter_ax)
        cax_sc = divider_sc.append_axes("right", size="3%", pad=0.05)
        cbar = fig.colorbar(sc, cax=cax_sc, orientation='vertical')
        cbar.set_label('Space group', fontsize=FS_AXIS_LABEL)
        cbar.ax.tick_params(labelsize=FS_TICKS)

    # ================= BOTTOM: SG HISTOGRAM =================
    sg_stats = (
        df.groupby("Space_group")
          .agg({"Energy_kJ_mol": "mean", "Space_group": "count"})
          .rename(columns={"Space_group": "count"})
    )
    existing_sg = sorted(df["Space_group"].unique())

    norm = plt.Normalize(
        sg_stats["Energy_kJ_mol"].min(),
        sg_stats["Energy_kJ_mol"].max(),
    )
    colors = plt.cm.gist_gray(norm(sg_stats.loc[existing_sg, "Energy_kJ_mol"]))
    bar_heights = sg_stats.loc[existing_sg, "count"] * 2

    bars = hist_ax.bar(
        range(1, len(existing_sg) + 1),
        bar_heights,
        color=colors,
        edgecolor="black",
        alpha=0.8,
    )

    hist_ax.spines['top'].set_visible(False)
    hist_ax.spines['right'].set_visible(False)
    hist_ax.set_xticks(range(1, len(existing_sg) + 1))
    hist_ax.set_xticklabels(existing_sg, fontsize=FS_TICKS)
    hist_ax.tick_params(axis="both", which="major", labelsize=FS_TICKS)

    hist_ax.set_yscale("log")
    hist_ax.set_ylim(1, sg_stats["count"].max() * 10)
    hist_ax.set_xlim(0.5, len(existing_sg) + 0.5)

    for j, bar in enumerate(bars):
        height = bar.get_height()
        sg_num = existing_sg[j]
        min_energy = df[df["Space_group"] == sg_num]["Energy_kJ_mol"].min()
        hist_ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{min_energy:.0f}",
            ha="center",
            va="bottom",
            fontsize=FS_BAR_TEXT,
        )

    if i % 2 == 0:
        hist_ax.set_ylabel("Occurrence", fontsize=FS_AXIS_LABEL)

# ======================= SAVE FIGURE ========================
plt.tight_layout()
plt.savefig("Fig3.png", dpi=300)
plt.close()

