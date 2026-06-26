import re
import sys
import matplotlib
matplotlib.use('WebAgg')
import matplotlib.pyplot as plt

def parse_orca_orbitals(file_path):
    """
    Parses an ORCA output file to extract the ground state energy 
    and TD-DFT excitation energies at each geometry optimization cycle.
    """
    # Conversion factor from Hartree (Eh) to cm^-1
    AU_TO_CM = 219474.63
    
    steps = []
    current_step = None
    
    # Regular expressions to locate data blocks
    cycle_re = re.compile(r"GEOMETRY OPTIMIZATION CYCLE\s+(\d+)")
    scf_energy_re = re.compile(r"Total Energy\s*:\s*([\d\-\.]+)\s*Eh")
    
    # Flags and storage for tracking the absorption table inside each cycle
    in_table = False
    table_lines_left = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            # Detect a new geometry cycle
            cycle_match = cycle_re.search(line)
            if cycle_match:
                if current_step is not None:
                    steps.append(current_step)
                current_step = {
                    'cycle': int(cycle_match.group(1)),
                    'e_ground': None,
                    'e_excited': []
                }
                in_table = False
                continue
            
            if current_step is None:
                continue
                
            # Capture the ground state energy (the last one in the cycle matches the step)
            scf_match = scf_energy_re.search(line)
            if scf_match:
                current_step['e_ground'] = float(scf_match.group(1))
                continue
                
            # Parse the Absorption Spectrum table to extract the roots accurately
            if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in line:
                in_table = True
                table_lines_left = 4 # Skip headers
                current_step['e_excited'] = []
                continue
                
            if in_table:
                if table_lines_left > 0:
                    table_lines_left -= 1
                else:
                    # End of table is marked by a horizontal line of dashes
                    if "------" in line or line.strip() == "":
                        in_table = False
                    else:
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                # Column index 4 contains the energy in cm-1
                                energy_cm = float(parts[4])
                                current_step['e_excited'].append(energy_cm)
                            except ValueError:
                                pass

        # Append the final cycle tracked
        if current_step is not None:
            steps.append(current_step)
            
    # Filter out steps that are incomplete or lack TD-DFT roots
    steps = [step for step in steps if step['e_ground'] is not None and step['e_excited']]
    
    if not steps:
        raise ValueError("No complete geometry cycles with TD-DFT roots found in the file.")
        
    # Apply reference shifting (Set Ground State of Cycle 1 to 0 cm^-1)
    e_ref_hartree = steps[0]['e_ground']
    
    cycles = []
    g_energies = []
    ex_energies = {i: [] for i in range(len(steps[0]['e_excited']))}
    
    for s in steps:
        cycles.append(s['cycle'])
        # Relative ground state energy in cm^-1
        rel_g = (s['e_ground'] - e_ref_hartree) * AU_TO_CM
        g_energies.append(rel_g)
        
        # Absolute excited state energy = relative ground state + vertical excitation energy
        for idx, ex_energy in enumerate(s['e_excited']):
            if idx in ex_energies:
                ex_energies[idx].append(rel_g + ex_energy)
                
    return cycles, g_energies, ex_energies

def plot_energies(cycles, g_energies, ex_energies):
    """
    Plots the ground and excited state potential energy profiles.
    """
    plt.figure(figsize=(9, 6))
    
    # Plot Ground State
    plt.plot(cycles, g_energies, marker='o', linestyle='-', color='black', 
             linewidth=2, markersize=6, label='Ground State ($S_0$)')
    
    # Plot Excited States
    for root_idx, energies in ex_energies.items():
        plt.plot(cycles, energies, marker='s', linestyle='--', 
                 linewidth=1.5, markersize=5, label=f'Root {root_idx + 1}')
        
    plt.title('Potential Energy Surface along Geometry Optimization', fontsize=14, fontweight='bold')
    plt.xlabel('Geometry Optimization Cycle', fontsize=12)
    plt.ylabel('Relative Energy (cm$^{-1}$)', fontsize=12)
    
    # Force integer labels on X-axis for steps
    plt.gca().xaxis.get_major_locator().set_params(integer=True)
    
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=10)
    plt.tight_layout()
    plt.show()
    # plt.savefig("excopt.png", dpi=300, format="png")
    # print(f"Successfully generated stacked plot: excopt.png")
    # plt.close()

if __name__ == "__main__":
    # Replace with the path to your file if running locally
    file_name = sys.argv[1] 
    
    #try:
    x_cycles, ground_y, excited_y_dict = parse_orca_orbitals(file_name)
    plot_energies(x_cycles, ground_y, excited_y_dict)
    #except Exception as e:
    #    print(f"Error: {e}")