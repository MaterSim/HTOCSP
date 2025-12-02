import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.gridspec as gridspec

FACTOR = 96.485  # eV/mol -> kJ/mol
method_order = ["MACE", "MACEOFF", "UMA", "DFT", "LATTE"]

# ---------- data loading ----------

def load_system_df(system_name):
    """
    Read <system_name>.csv and compute Delta_kJ_per_mol per method.
    """
    df = pd.read_csv(f"{system_name}.csv")

    # --- 1) Ensure Energy_kJ_per_mol is filled correctly ---
    if "Energy_kJ_per_mol" not in df.columns:
        # no kJ column at all: build it from eV
        if "Energy_eV_per_mol" in df.columns:
            df["Energy_kJ_per_mol"] = df["Energy_eV_per_mol"] * FACTOR
        else:
            raise ValueError(f"{system_name}.csv has no energy columns")
    else:
        # column exists, but maybe has NaNs (e.g. LATTE rows) → fix only those
        if df["Energy_kJ_per_mol"].isna().any() and "Energy_eV_per_mol" in df.columns:
            mask_nan = df["Energy_kJ_per_mol"].isna()
            df.loc[mask_nan, "Energy_kJ_per_mol"] = (
                df.loc[mask_nan, "Energy_eV_per_mol"] * FACTOR
            )

    # --- 2) Compute ΔU (kJ/mol) relative to minimum within each method ---
    df["Delta_kJ_per_mol"] = np.nan
    for meth in method_order:
        mask = df["Method"] == meth
        if mask.any():
            Emin = df.loc[mask, "Energy_kJ_per_mol"].min()
            df.loc[mask, "Delta_kJ_per_mol"] = (
                df.loc[mask, "Energy_kJ_per_mol"] - Emin
            )

    # --- 3) Method ordering & sorting ---
    df["Method"] = pd.Categorical(df["Method"],
                                  categories=method_order,
                                  ordered=True)
    df.sort_values(["Label", "Method"], inplace=True)

    return df

system_list = ["EBDC", "BDDC", "TCF-1", "TTBI", "HOF5a"]
names = ["ZJU-HOF-60", "ZJU-HOF-62", "TCF-1", "TTBI", "HOF-5a"]
system_dfs = {name: load_system_df(name) for name in system_list}

# ---------- style dictionaries ----------
generic_colors = {
    "Experimental":   "lightgrey",
    "Matched":        "blue",
    "Local Minimum":  "olive",
    "Global Minimum": "cadetblue",
}
generic_label_short = {
    "Experimental": "Exp.",
    "Matched": "Match",
    "Local Minimum": "Local",
    "Global Minimum": "Global",
}
tcf_colors = {
    "dense_Experimental":   "lightgrey",
    "Matched_dense":        "blue",
    "porous_Experimental":  "lightgrey",
    "Matched_porous":       "coral",
    "Global Minimum":       "cadetblue",
}
tcf_label_short = {
    "dense_Experimental":   "Dense",
    "Matched_dense":        "D-match",
    "porous_Experimental":  "Porous",
    "Matched_porous":       "P-match",
    "Global Minimum":       "Global",
}
ttbi_colors = {
    "Alpha_Experimental":   "lightgrey",
    "Alpha_Matched":        "blue",
    "Beta_Experimental":    "lightgrey",
    "Beta_Matched":         "coral",
    "Gamma_Experimental":   "lightgrey",
    "Gamma_Matched":        "red",
    "Local Minimum":        "olive",
    "Global Minimum":       "cadetblue",
}
ttbi_label_short = {
    "Alpha_Experimental":   "α",
    "Alpha_Matched":        "α_match",
    "Beta_Experimental":    "β",
    "Beta_Matched":         "β_match",
    "Gamma_Experimental":   "γ",
    "Gamma_Matched":        "γ_match",
    "Local Minimum":        "Local",
    "Global Minimum":       "Global",
}
style_by_system = {
    "TTBI":  (ttbi_colors, ttbi_label_short),
    "TCF-1": (tcf_colors,  tcf_label_short),
    # all others use generic
}
# ---------- plotting ----------
def plot_system(ax, label, system_name, df):
    # pick color/label maps
    colors, label_short = style_by_system.get(
        system_name,
        (generic_colors, generic_label_short),
    )
    # legend
    legend_elements = []
    for lbl, color in colors.items():
        if lbl in label_short:  # ensure a text label exists
            legend_elements.append(
                Line2D([0], [0], color=color, lw=3, label=label_short[lbl])
            )
    if system_name == 'EBDC':
        keep_order = ["Experimental", "Matched", "Global Minimum"]
        legend_elements = [
            Line2D([0], [0], color=colors[lbl], lw=3, label=label_short[lbl])
            for lbl in keep_order
            if lbl in colors and lbl in label_short
        ]
    ax.legend(
        handles=legend_elements,
        fontsize=13,
        loc=1,
        frameon=False,
    )
    

    xpos = np.arange(len(method_order))
    half_cap = 0.3
    line_alpha = 0.45
    cap_lw = 2
    connect_lw = 0.9

    method_to_index = {m: i for i, m in enumerate(method_order)}

    # label order
    label_order = []
    for m in method_order:
        for lbl in df[df["Method"] == m]["Label"]:
            if lbl not in label_order:
                label_order.append(lbl)

    for lbl in label_order:
        c = colors.get(lbl, "black")
        xs, ys = [], []

        for meth in method_order:
            i = method_to_index[meth]
            row = df[(df["Label"] == lbl) & (df["Method"] == meth)]
            if len(row) == 1:
                y = float(row["Delta_kJ_per_mol"].values[0])
                # cap
                ax.hlines(y, xpos[i] - half_cap, xpos[i] + half_cap,
                          color=c, lw=cap_lw, zorder=3)
                xs.append(xpos[i])
                ys.append(y)

            else:
                xs.append(None)
                ys.append(None)

        # dashed connectors
        prev = None
        for x, y in zip(xs, ys):
            if (prev is not None) and (x is not None) and (y is not None):
                ax.plot([prev[0], x], [prev[1], y],
                        linestyle="--", lw=connect_lw,
                        color=c, alpha=line_alpha, zorder=2)
            if (x is not None) and (y is not None):
                prev = (x, y)
            else:
                prev = None

    # cosmetics
    ax.set_xticks(xpos)
    ax.set_title(label, fontsize=12)
    
    ax.set_xlim(-0.5, len(method_order) + 0.8)
    '''
    if system_name in ["BDDC", "EBDC"]:
        ax.set_ylim(-3, 40)
    '''
    if system_name == 'HOF5a':
        ax.set_xticklabels(method_order, fontsize=12)
        #ax.tick_params(axis='y', labelsize=11)
    else:
        ax.set_xticklabels([])
        ax.tick_params(axis='y', labelsize=13)

# ---------- combined figure layout ----------
fig = plt.figure(figsize=(7.5, 11))
outer_gs = gridspec.GridSpec(5, 1, figure=fig, height_ratios=[0.7, 0.7, 0.8, 1.3, 0.8])

axes_map = {}
axes_map["BDDC"] = fig.add_subplot(outer_gs[1, 0])
axes_map["EBDC"] = fig.add_subplot(outer_gs[0, 0])
axes_map["TCF-1"] = fig.add_subplot(outer_gs[2, 0])
axes_map["TTBI"] = fig.add_subplot(outer_gs[3, 0])
axes_map["HOF5a"] = fig.add_subplot(outer_gs[4, 0])

for sys_name, n, label in zip(system_list, names, ["(a)", "(b)", "(c)", "(d)", "(e)"]):
    ax = axes_map[sys_name]
    plot_system(ax, label + " " + n, sys_name, system_dfs[sys_name])

fig.text(0.04, 0.5, "ΔU (kJ/mol)", va="center",
         rotation="vertical", fontsize=12)

plt.tight_layout(rect=[0.06, 0.04, 1, 1])
plt.savefig("Fig4.png", dpi=300)
#plt.show()

