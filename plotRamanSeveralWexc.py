import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
import numpy as np


def load_spectrum_data(filepath):
    """Loads space-separated spectral data, handling standard/Fortran formats."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: '{filepath}'")
    data = np.loadtxt(filepath)
    return data[:, 0], data[:, 1]

def set_dynamic_ylim(ax, x, y, x_min, x_max, isRoa=False, pad=0.025):
    
    """
    Sets y-limits based only on data within the visible x-range [x_min, x_max].
    pad: Fraction of the range to add as whitespace (default 10%).
    """
    # Create a mask for data within the visible x-range
    mask = (x >= x_min) & (x <= x_max)
    y_visible = y[mask]
    
    if y_visible.size > 0:
        y_min, y_max = np.min(y_visible), np.max(y_visible)
        if(isRoa):
            vall=max(abs(y_min),abs(y_max))
            y_min=-vall
            y_max=vall
        # Add padding so the peaks don't touch the top/bottom frame
        y_range = y_max - y_min
        ax.set_ylim(y_min - pad * y_range, y_max + pad * y_range)

def plot_multi_excitation_spectra(
    exp_file, calc_files_dict, output_image="multi_spectra_stack.png",xlim=[200,2000],isRoa=False
):
    """Plots experimental spectrum on top, and an arbitrary number of calculated

    spectra stacked below it with uniform formatting and zero vertical gap.

    Parameters:
    - exp_file: Path to experimental data file.
    - calc_files_dict: Dict of {"Label/Wavelength": "path_to_file.txt"}
    """
    # 1. Load Experimental Data
    try:
        x_exp, y_exp = load_spectrum_data(exp_file)
    except Exception as e:
        print(f"Error loading experimental file: {e}")
        return
    cmap = mpl.colormaps.get_cmap("tab10")
    # Count how many total subplots we need (1 experimental + N calculated)
    num_calc = len(calc_files_dict)
    total_plots = 1 + num_calc

    # Dynamically scale the figure height based on the number of files
    # 5 inches wide, 2 inches of height per stacked spectrum feels balanced
    fig_height = 1*num_calc

    fig, axes = plt.subplots(
        nrows=total_plots,
        ncols=1,
        sharex=True,
        figsize=(5.5, fig_height),
        gridspec_kw={"hspace": 0},
    )

    # Ensure axes is always iterable (even if only 1 calc file was passed)
    if total_plots == 1:
        axes = [axes]

    # --- STEP 2: Determine global scientific notation exponent from Experimental ---
    max_val = np.max(np.abs(y_exp))
    exponent = int(np.floor(np.log10(max_val)))

    # Formatting function for uniform 1-decimal place mapping
    def forward_scaled_format(x, pos):
        scaled_value = x / (10**exponent)
        return f"{scaled_value:.1f}"

    # --- STEP 3: Plot Experimental (Top Graph) ---
    ax_top = axes[0]
    ax_top.plot(
        x_exp, y_exp, color="black", linestyle="-", linewidth=1.2, label="Exp"
    )
    # if(isRoa):
    #     ax_top.set_ylabel(r"$\mathit{\Delta I}$ (arb. u.)")
    # else:
    #     ax_top.set_ylabel(r"$\mathit{I}$ (arb. u.)")

    #ax_top.set_ylabel(r"$\mathit{I}$ (arb. u.)", style="italic")
    ax_top.legend(loc="upper right", fontsize=9, frameon=False)
    set_dynamic_ylim(ax_top,x_exp,y_exp,xlim[0],xlim[1],isRoa)
    # Manually place the single global scale multiplier at the top-left
    # ax_top.text(
    #     -0.08,
    #     1.02,
    #     f"$\mathregular{{\\times 10^{exponent}}}$",
    #     transform=ax_top.transAxes,
    #     fontsize=10,
    #     va="bottom",
    #     ha="left",
    # )

    # --- STEP 4: Loop and Plot Calculated Wave-lengths ---
    for i, (label, filepath) in enumerate(calc_files_dict.items()):
        ax = axes[i + 1]  # Start at index 1, right under experimental

        try:
            x_calc, y_calc = load_spectrum_data(filepath)
        except Exception as e:
            print(f"Skipping {label}, error loading file: {e}")
            continue
        # if(isRoa):
        #     ax.set_ylabel(r"$\mathit{\Delta I}$ (arb. u.)")
        # else:
        #     ax.set_ylabel(r"$\mathit{I}$ (arb. u.)")

        # Plot with a cycling or standard color (using blue here as a default base)
        ax.plot(
            x_calc,
            y_calc,
            color=cmap(i),
            linestyle="-",
            linewidth=1.2,
            label=label,
        )
        # ax.set_ylabel(r"$\mathit{I}$ (arb. u.)", style="italic")
        ax.legend(loc="upper right", fontsize=9, frameon=False)
        set_dynamic_ylim(ax,x_calc,y_calc,xlim[0],xlim[1],isRoa)

    # --- STEP 5: Apply Unified Formatting across ALL subplots ---
    for ax in axes:
        
        # Fewer numbers on Y axis to maintain clean whitespace
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=2, prune="both"))
       # ax.yaxis.set_major_formatter(ticker.FuncFormatter(forward_scaled_format))

        # Add dense X grid lines, turn off Y grid lines completely
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
        ax.xaxis.grid(True, which="both", linestyle=":", alpha=0.25, color="gray")
        ax.yaxis.grid(False)

    # Set bottom-most X-axis label and range constraints
    ax_bottom = axes[-1]
    ax_bottom.set_xlabel("Wavenumber ($\mathrm{cm}^{-1}$)")
    ax_bottom.set_xlim(150, 2000)  # Adjust to your physical range constraints

    # Optimize edge limits tightly
    plt.subplots_adjust(top=0.93, bottom=0.12, left=0.18, right=0.95)

    # Save to high-quality compressed PNG
    plt.savefig(output_image, dpi=300, format="png")
    print(f"Successfully generated stacked plot: {output_image}")
    plt.close()


if __name__ == "__main__":
    # Path to your experimental spectrum
    argc=len(sys.argv)
    EXP_DATA = sys.argv[1]

    # Define your calculated spectra filenames dynamically in a dictionary.
    # The key will automatically serve as the legend string.
    isROA=(sys.argv[2])
    if(isROA[0].lower()=='t'):
        isROA=True
    else:
        isROA=False
    print("ROA: "+str(isROA))
    CALCULATED_DATASETS = {}
    for i in range(3,argc,2):
        CALCULATED_DATASETS[sys.argv[i]]=sys.argv[i+1]
    
    # CALCULATED_DATASETS = {
    #     "Excitation: 355 nm": "calc_355nm.txt",
    #     "Excitation: 432 nm": "calc_432nm.txt",
    #     "Excitation: 532 nm": "calc_532nm.txt",
    #     "Excitation: 633 nm": "calc_633nm.txt",
    # }

    output='raman_wexc_stacked.png'
    xlim=[200,2000]
    # Run execution
    plot_multi_excitation_spectra(EXP_DATA, CALCULATED_DATASETS,output,xlim,isROA)