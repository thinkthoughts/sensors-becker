# Engineering Object Graph

Generated from `engineering_navigator/engineering_objects/*.yaml`.

## Engineering Objects

| Object | Type | Status | Sources | Candidate Specs | Open Specs |
|---|---|---|---:|---:|---:|
| [Absorber](engineering_objects/absorber.yaml) | detector_component | active | 3 | 0 | 0 |
| [Detector Module](engineering_objects/detector_module.yaml) | assembly | planned | 3 | 0 | 0 |
| [Electroplating](engineering_objects/electroplating.yaml) | manufacturing_process | active | 3 | 0 | 0 |
| [Instrument Scaling](engineering_objects/instrument_scaling.yaml) | system_scaling | planned | 0 | 0 | 5 |
| [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) | thermal_structure | active | 2 | 0 | 0 |
| [Transition-Edge Sensor](engineering_objects/tes.yaml) | sensor | active | 3 | 0 | 0 |

## Relationships

| From | Relationship | To |
|---|---|---|
| [Absorber](engineering_objects/absorber.yaml) | `manufactured_by` | [Electroplating](engineering_objects/electroplating.yaml) |
| [Absorber](engineering_objects/absorber.yaml) | `thermally_coupled_to` | [Transition-Edge Sensor](engineering_objects/tes.yaml) |
| [Absorber](engineering_objects/absorber.yaml) | `thermally_supported_by` | [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) |
| [Absorber](engineering_objects/absorber.yaml) | `integrates_into` | [Detector Module](engineering_objects/detector_module.yaml) |
| [Detector Module](engineering_objects/detector_module.yaml) | `contains` | [Absorber](engineering_objects/absorber.yaml) |
| [Detector Module](engineering_objects/detector_module.yaml) | `contains` | [Transition-Edge Sensor](engineering_objects/tes.yaml) |
| [Detector Module](engineering_objects/detector_module.yaml) | `contains` | [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) |
| [Detector Module](engineering_objects/detector_module.yaml) | `supports` | [Instrument Scaling](engineering_objects/instrument_scaling.yaml) |
| [Electroplating](engineering_objects/electroplating.yaml) | `produces` | [Absorber](engineering_objects/absorber.yaml) |
| [Electroplating](engineering_objects/electroplating.yaml) | `constrains_component_quality` | [Detector Module](engineering_objects/detector_module.yaml) |
| [Instrument Scaling](engineering_objects/instrument_scaling.yaml) | `contains` | [Detector Module](engineering_objects/detector_module.yaml) |
| [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) | `thermally_links` | [Transition-Edge Sensor](engineering_objects/tes.yaml) |
| [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) | `supports_detector_thermal_path` | [Absorber](engineering_objects/absorber.yaml) |
| [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) | `integrates_into` | [Detector Module](engineering_objects/detector_module.yaml) |
| [Transition-Edge Sensor](engineering_objects/tes.yaml) | `receives_thermal_energy_from` | [Absorber](engineering_objects/absorber.yaml) |
| [Transition-Edge Sensor](engineering_objects/tes.yaml) | `thermally_linked_by` | [Thermal-Isolation Membrane](engineering_objects/membrane.yaml) |
| [Transition-Edge Sensor](engineering_objects/tes.yaml) | `integrates_into` | [Detector Module](engineering_objects/detector_module.yaml) |

---

*Admissible generalizations trail leading specifications.*
