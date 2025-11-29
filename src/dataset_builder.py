"""
Dataset Builder for ASHRAE 90.1-2013 Construction Rules

This module normalizes construction_properties.json and construction_sets.json
into a unified JSON schema for fine-tuning a text-to-JSON model.
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_climate_zone(climate_zone_set: Optional[str]) -> Optional[str]:
    """
    Extract climate zone from climate_zone_set string.
    Example: "ClimateZone 0" -> "0", "ClimateZone 1A" -> "1A"
    """
    if climate_zone_set is None:
        return None
    # Remove "ClimateZone " prefix if present
    if climate_zone_set.startswith("ClimateZone "):
        return climate_zone_set.replace("ClimateZone ", "").strip()
    return climate_zone_set.strip()


def normalize_performance_rule(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a construction_properties entry into the unified schema.
    rule_category = "performance"
    """
    # Extract climate zone
    climate_zone = extract_climate_zone(entry.get("climate_zone_set"))
    
    # Build the normalized rule
    rule = {
        "rule_id": str(uuid.uuid4()),
        "standard": "ASHRAE 90.1-2013",
        "domain": "Construction",
        "rule_category": "performance",
        
        "inputs": {
            "climate_zone": climate_zone,
            "building_type": None,
            "space_type": None,
            "surface_type": entry.get("intended_surface_type"),
            "construction_type": entry.get("standards_construction_type"),
            "building_category": entry.get("building_category"),
            "minimum_percent_of_surface": entry.get("minimum_percent_of_surface"),
            "maximum_percent_of_surface": entry.get("maximum_percent_of_surface")
        },
        
        "outputs": {
            "construction_name": entry.get("construction"),
            "assigned_construction_type": None,
            "max_u_value": entry.get("assembly_maximum_u_value"),
            "max_f_factor": entry.get("assembly_maximum_f_factor"),
            "max_c_factor": entry.get("assembly_maximum_c_factor"),
            "max_shgc": entry.get("assembly_maximum_solar_heat_gain_coefficient"),
            "min_vt": entry.get("assembly_minimum_visible_transmittance"),
            "min_vt_shgc": entry.get("assembly_minimum_vt_shgc")
        },
        
        "units": {
            "u_value": entry.get("assembly_maximum_u_value_unit"),
            "f_factor": entry.get("assembly_maximum_f_factor_unit"),
            "c_factor": entry.get("assembly_maximum_c_factor_unit"),
            "shgc": None,  # SHGC is unitless
            "vt": None  # VT is unitless
        },
        
        "notes": {
            "u_value_includes_interior_film": entry.get("u_value_includes_interior_film_coefficient"),
            "u_value_includes_exterior_film": entry.get("u_value_includes_exterior_film_coefficient")
        }
    }
    
    return rule


def normalize_assignment_rule(
    construction_set: Dict[str, Any],
    surface_field: str,
    construction_type: str,
    building_category: Optional[str]
) -> Dict[str, Any]:
    """
    Normalize a construction_sets entry into an assignment rule.
    rule_category = "assignment"
    
    Args:
        construction_set: The full construction set entry
        surface_field: The field name (e.g., "exterior_wall_standards_construction_type")
        construction_type: The construction type value (non-null)
        building_category: The corresponding building category
    """
    # Map surface field names to surface types
    # Extract surface type from field name (e.g., "exterior_wall_..." -> "ExteriorWall")
    surface_type = None
    if "exterior_wall" in surface_field:
        surface_type = "ExteriorWall"
    elif "exterior_floor" in surface_field:
        surface_type = "ExteriorFloor"
    elif "exterior_roof" in surface_field:
        surface_type = "ExteriorRoof"
    elif "ground_contact_wall" in surface_field:
        surface_type = "GroundContactWall"
    elif "ground_contact_floor" in surface_field:
        surface_type = "GroundContactFloor"
    elif "ground_contact_ceiling" in surface_field:
        surface_type = "GroundContactCeiling"
    elif "exterior_fixed_window" in surface_field:
        surface_type = "ExteriorFixedWindow"
    elif "exterior_operable_window" in surface_field:
        surface_type = "ExteriorOperableWindow"
    elif "exterior_door" in surface_field:
        surface_type = "ExteriorDoor"
    elif "exterior_glass_door" in surface_field:
        surface_type = "ExteriorGlassDoor"
    elif "exterior_overhead_door" in surface_field:
        surface_type = "ExteriorOverheadDoor"
    elif "exterior_skylight" in surface_field:
        surface_type = "ExteriorSkylight"
    
    # Build the normalized rule
    rule = {
        "rule_id": str(uuid.uuid4()),
        "standard": "ASHRAE 90.1-2013",
        "domain": "Construction",
        "rule_category": "assignment",
        
        "inputs": {
            "climate_zone": None,
            "building_type": construction_set.get("building_type") if construction_set.get("building_type") != "Any" else None,
            "space_type": construction_set.get("space_type"),
            "surface_type": surface_type,
            "construction_type": None,
            "building_category": building_category,
            "minimum_percent_of_surface": None,
            "maximum_percent_of_surface": None
        },
        
        "outputs": {
            "construction_name": None,
            "assigned_construction_type": construction_type,
            "max_u_value": None,
            "max_f_factor": None,
            "max_c_factor": None,
            "max_shgc": None,
            "min_vt": None,
            "min_vt_shgc": None
        },
        
        "units": {
            "u_value": None,
            "f_factor": None,
            "c_factor": None,
            "shgc": None,
            "vt": None
        },
        
        "notes": {
            "u_value_includes_interior_film": None,
            "u_value_includes_exterior_film": None
        }
    }
    
    return rule


def normalize_construction_properties(
    properties_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Normalize all entries from construction_properties.json.
    Returns a list of performance rules.
    """
    rules = []
    properties_list = properties_data.get("construction_properties", [])
    
    for entry in properties_list:
        try:
            rule = normalize_performance_rule(entry)
            rules.append(rule)
        except Exception as e:
            print(f"Warning: Failed to normalize performance rule: {e}")
            continue
    
    return rules


def normalize_construction_sets(
    sets_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Normalize all entries from construction_sets.json.
    Returns a list of assignment rules (one per non-null surface type).
    """
    rules = []
    sets_list = sets_data.get("construction_sets", [])
    
    # Fields that represent surface type assignments
    surface_type_fields = [
        "exterior_wall_standards_construction_type",
        "exterior_floor_standards_construction_type",
        "exterior_roof_standards_construction_type",
        "ground_contact_wall_standards_construction_type",
        "ground_contact_floor_standards_construction_type",
        "ground_contact_ceiling_standards_construction_type",
        "exterior_fixed_window_standards_construction_type",
        "exterior_operable_window_standards_construction_type",
        "exterior_door_standards_construction_type",
        "exterior_glass_door_standards_construction_type",
        "exterior_overhead_door_standards_construction_type",
        "exterior_skylight_standards_construction_type"
    ]
    
    for construction_set in sets_list:
        for surface_field in surface_type_fields:
            construction_type = construction_set.get(surface_field)
            
            # Only create a rule if construction_type is not null
            if construction_type is not None:
                # Get the corresponding building_category field
                building_category_field = surface_field.replace(
                    "_standards_construction_type", "_building_category"
                )
                building_category = construction_set.get(building_category_field)
                
                try:
                    rule = normalize_assignment_rule(
                        construction_set,
                        surface_field,
                        construction_type,
                        building_category
                    )
                    rules.append(rule)
                except Exception as e:
                    print(f"Warning: Failed to normalize assignment rule for {surface_field}: {e}")
                    continue
    
    return rules


def build_normalized_dataset(
    properties_path: str = "./data/construction_properties.json",
    sets_path: str = "./data/construction_sets.json"
) -> List[Dict[str, Any]]:
    """
    Main function to build the normalized dataset.
    
    Args:
        properties_path: Path to construction_properties.json
        sets_path: Path to construction_sets.json
    
    Returns:
        List of normalized rules (performance + assignment)
    """
    # Load JSON files
    print("Loading construction_properties.json...")
    properties_data = load_json_file(properties_path)
    
    print("Loading construction_sets.json...")
    sets_data = load_json_file(sets_path)
    
    # Normalize performance rules
    print("Normalizing performance rules...")
    performance_rules = normalize_construction_properties(properties_data)
    print(f"Created {len(performance_rules)} performance rules")
    
    # Normalize assignment rules
    print("Normalizing assignment rules...")
    assignment_rules = normalize_construction_sets(sets_data)
    print(f"Created {len(assignment_rules)} assignment rules")
    
    # Combine rules
    all_rules = performance_rules + assignment_rules
    print(f"\nTotal normalized rules: {len(all_rules)}")
    
    # Print five example rules
    print("\n" + "="*80)
    print("EXAMPLE NORMALIZED RULES (5 samples)")
    print("="*80)
    
    # Show mix of performance and assignment rules
    examples = []
    if performance_rules:
        examples.append(("PERFORMANCE", performance_rules[0]))
    if len(performance_rules) > 1:
        examples.append(("PERFORMANCE", performance_rules[len(performance_rules)//2]))
    if assignment_rules:
        examples.append(("ASSIGNMENT", assignment_rules[0]))
    if len(assignment_rules) > 1:
        examples.append(("ASSIGNMENT", assignment_rules[len(assignment_rules)//2]))
    if len(all_rules) > 4:
        examples.append(("MIXED", all_rules[-1]))
    
    for i, (rule_type, rule) in enumerate(examples[:5], 1):
        print(f"\n--- Example {i} ({rule_type} RULE) ---")
        print(json.dumps(rule, indent=2))
    
    return all_rules


if __name__ == "__main__":
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    properties_path = project_root / "data" / "construction_properties.json"
    sets_path = project_root / "data" / "construction_sets.json"
    
    # Build normalized dataset
    normalized_rules = build_normalized_dataset(
        str(properties_path),
        str(sets_path)
    )
    
    print(f"\n[OK] Dataset building complete. Total rules: {len(normalized_rules)}")

