import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def load_ecd_data(filepath):
    """Loads space-separated ECD data, handling decimal and Fortran formats."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' could not be found.")

    # np.loadtxt automatically handles space/whitespace separation
    # and parses standard scientific notation (e.g., 1.23e-4 or 1.23E-04)
    data = np.loadtxt(filepath)

    if data.shape[1] < 2:
        raise ValueError(
            f"File '{filepath}' must have at least 2 columns (x, y)."
        )

    wavelength = data[:, 0]
    intensity = data[:, 1]
    return wavelength, intensity

def set_dynamic_ylim(ax, x, y, x_min, x_max, pad=0.1):
    """
    Sets y-limits based only on data within the visible x-range [x_min, x_max].
    pad: Fraction of the range to add as whitespace (default 10%).
    """
    # Create a mask for data within the visible x-range
    mask = (x >= x_min) & (x <= x_max)
    y_visible = y[mask]
    
    if y_visible.size > 0:
        y_min, y_max = np.min(y_visible), np.max(y_visible)
        # Add padding so the peaks don't touch the top/bottom frame
        y_range = y_max - y_min
        ax.set_ylim(y_min - pad * y_range, y_max + pad * y_range)


def plot_ecd_spectra(exp_file, calc_file, calc_file_cluster, output_image="ecd_spectra.png",xlim=[150,2000]):
    """Plots experimental and calculated ECD spectra vertically, sharing the X-axis."""
    # Load data
    try:
        x_exp, y_exp = load_ecd_data(exp_file)
        x_calc, y_calc = load_ecd_data(calc_file)
        x_calc_cluster,y_calc_cluster=load_ecd_data(calc_file_cluster)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Create figure with 2 subplots stacked vertically sharing the X-axis
    fig, (ax1, ax2,ax3) = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(5,5),gridspec_kw={'hspace': 0}
    )

    # 1. Top Plot: Experimental Data
    ax1.plot(
        x_exp,
        y_exp,
        color="black",
        linestyle="-",
        linewidth=1.5,
        label="Experimental",
    )
    ax1.legend(loc="upper right",fontsize=9,frameon=False)
    ax1.xaxis.grid(True, linestyle="-", alpha=0.6)
    ax1.set_xlim(xlim[0], xlim[1])
    set_dynamic_ylim(ax1,x_exp,y_exp,xlim[0],xlim[1])
    
    # 2. Bottom Plot: Calculated Data
    ax2.plot(
        x_calc, y_calc, color="blue", linestyle="-", linewidth=1.5, label="CPCM"
    )
    ax2.legend(loc="upper right",fontsize=9,frameon=False)
    ax2.xaxis.grid(True, linestyle="-", alpha=0.6)
    ax2.set_xlim(xlim[0], xlim[1])
    set_dynamic_ylim(ax2,x_calc,y_calc,xlim[0],xlim[1])
    
    ax3.plot(
        x_calc_cluster, y_calc_cluster, color="red", linestyle="-", linewidth=1.5, label="CPCM + clusters"
    )
    ax3.set_xlabel("Wavenumber ($\mathrm{cm^{-1}}$)")
    ax3.legend(loc="upper right",fontsize=9,frameon=False)
    ax3.xaxis.grid(True, linestyle="-", alpha=0.6)
    ax3.set_xlim(xlim[0], xlim[1])
    set_dynamic_ylim(ax3,x_calc_cluster,y_calc_cluster,xlim[0],xlim[1])
    
    all_axes=[ax1,ax2,ax3]
    for ax in all_axes:
        #ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(0))
        ax.set_ylabel(r"$\mathit{\Delta I}$ (arb. u.)")
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(3))
        ax.xaxis.grid(True, which="both", linestyle="-", alpha=0.3, color="gray")
    
    # Clean up layout overlap
    plt.tight_layout()

    # Save to high-quality lossless PNG
    plt.savefig(output_image, dpi=300, format="png")
    print(f"Successfully generated plot: {output_image}")
    plt.close()


if __name__ == "__main__":
    # Define your file paths here
    
    OUTPUT_FILE = "raman.png"
    argc=len(sys.argv)-1
    EXPERIMENTAL_FILE = sys.argv[1]
    CALCULATED_FILE = sys.argv[2]
    CALCULATED_CLUSTER_FILE=sys.argv[3]
    
    if(argc>=4):
        XLIM = sys.argv[4].split(',')
        # Execute the plotting function
        plot_ecd_spectra(EXPERIMENTAL_FILE, CALCULATED_FILE, CALCULATED_CLUSTER_FILE, OUTPUT_FILE,XLIM)
    else:    
        plot_ecd_spectra(EXPERIMENTAL_FILE, CALCULATED_FILE, CALCULATED_CLUSTER_FILE, OUTPUT_FILE)
    

    