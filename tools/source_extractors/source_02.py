"""SOURCE_02: non-Gaussian spectral-response evidence."""

def extract(scaffold: dict) -> dict:
    record = dict(scaffold)
    record.update({
        "record_status": "evidence_extracted",
        "extraction_status": "complete_for_source_record_v1",
        "authors": [
            "Daikang Yan","Ralu Divan","Lisa M. Gades","Peter Kenesei",
            "Timothy J. Madden","Antonino Miceli","Jun-Sang Park",
            "Umeshkumar M. Patel","Orlando Quaranta","Hemant Sharma",
            "Douglas A. Bennett","William B. Doriese","Joseph W. Fowler",
            "Johnathon Gard","James Hays-Wehle","Kelsey M. Morgan",
            "Daniel R. Schmidt","Daniel S. Swetz","Joel N. Ullom"
        ],
        "materials": [
            {"name":"Gold","role":"absorber base and thermalization layer","source_pages":[1,2,3]},
            {"name":"Evaporated bismuth","role":"x-ray absorber associated with low-energy tailing","source_pages":[1,2,3,4]},
            {"name":"Electroplated bismuth","role":"x-ray absorber with Gaussian-like response","source_pages":[1,2,3,4]},
            {"name":"Mo/Cu bilayer","role":"transition-edge sensor","source_pages":[1]},
            {"name":"Copper","role":"TES banks, bars, and temporary plating current path","source_pages":[1]},
            {"name":"SiNx membrane","role":"thermal-isolation structure controlling G","source_pages":[2,3]}
        ],
        "fabrication_methods": [
            {"method":"Gold absorber fabrication","purpose":"reference absorber","parameters":{"Au_thickness_um":1.0},"source_pages":[1]},
            {"method":"Lift-off deposition of evaporated bismuth","purpose":"fabricate Au/evap-Bi absorbers","parameters":{"Au_base_um":1.0,"Bi_um":3.0},"source_pages":[1]},
            {"method":"Electrodeposition through patterned Au seed layer","purpose":"fabricate Au/elp-Bi absorbers","parameters":{"Au_base_um":1.0,"Bi_um":3.0},"source_pages":[1]},
            {"method":"Perforated SiNx membrane fabrication","purpose":"control thermal conductance","source_pages":[2]},
            {"method":"FIB cross-section and SEM","purpose":"compare absorber morphology","source_pages":[3]},
            {"method":"High-energy x-ray diffraction","purpose":"measure grain size","source_pages":[3]}
        ],
        "design_variables": [
            {"id":"absorber_material","name":"absorber material stack","unit":"category","role":"primary manufacturing variable"},
            {"id":"deposition_method","name":"bismuth deposition method","unit":"category","role":"microstructure control"},
            {"id":"Au_thickness","name":"gold thickness","unit":"µm","role":"thermalization and absorption"},
            {"id":"Bi_thickness","name":"bismuth thickness","unit":"µm","role":"quantum efficiency and tailing"},
            {"id":"absorber_area","name":"absorber dimensions","unit":"µm²","role":"dynamic range"},
            {"id":"G","name":"thermal conductance","unit":"pW/K","role":"electrothermal stability"},
            {"id":"C","name":"heat capacity","unit":"pJ/K","role":"energy resolution"},
            {"id":"delta_E","name":"energy resolution","unit":"eV FWHM","role":"detector performance"},
            {"id":"tail_fraction","name":"low-energy tail fraction","unit":"percent","role":"spectral-response quality"},
            {"id":"photon_energy","name":"incident photon energy","unit":"keV","role":"tail dependence"},
            {"id":"grain_size","name":"bismuth grain size","unit":"nm","role":"carrier thermalization"},
            {"id":"residual_resistance_ratio","name":"residual resistance ratio","unit":"dimensionless","role":"transport regime"}
        ],
        "reported_values": [
            {"object":"all absorber variants","variable":"Au_thickness","value":1.0,"unit":"µm","source_page":1},
            {"object":"Au/Bi absorbers","variable":"Bi_thickness","value":3.0,"unit":"µm","source_page":1},
            {"object":"TES","variable":"Tc","value":100,"unit":"mK approximately","source_page":1},
            {"object":"TES-to-absorber connection","variable":"Au_link_thickness","value":0.2,"unit":"µm","source_page":1},
            {"object":"absorber base","variable":"additional_Au_thickness","value":0.8,"unit":"µm","source_page":1},
            {"object":"small absorber","variable":"dimensions","value":"340 × 340","unit":"µm","source_page":2},
            {"object":"large absorber","variable":"dimensions","value":"530 × 720","unit":"µm","source_page":2},
            {"object":"3 µm Bi absorber","variable":"quantum_efficiency","value":76,"unit":"percent approximately","condition":"6 keV","source_page":2},
            {"object":"3 µm Bi absorber","variable":"quantum_efficiency","value":8,"unit":"percent approximately","condition":"30 keV","source_page":2},
            {"object":"small Au pixel","variable":"G","value":254.7,"unit":"pW/K","source_page":3},
            {"object":"small Au/evap-Bi pixel","variable":"G","value":254.3,"unit":"pW/K","source_page":3},
            {"object":"small Au/elp-Bi pixel","variable":"G","value":263.0,"unit":"pW/K","source_page":3},
            {"object":"large Au pixel","variable":"G","value":384.0,"unit":"pW/K","source_page":3},
            {"object":"large Au/evap-Bi pixel","variable":"G","value":392.3,"unit":"pW/K","source_page":3},
            {"object":"large Au/elp-Bi pixel","variable":"G","value":400.3,"unit":"pW/K","source_page":3},
            {"object":"small Au pixel","variable":"C","value":1.2,"unit":"pJ/K","source_page":3},
            {"object":"small Au/evap-Bi pixel","variable":"C","value":1.2,"unit":"pJ/K","source_page":3},
            {"object":"small Au/elp-Bi pixel","variable":"C","value":1.1,"unit":"pJ/K","source_page":3},
            {"object":"large Au pixel","variable":"C","value":3.1,"unit":"pJ/K","source_page":3},
            {"object":"large Au/evap-Bi pixel","variable":"C","value":2.9,"unit":"pJ/K","source_page":3},
            {"object":"large Au/elp-Bi pixel","variable":"C","value":3.0,"unit":"pJ/K","source_page":3},
            {"object":"evaporated Bi","variable":"average_grain_size","value":30,"unit":"nm approximately","source_page":3},
            {"object":"electroplated Bi","variable":"average_grain_radius","value":630,"unit":"nm approximately","source_page":3},
            {"object":"evaporated Bi","variable":"residual_resistance_ratio","value":0.4,"unit":"dimensionless","source_page":3},
            {"object":"secondary-electron cloud in Bi","variable":"cloud_size","value":60,"unit":"nm approximately","condition":"6 keV","source_page":4},
            {"object":"TES response","variable":"typical_response_time","value":1,"unit":"ms approximately","source_page":2}
        ],
        "measured_outcomes": [
            {"outcome":"Au and Au/elp-Bi spectra are Gaussian-like","result":"No low-energy tail detected in reported fits","source_pages":[2]},
            {"outcome":"Au/evap-Bi requires a Gaussian-plus-tail model","result":"A simple Gaussian fit fails","source_pages":[2]},
            {"outcome":"All absorber types have similar energy resolution","result":"Consistent with similar heat capacities","source_pages":[2]},
            {"outcome":"Tail fraction rises with photon energy","result":"Observed for Ti, Cr, Mn, Fe, and Cu Kα lines","source_pages":[2,4]},
            {"outcome":"Electroplated Bi adds absorption without resolution penalty","result":"3 µm Bi contributes negligible heat capacity relative to Au","source_pages":[2,4]}
        ],
        "equations": [
            {"id":"heat_capacity_from_decay","expression":"C = G * tau_thermal","display":r"C=G\tau_{\mathrm{thermal}}","variables":["C","G","tau_thermal"],"source_page":2,"role":"estimate total heat capacity"},
            {"id":"energy_resolution_heat_capacity_scaling","expression":"delta_E proportional_to sqrt(C)","display":r"\Delta E\propto\sqrt{C}","variables":["delta_E","C"],"source_page":2,"role":"energy-resolution scaling"}
        ],
        "assumptions": [
            {"assumption":"Pulse-decay time near Tb ≈ Tc approximates the thermal time constant.","source_pages":[2]},
            {"assumption":"Matched thermal coupling isolates absorber-material effects.","source_pages":[1,2]},
            {"assumption":"Low-energy tailing reflects incomplete energy collection before the TES response completes.","source_pages":[2]},
            {"assumption":"Morphology-based trapping is more plausible than energy escape for these devices.","source_pages":[3,4]}
        ],
        "engineering_relationships": [
            {"relationship":"Absorber morphology is linked to spectral response under matched thermal coupling.","engineering_effect":"Electroplated Bi preserves Gaussian response while evaporated Bi introduces a low-energy tail.","source_pages":[1,2,4]},
            {"relationship":"Bismuth adds negligible heat capacity relative to the Au base.","engineering_effect":"3 µm Bi increases quantum efficiency without measured resolution penalty.","source_pages":[2,4]},
            {"relationship":"Small columnar evaporated-Bi grains increase boundary scattering and trapping.","engineering_effect":"Incomplete thermalization lowers reconstructed event energy.","source_pages":[3,4]},
            {"relationship":"Tail fraction increases with incident photon energy.","engineering_effect":"Larger secondary-electron clouds encounter more grains and boundaries.","source_pages":[2,4]},
            {"relationship":"Tail fraction increases with evaporated-Bi thickness.","engineering_effect":"Events farther from the Au layer have greater trapping probability.","source_pages":[3]},
            {"relationship":"Thermal conductance scales with TES-plus-absorber perimeter.","engineering_effect":"Membrane geometry remains distinct from absorber material.","source_pages":[2,3]}
        ],
        "engineering_constraints": [
            {"constraint":"Spectral response","specification":"Preserve a Gaussian-like line response without low-energy tailing.","source_pages":[1,2,4]},
            {"constraint":"Quantum efficiency","specification":"Provide adequate stopping power at target x-ray energy.","source_pages":[1,2,4]},
            {"constraint":"Heat capacity","specification":"Added absorber material should not degrade energy resolution.","source_pages":[1,2,4]},
            {"constraint":"Thermal coupling","specification":"Comparisons require matched TES-to-absorber and bath coupling.","source_pages":[1,2]},
            {"constraint":"Hard-x-ray extension","specification":"Approach unity quantum efficiency through 20 keV.","source_pages":[4]}
        ],
        "future_questions": [
            "What electroplated-Bi thickness preserves tail-free response while approaching unity efficiency through 20 keV?",
            "Which grain-size distribution should become the absorber acceptance specification?",
            "How does tail fraction vary jointly with grain size, thickness, and photon energy?",
            "How repeatable are spectral-tail measurements across wafers and plating batches?",
            "Which electroplating parameters control transport and thermalization?"
        ],
        "unreported_variables": [
            "complete numerical energy-resolution values for every absorber variant",
            "complete numerical tail fractions for all tested lines",
            "grain-size distribution widths",
            "wafer-to-wafer and batch-to-batch variability",
            "electroplating process window and tolerances",
            "manufacturing yield",
            "surface roughness and oxide fraction"
        ],
        "extraction_notes": [
            "Page references use manuscript page numbers visible in the PDF.",
            "Absorber variants were fabricated on the same die with matched thermal coupling.",
            "Electroplated Bi is preferred by the reported response, but no final manufacturing tolerance is defined.",
            "Electroplated-Bi grain size is reported as an average radius of approximately 630 nm."
        ]
    })
    record.pop("source_supported_relationships", None)
    return record
