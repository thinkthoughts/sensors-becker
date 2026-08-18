"""SOURCE_03 extractor.

Chen et al. (2021)
"Electroplating Deposition of Bismuth Absorbers for X-ray
Superconducting Transition Edge Sensors"

DOI: 10.3390/ma14237169
"""

from __future__ import annotations

from copy import deepcopy


def extract(scaffold: dict) -> dict:
    record = deepcopy(scaffold)

    record.update(
        {
            "record_status": "evidence_extracted",
            "extraction_status": "complete_for_source_record_v1",
            "authors": [
                "Jian Chen",
                "Jinjin Li",
                "Xiaolong Xu",
                "Zhenyu Wang",
                "Siming Guo",
                "Zheng Jiang",
                "Huifang Gao",
                "Qing Zhong",
                "Yuan Zhong",
                "Jiusun Zeng",
                "Xueshen Wang",
            ],
            "materials": [
                {
                    "name": "Bismuth",
                    "role": "electroplated X-ray absorber",
                    "source_sections": ["Abstract", "2.2", "4"],
                },
                {
                    "name": "Gold",
                    "role": "electroplating seed layer",
                    "source_sections": ["2.2"],
                },
                {
                    "name": "Titanium",
                    "role": "adhesion layer beneath Au seed layer",
                    "source_sections": ["2.2"],
                },
                {
                    "name": "Silicon",
                    "role": "4-inch deposition substrate",
                    "source_sections": ["2.2"],
                },
            ],
            "fabrication_methods": [
                {
                    "method": "Bismuth electroplating",
                    "purpose": "deposit Bi absorber films",
                    "parameters": {
                        "electroplating_time_min": 2,
                        "current_density_mA_per_cm2": [
                            1, 2, 3, 5, 7, 9, 11, 13, 15
                        ],
                        "bath_temperature_C": [30, 40, 50, 60],
                    },
                    "source_sections": ["2.2"],
                },
                {
                    "method": "Au/Ti seed-layer sputtering",
                    "purpose": "provide conductive electroplating seed layer",
                    "parameters": {
                        "Au_seed_thickness_nm": 125,
                        "Ti_adhesion_thickness_nm": 10,
                    },
                    "source_sections": ["2.2"],
                },
                {
                    "method": "Scanning electron microscopy",
                    "purpose": "characterize morphology and grain size",
                    "source_sections": ["2.3"],
                },
                {
                    "method": "X-ray diffraction",
                    "purpose": "characterize crystalline structure and orientation",
                    "source_sections": ["2.3"],
                },
                {
                    "method": "Electrical resistance characterization",
                    "purpose": "measure sheet resistance and residual resistance ratio",
                    "source_sections": ["2.3"],
                },
                {
                    "method": "Single-energy X-ray absorption measurement",
                    "purpose": "measure Bi-film absorptivity",
                    "source_sections": ["2.3"],
                },
            ],
            "design_variables": [
                {
                    "id": "current_density",
                    "name": "electroplating current density",
                    "unit": "mA/cm²",
                    "role": "deposition and grain-size control",
                },
                {
                    "id": "bath_temperature",
                    "name": "electroplating solution temperature",
                    "unit": "°C",
                    "role": "crystal-orientation and process control",
                },
                {
                    "id": "deposition_time",
                    "name": "electroplating time",
                    "unit": "min",
                    "role": "film-growth control",
                },
                {
                    "id": "Bi_thickness",
                    "name": "bismuth film thickness",
                    "unit": "µm",
                    "role": "grain growth and X-ray absorptivity",
                },
                {
                    "id": "grain_size",
                    "name": "bismuth grain size",
                    "unit": "nm",
                    "role": "microstructure metric",
                },
                {
                    "id": "crystal_orientation",
                    "name": "bismuth crystal orientation",
                    "unit": "category",
                    "role": "microstructure metric",
                },
                {
                    "id": "residual_resistance_ratio",
                    "name": "R300K/R4.2K",
                    "unit": "dimensionless",
                    "role": "electrical transport metric",
                },
                {
                    "id": "xray_absorptivity",
                    "name": "X-ray absorptivity",
                    "unit": "percent",
                    "role": "absorber stopping-power metric",
                },
                {
                    "id": "Au_seed_thickness",
                    "name": "gold seed-layer thickness",
                    "unit": "nm",
                    "role": "electroplating substrate variable",
                },
                {
                    "id": "Ti_adhesion_thickness",
                    "name": "titanium adhesion-layer thickness",
                    "unit": "nm",
                    "role": "seed-layer adhesion variable",
                },
                {
                    "id": "bath_pH",
                    "name": "electroplating solution pH",
                    "unit": "dimensionless",
                    "role": "electrolyte condition",
                },
            ],
            "reported_values": [
                {
                    "object": "electroplating current-density series",
                    "variable": "current_density",
                    "value": "1, 2, 3, 5, 7, 9, 11, 13, 15",
                    "unit": "mA/cm²",
                    "condition": "2 min deposition",
                    "source_section": "2.2",
                },
                {
                    "object": "electroplating temperature series",
                    "variable": "bath_temperature",
                    "value": "30, 40, 50, 60",
                    "unit": "°C",
                    "condition": "process study",
                    "source_section": "2.2",
                },
                {
                    "object": "electroplating process",
                    "variable": "deposition_time",
                    "value": 2,
                    "unit": "min",
                    "source_section": "2.2",
                },
                {
                    "object": "seed layer",
                    "variable": "Au_seed_thickness",
                    "value": 125,
                    "unit": "nm",
                    "source_section": "2.2",
                },
                {
                    "object": "adhesion layer",
                    "variable": "Ti_adhesion_thickness",
                    "value": 10,
                    "unit": "nm",
                    "source_section": "2.2",
                },
                {
                    "object": "electroplating bath",
                    "variable": "bath_pH",
                    "value": 0.3,
                    "unit": "dimensionless approximately",
                    "source_section": "2.2",
                },
                {
                    "object": "reported high-quality Bi film",
                    "variable": "current_density",
                    "value": 9,
                    "unit": "mA/cm²",
                    "condition": "40 °C",
                    "source_section": "4",
                },
                {
                    "object": "reported high-quality Bi film",
                    "variable": "bath_temperature",
                    "value": 40,
                    "unit": "°C",
                    "condition": "9 mA/cm²",
                    "source_section": "4",
                },
                {
                    "object": "reported high-quality Bi film",
                    "variable": "Bi_thickness",
                    "value": 0.431,
                    "unit": "µm",
                    "condition": "9 mA/cm², 40 °C",
                    "source_section": "4",
                },
                {
                    "object": "reported high-quality Bi film",
                    "variable": "grain_size",
                    "value": 567,
                    "unit": "nm",
                    "condition": "9 mA/cm², 40 °C",
                    "source_section": "4",
                },
                {
                    "object": "Bi film",
                    "variable": "residual_resistance_ratio",
                    "value": 1.37,
                    "unit": "dimensionless",
                    "condition": "862 nm film; 9 mA/cm²; 40 °C; 2 min",
                    "source_section": "Abstract",
                },
                {
                    "object": "5 µm Bi film",
                    "variable": "xray_absorptivity",
                    "value": 40.3,
                    "unit": "percent",
                    "condition": "10 keV",
                    "source_section": "Table 2",
                },
                {
                    "object": "5 µm Bi film",
                    "variable": "xray_absorptivity",
                    "value": 30.689,
                    "unit": "percent",
                    "condition": "15.6 keV",
                    "source_section": "Table 2",
                },
                {
                    "object": "2 µm Bi film",
                    "variable": "xray_absorptivity",
                    "value": 12.691,
                    "unit": "percent",
                    "condition": "10 keV",
                    "source_section": "Table 2",
                },
                {
                    "object": "3 µm Bi film",
                    "variable": "xray_absorptivity",
                    "value": 23.855,
                    "unit": "percent",
                    "condition": "10 keV",
                    "source_section": "Table 2",
                },
                {
                    "object": "4 µm Bi film",
                    "variable": "xray_absorptivity",
                    "value": 31.524,
                    "unit": "percent",
                    "condition": "10 keV",
                    "source_section": "Table 2",
                },
            ],
            "measured_outcomes": [
                {
                    "outcome": "Bi films are polycrystalline rhombohedral bismuth",
                    "result": "XRD shows a typical (012) orientation.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "outcome": "Grain size increases with electroplating current density",
                    "result": "Higher current density produces larger average grains in the reported series.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "outcome": "Grain size increases with film thickness",
                    "result": "Thicker electroplated Bi films exhibit larger average grains.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "outcome": "Temperature changes crystal orientation",
                    "result": "Increasing bath temperature changes Bi-grain orientation while grain-size dependence is weak.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "outcome": "Bi absorptivity increases with thickness",
                    "result": "Measured absorptivity rises from 2 to 5 µm at both reported X-ray energies.",
                    "source_sections": ["Table 2"],
                },
            ],
            "equations": [
                {
                    "id": "residual_resistance_ratio",
                    "expression": "RRR = R_300K / R_4.2K",
                    "display": "RRR = R_{300 K}/R_{4.2 K}",
                    "variables": ["residual_resistance_ratio"],
                    "source_section": "Abstract",
                    "role": "electrical transport characterization",
                },
            ],
            "assumptions": [
                {
                    "assumption": "Film morphology, crystal structure, electrical transport, and absorptivity are useful process-quality indicators for Bi TES absorbers.",
                    "source_sections": ["Abstract", "2.3", "4"],
                },
                {
                    "assumption": "The reported parameter sweeps characterize process trends rather than a complete manufacturing tolerance window.",
                    "source_sections": ["2.2", "4"],
                },
            ],
            "engineering_relationships": [
                {
                    "relationship": "Electroplating current density influences Bi grain size.",
                    "engineering_effect": "Average grain size increases as current density increases.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "relationship": "Bi film thickness influences grain size.",
                    "engineering_effect": "Average grain size increases with increasing film thickness.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "relationship": "Electroplating temperature influences crystal orientation.",
                    "engineering_effect": "Bi grain orientation changes as bath temperature increases.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "relationship": "Bi thickness determines measured X-ray absorptivity.",
                    "engineering_effect": "Increasing thickness increases stopping power at 10 and 15.6 keV.",
                    "source_sections": ["Table 2"],
                },
                {
                    "relationship": "Electroplating conditions determine electrical transport quality.",
                    "engineering_effect": "A film deposited at 9 mA/cm² and 40 °C reports RRR = 1.37.",
                    "source_sections": ["Abstract", "4"],
                },
            ],
            "engineering_constraints": [
                {
                    "constraint": "Absorber stopping power",
                    "specification": "Bi thickness must provide adequate X-ray absorptivity at the target photon energy.",
                    "source_sections": ["Abstract", "Table 2", "4"],
                },
                {
                    "constraint": "Microstructure",
                    "specification": "Electroplating conditions must control grain size and crystal orientation.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "constraint": "Electrical transport",
                    "specification": "Process conditions should produce reproducible absorber transport properties.",
                    "source_sections": ["Abstract", "4"],
                },
                {
                    "constraint": "Process control",
                    "specification": "Current density, temperature, deposition time, electrolyte, and seed layer must be recorded as coupled fabrication variables.",
                    "source_sections": ["2.2"],
                },
            ],
            "future_questions": [
                "What current-density interval preserves the desired Bi microstructure across wafers and batches?",
                "What bath-temperature interval preserves the desired grain orientation and electrical transport?",
                "How do current density, thickness, and temperature jointly affect grain-size distributions?",
                "Which grain-size or morphology metric best predicts Gaussian-like TES spectral response?",
                "What electroplating tolerances produce repeatable absorber thickness and X-ray absorptivity?",
                "How do the reported film-level process metrics transfer to completed TES detector performance?",
            ],
            "unreported_variables": [
                "batch-to-batch process variability",
                "wafer-to-wafer process variability",
                "manufacturing yield",
                "numeric current-density tolerance",
                "numeric bath-temperature tolerance",
                "numeric plating-rate tolerance",
                "grain-size distribution acceptance limits",
                "completed-TES spectral response for the reported process sweep",
            ],
            "reported_process_points": [
                {
                    "source": "SOURCE_03",
                    "current_density_mA_per_cm2": 9,
                    "bath_temperature_C": 40,
                    "deposition_time_min": 2,
                    "bismuth_thickness_um": 0.431,
                    "grain_size_nm": 567,
                    "process_interpretation": "reported high-quality film condition",
                }
            ],
            "extraction_notes": [
                "Section and table references follow the open-access journal article.",
                "The paper reports parameter sweeps and process trends, not a validated manufacturing tolerance window.",
                "The 431 nm / 567 nm condition is reported in the conclusion as a high-quality Bi film result.",
                "The abstract separately reports RRR = 1.37 for an 862 nm Bi film deposited at 9 mA/cm² and 40 °C for 2 min.",
                "Measured absorptivity is a film-level stopping-power result and should not be relabeled as completed-detector quantum efficiency.",
            ],
        }
    )

    # Extraction priorities belong to the scaffold, not the completed record.
    record.pop("priority_variables_to_extract", None)

    return record
