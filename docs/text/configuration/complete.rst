Complete TOML example
=====================

Here we use as an example one of the configuration files used in the tests
(see `input.toml <https://github.com/cssr-tools/pofff/blob/main/examples/input.toml>`_).
The first input parameter is:

.. code-block:: python
    :linenos:

    # Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
    flow = "flow --newton-min-iterations=1 --enable-tuning=true --enable-opm-rst-file=true"
    
If **flow** is not in your path, then write the full path to the executable, as well as adding mpirun
if this is supported in your machine (e.g., flow = "mpirun -np 8 /Users/dmar/Github/opm/build/opm-simulators/bin/flow \-\-newton-min-iterations=1").

The next entries define the following parameters:

.. code-block:: python
    :linenos:
    :lineno-start: 4

    # Set the model parameters
    grid="corner-point" # Type of grid (cartesian, tensor, or corner-point)
    thickness="final" # Thickness maps (measured 'initial', 'final', or a real positive value)
    mult_thickness=1 # Thickness multiplier (a real positive value)
    x=[140] # If cartesian, number of x cells [-]; otherwise, variable array of x-refinement
    z=[7,5,5,5,5,5,5,8,10,9,5] # If cartesian, number of z cells [-]; if tensor, variable array of z-refinement; if corner-point, fix array of z-refinement (11 entries)
    temperature=[20, 20] # Temperature bottom and top rig [C]
    pressure=104900 # Pressure at the datum [Pa]           
    diffusion=[1e-9, 2e-8] # Diffusion (in liquid and gas) [m^2/s]
    sources=[[0.9, 0.3], [1.7, 0.7]] # Source positions: x and z coordinates [m], source 1 to 2

    # Schedule: 1) injection time [s], 2) time step size to write results [s], 3) injection rate [kg/s] (source1), and 4) injection rate [kg/s] (source2)
    inj=[[900, 900, 3E-7, 0, '1e-2 3e-4 1e-20 1e-20 1.6 0.2 0.65 1.1']]

    # Facie Properties
    facie1={"permx1"=50e3,"permz1"=50e3,"poro1"=0.37,"disperc1"=1e-1,"swi1"=0.32,"sni1"=0.3,"pen1"=1500,"nkrw1"=2,"nkrn1"=2,"npe1"=2,"thre1"=5e-2,"npnt1"=100}
    facie2={"permx2"=100e3,"permz2"=100e3,"poro2"=0.38,"disperc2"=1e-1,"swi2"=0.14,"sni2"=0.3,"pen2"=800,"nkrw2"=2,"nkrn2"=2,"npe2"=2,"thre2"=5e-2,"npnt2"=100}
    facie3={"permx3"=300e3,"permz3"=300e3,"poro3"=0.40,"disperc3"=1e-1,"swi3"=0.12,"sni3"=0.1,"pen3"=200,"nkrw3"=2,"nkrn3"=2,"npe3"=2,"thre3"=5e-2,"npnt3"=100}
    facie4={"permx4"=800e3,"permz4"=800e3,"poro4"=0.39,"disperc4"=1e-1,"swi4"=0.12,"sni4"=0.1,"pen4"=150,"nkrw4"=2,"nkrn4"=2,"npe4"=2,"thre4"=5e-2,"npnt4"=100}
    facie5={"permx5"=1500e3,"permz5"=1500e3,"poro5"=0.39,"disperc5"=1e-1,"swi5"=0.12,"sni5"=0.1,"pen5"=100,"nkrw5"=2,"nkrn5"=2,"npe5"=2,"thre5"=5e-2,"npnt5"=100}
    facie6={"permx6"=3000e3,"permz6"=3000e3,"poro6"=0.42,"disperc6"=1e-1,"swi6"=0,"sni6"=0,"pen6"=1,"nkrw6"=2,"nkrn6"=2,"npe6"=2,"thre6"=5e-2,"npnt6"=100}

    # Set the saturation functions
    krw="(max(0, (sw - swi) / (1 - swi))) ** nkrw"             #Wetting rel perm saturation function [-]
    krn="(max(0, (1 - sw - sni) / (1 - sni))) ** nkrn"         #Non-wetting rel perm saturation function [-]
    cap="pen * ((sw-swi) / (1-swi)) ** (-(1.0 / npen))"        #Capillary pressure saturation function [Pa]

Each line adds a description of the variables. For the facie properties, "THREN" is the threshold to evaluate the capillary pressure function to avoid dividing by 0,
and "NPNTN" is the number of points to generate the saturation tables.

See the input files in the `examples <https://github.com/cssr-tools/pofff/blob/main/examples>`_ and `publication <https://github.com/cssr-tools/pofff/blob/main/publication>`_ 
to set the history matchings.
