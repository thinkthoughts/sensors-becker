"""Source-specific extractor for SOURCE_06.

Source:
    PySMuRF tuning documentation
    https://pysmurf.readthedocs.io/en/main/client/tune.html

This source is implementation-facing documentation for the SMuRF control
software. It is used to test whether the real channel-assignment logic
supplies the modular and coprimality structure required for a direct
General Divisor Theorem application.
"""

from __future__ import annotations

from copy import deepcopy


def extract(scaffold: dict) -> dict:
    """Complete SOURCE_06 from the documented PySMuRF tuning interface."""

    record = deepcopy(scaffold)

    record.update(
        {
            "record_status": "evidence_extracted",
            "extraction_status": "complete_for_source_record_v1",
            "authors": [
                "SLAC PySMuRF developers",
            ],
            "materials": [
                {
                    "name": "microwave resonator channels",
                    "role": "software-assigned readout channels",
                    "source_sections": ["assign_channels"],
                },
                {
                    "name": "SMuRF firmware bands and subbands",
                    "role": "discrete digital readout structure",
                    "source_sections": ["assign_channels", "check_lock"],
                },
            ],
            "fabrication_methods": [],
            "design_variables": [
                {
                    "id": "band",
                    "name": "SMuRF band index",
                    "unit": "integer_index",
                    "role": "select 500 MHz readout band",
                },
                {
                    "id": "subband",
                    "name": "assigned subband index",
                    "unit": "integer_index",
                    "role": "digital channelization",
                },
                {
                    "id": "channel",
                    "name": "assigned channel number",
                    "unit": "integer_index",
                    "role": "resonator readout assignment",
                },
                {
                    "id": "channel_per_subband",
                    "name": "channels assigned per subband",
                    "unit": "channels",
                    "role": "assignment capacity",
                },
                {
                    "id": "min_offset",
                    "name": "minimum resonator frequency offset",
                    "unit": "MHz",
                    "role": "pairwise collision exclusion",
                },
                {
                    "id": "frequency_offset_from_subband_center",
                    "name": "resonator offset from subband center",
                    "unit": "MHz",
                    "role": "continuous placement within subband",
                },
                {
                    "id": "tracking_status",
                    "name": "channel tracking quality state",
                    "unit": "categorical",
                    "role": "channel enable/disable decision",
                },
                {
                    "id": "n_phi0",
                    "name": "desired flux quanta per ramp cycle",
                    "unit": "Phi0",
                    "role": "flux-ramp amplitude target",
                },
            ],
            "reported_values": [
                {
                    "variable": "channel_per_subband",
                    "value": 4,
                    "unit": "channels",
                    "condition": "default assign_channels argument",
                    "source_section": "assign_channels",
                },
                {
                    "variable": "min_offset",
                    "value": 0.1,
                    "unit": "MHz",
                    "condition": "default minimum offset between resonators",
                    "source_section": "assign_channels",
                },
                {
                    "variable": "band_width",
                    "value": 500,
                    "unit": "MHz",
                    "condition": "band parameter documentation describes the 500 MHz band",
                    "source_section": "calculate_eta_svd / check_lock",
                },
                {
                    "variable": "tone_power",
                    "value_range": [0, 15],
                    "unit": "integer_setting",
                    "condition": "for most SMuRF firmware versions",
                    "source_section": "eta_scan",
                },
            ],
            "measured_outcomes": [],
            "equations": [],
            "assumptions": [
                {
                    "assumption": (
                        "Channel assignment is driven by resonator frequency positions and "
                        "documented software rules rather than by a published modular formula."
                    ),
                    "source_section": "assign_channels",
                },
            ],
            "engineering_relationships": [
                {
                    "relationship": "resonator_frequency_maps_to_subband_and_channel",
                    "engineering_effect": (
                        "assign_channels maps resonator frequencies to integer subband and channel arrays."
                    ),
                    "source_sections": ["assign_channels"],
                },
                {
                    "relationship": "minimum_frequency_offset_excludes_close_pairs",
                    "engineering_effect": (
                        "If two resonators are closer than the configured minimum offset, both are ignored."
                    ),
                    "source_sections": ["assign_channels"],
                },
                {
                    "relationship": "channel_capacity_is_bounded_per_subband",
                    "engineering_effect": (
                        "The default assignment capacity is four channels per subband."
                    ),
                    "source_sections": ["assign_channels"],
                },
                {
                    "relationship": "tracking_quality_disables_bad_channels",
                    "engineering_effect": (
                        "check_lock turns off channels that violate tracking quality limits."
                    ),
                    "source_sections": ["check_lock"],
                },
                {
                    "relationship": "flux_quanta_target_is_not_intrinsically_integer",
                    "engineering_effect": (
                        "n_phi0 is float-valued; integer values are recommended but not required."
                    ),
                    "source_sections": ["estimate_flux_ramp_amp"],
                },
            ],
            "engineering_constraints": [
                {
                    "constraint": "minimum_resonator_offset",
                    "statement": (
                        "The default minimum offset between resonators is 0.1 MHz; if closer, both resonators are ignored."
                    ),
                    "source_section": "assign_channels",
                },
                {
                    "constraint": "channels_per_subband",
                    "statement": (
                        "assign_channels defaults to four channels per subband."
                    ),
                    "source_section": "assign_channels",
                },
                {
                    "constraint": "tracking_quality_limits",
                    "statement": (
                        "check_lock turns off channels with bad tracking according to configured limits."
                    ),
                    "source_section": "check_lock",
                },
            ],
            "future_questions": [
                "What exact formula maps resonator frequency to integer subband index?",
                "What exact rule chooses channel number within each subband?",
                "Are any subband/channel indices systematically skipped for clocking, aliasing, or synchronization reasons?",
                "Can any software exclusion be expressed exactly as a residue-class rule?",
                "Can any software exclusion be expressed exactly as gcd(n,N)=1?",
            ],
            "unreported_variables": [
                "explicit closed-form subband assignment formula",
                "explicit modular channel assignment rule",
                "explicit factor-based index exclusion rule",
                "documented coprimality condition on channel or subband indices",
            ],
            "gdt_applicability": {
                "status": "real_integer_assignment_present_but_direct_GDT_not_established",
                "candidate_integer_structures": [
                    {
                        "structure": "subband_index",
                        "evidence": "assign_channels returns an integer subband array",
                        "gdt_status": "integer_state_present_modular_rule_not_documented",
                    },
                    {
                        "structure": "channel_number",
                        "evidence": "assign_channels returns an integer channel array",
                        "gdt_status": "integer_state_present_residue_rule_not_documented",
                    },
                    {
                        "structure": "channels_per_subband",
                        "evidence": "default value is 4",
                        "gdt_status": "bounded_integer_capacity_not_a_residue_rule",
                    },
                ],
                "physical_exclusion_rule": {
                    "type": "pairwise_frequency_distance_threshold",
                    "rule": "ignore both resonators if separation < 0.1 MHz",
                    "gdt_status": (
                        "not_coprimality; documented exclusion is metric/threshold-based rather than factor-based"
                    ),
                },
                "important_negative_result": (
                    "n_phi0 is documented as float-valued. Integer values are recommended but not required, "
                    "so it is not an intrinsic integer state for direct GDT use."
                ),
                "missing_direct_hypotheses": [
                    "natural modulus m tied to the assignment algorithm",
                    "physical residue-class rule n ≡ a (mod m)",
                    "physical factor-exclusion rule gcd(n,N)=1",
                ],
            },
            "extraction_notes": [
                "SOURCE_06 advances the audit from published architecture to implementation-facing assignment rules.",
                "The software confirms real integer subband and channel outputs.",
                "The documented close-resonator exclusion is a frequency-distance threshold, not a coprimality rule.",
                "A direct GDT application therefore remains unestablished after SOURCE_06.",
            ],
        }
    )

    record.pop("priority_variables_to_extract", None)
    record.pop("gdt_applicability_priorities", None)

    return record
