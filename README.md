# MEC-downscaling-example
Collection of scripts to downscale CLM MEC output to an high-resolution regional grid

A version of these scripts has been used in the paper [Present‐Day Greenland Ice Sheet Climate and Surface Mass Balance in CESM2](doi.org/10.1029/2019JF005318) where I called it "offline downscaling": 

> In this study, EC‐indexed SEB and SMB components are downscaled offline to an 11 km RCM grid for comparison to RCM output. Our offline downscaling follows a two‐step procedure, similar to the online downscaling. First, EC topography and variables of interest are bilinearly interpolated to the target grid. Then, the variable of interest is vertically downscaled toward the target elevation by using the 3‐D fields from the previous steps. No corrections are made to preserve area‐integrated mass or energy, so these offline fluxes may differ from fluxes that were downscaled online.
