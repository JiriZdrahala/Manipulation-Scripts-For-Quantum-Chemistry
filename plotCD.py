import os
import sys
import matplotlib.pyplot as plt
import numpy as np


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


def plot_ecd_spectra(exp_file, calc_file, output_image="ecd_spectra.png",xlim=[300,800]):
    """Plots experimental and calculated ECD spectra vertically, sharing the X-axis."""
    # Load data
    try:
        x_exp, y_exp = load_ecd_data(exp_file)
        x_calc, y_calc = load_ecd_data(calc_file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Create figure with 2 subplots stacked vertically sharing the X-axis
    fig, (ax1, ax2) = plt.subplots(
        nrows=2, ncols=1, sharex=True, figsize=(5,5),gridspec_kw={'hspace': 0}
    )

    # 1. Top Plot: Experimental Data
    ax1.plot(
        x_exp,
        y_exp,
        color="black",
        linestyle="--",
        linewidth=1.5,
        label="Experimental",
    )
    ax1.set_ylabel(r"$\Delta\epsilon$ ($\mathregular{L\cdot mol^{-1}\cdot cm^{-1}}$)")
    ax1.legend(loc="upper right",fontsize=9,frameon=False)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.set_xlim(xlim[0], xlim[1])
    
    # 2. Bottom Plot: Calculated Data
    ax2.plot(
        x_calc, y_calc, color="red", linestyle="-", linewidth=1.5, label="Calculated"
    )
    ax2.set_xlabel("Wavelength (nm)")
    ax2.set_ylabel(r"$\Delta\epsilon$ ($\mathregular{L\cdot mol^{-1}\cdot cm^{-1}}$)")
    ax2.legend(loc="upper right",fontsize=9,frameon=False)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.set_xlim(xlim[0], xlim[1])
    # Clean up layout overlap
    plt.tight_layout()

    # Save to high-quality lossless PNG
    plt.savefig(output_image, dpi=300, format="png")
    print(f"Successfully generated plot: {output_image}")
    plt.close()


if __name__ == "__main__":
    # Define your file paths here
    
    OUTPUT_FILE = "ECD.png"
    argc=len(sys.argv)-1
    EXPERIMENTAL_FILE = sys.argv[1]
    CALCULATED_FILE = sys.argv[2]
    
    if(argc>=3):
        XLIM = sys.argv[3].split(',')
        # Execute the plotting function
        plot_ecd_spectra(EXPERIMENTAL_FILE, CALCULATED_FILE, OUTPUT_FILE,XLIM)
    else:    
        plot_ecd_spectra(EXPERIMENTAL_FILE, CALCULATED_FILE, OUTPUT_FILE)
    

    