import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def load_ecd_data(filepath):
    """Loads space-separated ECD data, handling decimal and Fortran formats."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' could not be found.")

    data = np.loadtxt(filepath)

    if data.shape[1] < 2:
        raise ValueError(
            f"File '{filepath}' must have at least 2 columns (x, y)."
        )

    wavelength = data[:, 0]
    intensity = data[:, 1]
    return wavelength, intensity

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
expo=0.0
def forward_scaled_format(x,pos):
    scaled_value = x / (10**expo)
    return f"{scaled_value:.2f}"

def plot_ecd_spectra(exp_file, calc_file, ssimil1, calc_file_cluster, ssimil2,isRoa, output_image):
    """Plots experimental and calculated ECD spectra vertically, sharing the X-axis."""
    xlim=[200,2000]
    # Load data
    try:
        x_exp, y_exp = load_ecd_data(exp_file)
        x_calc, y_calc = load_ecd_data(calc_file)
        x_calc_cluster,y_calc_cluster=load_ecd_data(calc_file_cluster)
    except Exception as e:
        print(f"Error loading data: {e}")
        return


    max_val = np.max(np.abs(y_exp))
    # Calculate the base-10 exponent (e.g., 1.5e7 -> 7)
    exponent = int(np.floor(np.log10(max_val)))
    global expo
    expo=exponent
    # Create figure with 2 subplots stacked vertically sharing the X-axis
    fig, (ax1, ax2,ax3) = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(5,5),gridspec_kw={'hspace': 0}
    )

    for ax in [ax1, ax2, ax3]:
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=3, prune="both"))
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(forward_scaled_format))
        
    
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
    ax1.text(
        -0.08,
        1.02,
        f"$\\mathregular{{\\times 10^{exponent}}}$",
        transform=ax1.transAxes,
        fontsize=10,
        va="bottom",
        ha="left"
    )
    
    
    ssimil_xpos=0.975
    ssimil_ypos=0.78
    ax2.plot(
        x_calc, y_calc, color="blue", linestyle="-", linewidth=1.5, label="CPCM"
    )
    ax2.legend(loc="upper right",fontsize=9,frameon=False)
    ax2.xaxis.grid(True, linestyle="-", alpha=0.6)
    ax2.set_xlim(xlim[0], xlim[1])
    set_dynamic_ylim(ax2,x_calc,y_calc,xlim[0],xlim[1],isRoa)
    ax2.text(
        ssimil_xpos,
        ssimil_ypos,  # X and Y coordinates (95% right, 90% up within the box)
        ssimil1,
        transform=ax2.transAxes,  # Use axis coordinates, not data coordinates
        fontsize=9,
        horizontalalignment="right",  # Anchors the text from its right edge
        verticalalignment="top",  # Anchors the text from its top edge
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0.7)
    )
    
    
    ax3.plot(
        x_calc_cluster, y_calc_cluster, color="red", linestyle="-", linewidth=1.5, label="CPCM + clusters"
    )
    ax3.set_xlabel("Wavenumber ($\mathrm{cm^{-1}}$)")
    ax3.legend(loc="upper right",fontsize=9,frameon=False)
    ax3.xaxis.grid(True, linestyle="-", alpha=0.6)
    ax3.set_xlim(xlim[0], xlim[1])
    set_dynamic_ylim(ax3,x_calc_cluster,y_calc_cluster,xlim[0],xlim[1],isRoa)
    ax3.text(
        ssimil_xpos,
        ssimil_ypos,  # X and Y coordinates (95% right, 90% up within the box)
        ssimil2,
        transform=ax3.transAxes,  # Use axis coordinates, not data coordinates
        fontsize=9,
        horizontalalignment="right",  # Anchors the text from its right edge
        verticalalignment="top",  # Anchors the text from its top edge
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0.7)
    )
    all_axes=[ax1,ax2,ax3]
    for ax in all_axes:
        if(isRoa):
            ax.set_ylabel(r"$\mathit{\Delta I}$ (arb. u.)")
        else:
            ax.set_ylabel(r"$\mathit{I}$ (arb. u.)")
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(3))
        ax.xaxis.grid(True, which="both", linestyle="-", alpha=0.3, color="gray")
    
    fig.canvas.draw()  

    ax2.yaxis.get_offset_text().set_visible(False)
    ax3.yaxis.get_offset_text().set_visible(False)

    plt.subplots_adjust(top=0.93, bottom=0.12, left=0.18, right=0.95)
    plt.savefig(output_image, dpi=300, format="png")
    print(f"Successfully generated plot: {output_image}")
    plt.close()


if __name__ == "__main__":
    # Define your file paths here
    
    OUTPUT_FILE = "raman.png"
    argc=len(sys.argv)-1
    EXPERIMENTAL_FILE = sys.argv[1]
    CALCULATED_FILE = sys.argv[2]
    SSIMIL1=(sys.argv[3])
    CALCULATED_CLUSTER_FILE=sys.argv[4]
    SSIMIL2=(sys.argv[5])
    isROA=(sys.argv[6])
    if(isROA[0].lower()=='t'):
        isROA=True
    else:
        isROA=False
    print("ROA: "+str(isROA))
    
    plot_ecd_spectra(EXPERIMENTAL_FILE, CALCULATED_FILE, SSIMIL1, CALCULATED_CLUSTER_FILE, SSIMIL2, isROA, OUTPUT_FILE)
    

    