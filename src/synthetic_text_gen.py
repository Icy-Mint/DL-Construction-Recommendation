"""
Synthetic Text Generator for Construction Rules

This module generates 1-3 synthetic regulatory-style sentences per normalized rule
for training a text-to-JSON model. All text avoids copyrighted ASHRAE content.
"""

import json
import random
from typing import Dict, List, Tuple, Any, Optional


def format_value(value: Any) -> str:
    """Format a value for inclusion in text (handle None, numbers, etc.)."""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def generate_performance_texts(rule: Dict[str, Any]) -> List[str]:
    """
    Generate 1-3 synthetic sentences for a performance rule.
    
    Templates focus on U-values, SHGC, C-factor, F-factor, and VT requirements.
    """
    inputs = rule.get("inputs", {})
    outputs = rule.get("outputs", {})
    
    climate_zone = inputs.get("climate_zone")
    surface_type = inputs.get("surface_type")
    construction_type = inputs.get("construction_type")
    building_category = inputs.get("building_category")
    max_u_value = outputs.get("max_u_value")
    max_shgc = outputs.get("max_shgc")
    max_f_factor = outputs.get("max_f_factor")
    max_c_factor = outputs.get("max_c_factor")
    min_vt = outputs.get("min_vt")
    min_vt_shgc = outputs.get("min_vt_shgc")
    construction_name = outputs.get("construction_name")
    
    texts = []
    
    # Template 1: U-value requirement
    if max_u_value is not None:
        templates = [
            "In climate zone {cz}, {st} of type {ct} must not exceed a U-factor of {val}.",
            "For {st} with {ct} construction in zone {cz}, the maximum U-value is {val}.",
            "The baseline requirement for {st} ({ct}) in climate zone {cz} is U ≤ {val}.",
            "In zone {cz}, {st} assemblies using {ct} construction shall have U-value no greater than {val}.",
        ]
        
        if climate_zone and surface_type and construction_type:
            template = random.choice(templates)
            text = template.format(
                cz=climate_zone,
                st=surface_type,
                ct=construction_type,
                val=max_u_value
            )
            texts.append(text)
        
        # Variation with building category
        if building_category and climate_zone and surface_type and construction_type:
            templates_cat = [
                "For {bc} buildings in zone {cz}, {st} of type {ct} must have U-value ≤ {val}.",
                "In climate zone {cz}, {bc} {st} with {ct} construction requires U ≤ {val}.",
            ]
            template = random.choice(templates_cat)
            text = template.format(
                bc=building_category,
                cz=climate_zone,
                st=surface_type,
                ct=construction_type,
                val=max_u_value
            )
            texts.append(text)
    
    # Template 2: SHGC requirement
    if max_shgc is not None and surface_type:
        templates = [
            "The baseline assembly requires SHGC ≤ {val} for {st}.",
            "For {st}, the maximum solar heat gain coefficient is {val}.",
            "The baseline SHGC limit for {st} is {val}.",
        ]
        template = random.choice(templates)
        text = template.format(
            st=surface_type,
            val=max_shgc
        )
        texts.append(text)
        
        # With climate zone
        if climate_zone:
            templates_cz = [
                "In climate zone {cz}, {st} must have SHGC no greater than {val}.",
                "Zone {cz} requires SHGC ≤ {val} for {st}.",
            ]
            template = random.choice(templates_cz)
            text = template.format(
                cz=climate_zone,
                st=surface_type,
                val=max_shgc
            )
            texts.append(text)
    
    # Template 3: F-factor requirement
    if max_f_factor is not None and surface_type:
        templates = [
            "The F-factor for {st} must not exceed {val}.",
            "For {st}, the maximum F-factor is {val}.",
            "Baseline F-factor requirement for {st} is ≤ {val}.",
        ]
        template = random.choice(templates)
        text = template.format(
            st=surface_type,
            val=max_f_factor
        )
        texts.append(text)
    
    # Template 4: C-factor requirement
    if max_c_factor is not None and surface_type:
        templates = [
            "The C-factor for {st} shall be no greater than {val}.",
            "For {st}, the maximum C-factor is {val}.",
            "Baseline C-factor limit for {st} is {val}.",
        ]
        template = random.choice(templates)
        text = template.format(
            st=surface_type,
            val=max_c_factor
        )
        texts.append(text)
    
    # Template 5: Visible transmittance requirement
    if min_vt is not None and surface_type:
        templates = [
            "The minimum visible transmittance for {st} is {val}.",
            "For {st}, VT must be at least {val}.",
            "Baseline requires VT ≥ {val} for {st}.",
        ]
        template = random.choice(templates)
        text = template.format(
            st=surface_type,
            val=min_vt
        )
        texts.append(text)
    
    # Template 6: Combined requirements
    if max_u_value is not None and max_shgc is not None and surface_type:
        templates = [
            "For {st}, the baseline requires U ≤ {u} and SHGC ≤ {s}.",
            "The baseline assembly for {st} must meet U ≤ {u} and SHGC ≤ {s}.",
        ]
        template = random.choice(templates)
        text = template.format(
            st=surface_type,
            u=max_u_value,
            s=max_shgc
        )
        texts.append(text)
    
    # Template 7: Construction name reference
    if construction_name and max_u_value is not None and surface_type:
        templates = [
            "The {cn} assembly for {st} must have U-value ≤ {val}.",
            "For {st}, use {cn} with maximum U-value of {val}.",
        ]
        template = random.choice(templates)
        text = template.format(
            cn=construction_name,
            st=surface_type,
            val=max_u_value
        )
        texts.append(text)
    
    # If no specific requirements, create a generic rule
    if not texts and surface_type:
        templates = [
            "Baseline requirements apply to {st}.",
            "The baseline standard specifies requirements for {st}.",
        ]
        template = random.choice(templates)
        text = template.format(st=surface_type)
        texts.append(text)
    
    # Return 1-3 texts (random selection if more than 3)
    if len(texts) > 3:
        return random.sample(texts, 3)
    elif len(texts) == 0:
        # Fallback if nothing was generated
        return ["Baseline construction requirement."]
    else:
        return texts


def generate_assignment_texts(rule: Dict[str, Any]) -> List[str]:
    """
    Generate 1-3 synthetic sentences for an assignment rule.
    
    Templates focus on which construction type to use for specific surfaces.
    """
    inputs = rule.get("inputs", {})
    outputs = rule.get("outputs", {})
    
    building_type = inputs.get("building_type")
    space_type = inputs.get("space_type")
    surface_type = inputs.get("surface_type")
    building_category = inputs.get("building_category")
    assigned_construction_type = outputs.get("assigned_construction_type")
    
    texts = []
    
    # Template 1: Basic assignment
    if assigned_construction_type and surface_type:
        templates = [
            "For {st} surfaces, use {ct} construction.",
            "The baseline requires {ct} construction for {st}.",
            "Use {ct} for {st} in the baseline model.",
            "{st} shall use {ct} construction type.",
        ]
        template = random.choice(templates)
        text = template.format(
            st=surface_type,
            ct=assigned_construction_type
        )
        texts.append(text)
    
    # Template 2: With building type
    if building_type and assigned_construction_type and surface_type:
        templates = [
            "For {bt} buildings, use {ct} for {st} surfaces.",
            "In {bt} buildings, {st} requires {ct} construction.",
            "The baseline for {bt} specifies {ct} for {st}.",
            "{bt} buildings shall use {ct} construction for {st}.",
        ]
        template = random.choice(templates)
        text = template.format(
            bt=building_type,
            ct=assigned_construction_type,
            st=surface_type
        )
        texts.append(text)
    
    # Template 3: With space type
    if space_type and assigned_construction_type and surface_type:
        templates = [
            "For {sp} spaces, use {ct} for {st}.",
            "In {sp} spaces, {st} shall be {ct} construction.",
            "The baseline for {sp} requires {ct} for {st}.",
        ]
        template = random.choice(templates)
        text = template.format(
            sp=space_type,
            ct=assigned_construction_type,
            st=surface_type
        )
        texts.append(text)
    
    # Template 4: With building category
    if building_category and assigned_construction_type and surface_type:
        templates = [
            "For {bc} buildings, {st} must use {ct} construction.",
            "In {bc} buildings, use {ct} for {st}.",
            "The baseline for {bc} buildings specifies {ct} for {st}.",
        ]
        template = random.choice(templates)
        text = template.format(
            bc=building_category,
            ct=assigned_construction_type,
            st=surface_type
        )
        texts.append(text)
    
    # Template 5: Combined building type and space type
    if building_type and space_type and assigned_construction_type and surface_type:
        templates = [
            "For {bt} buildings with {sp} spaces, use {ct} for {st}.",
            "In {bt} buildings, {sp} spaces require {ct} construction for {st}.",
        ]
        template = random.choice(templates)
        text = template.format(
            bt=building_type,
            sp=space_type,
            ct=assigned_construction_type,
            st=surface_type
        )
        texts.append(text)
    
    # Fallback if nothing was generated
    if not texts:
        if assigned_construction_type and surface_type:
            texts.append(f"Use {assigned_construction_type} for {surface_type}.")
        else:
            texts.append("Baseline construction assignment requirement.")
    
    # Return 1-3 texts (random selection if more than 3)
    if len(texts) > 3:
        return random.sample(texts, 3)
    else:
        return texts


def generate_texts_for_rule(rule: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Generate 1-3 synthetic text-JSON pairs for a single rule.
    
    Args:
        rule: A normalized rule dictionary
    
    Returns:
        List of tuples (input_text, target_json_string)
    """
    rule_category = rule.get("rule_category")
    target_json = json.dumps(rule, separators=(',', ':'))  # Compact JSON
    
    if rule_category == "performance":
        texts = generate_performance_texts(rule)
    elif rule_category == "assignment":
        texts = generate_assignment_texts(rule)
    else:
        # Fallback for unknown rule types
        texts = ["Baseline construction requirement."]
    
    # Return list of (text, json) tuples
    return [(text, target_json) for text in texts]


def generate_texts_for_rules(rules: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    Generate synthetic text-JSON pairs for a list of rules.
    
    Args:
        rules: List of normalized rule dictionaries
    
    Returns:
        List of tuples (input_text, target_json_string)
    """
    all_pairs = []
    
    for rule in rules:
        try:
            pairs = generate_texts_for_rule(rule)
            all_pairs.extend(pairs)
        except Exception as e:
            print(f"Warning: Failed to generate text for rule {rule.get('rule_id', 'unknown')}: {e}")
            continue
    
    return all_pairs


if __name__ == "__main__":
    # Test the generator with sample rules
    from dataset_builder import build_normalized_dataset
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    properties_path = project_root / "data" / "construction_properties.json"
    sets_path = project_root / "data" / "construction_sets.json"
    
    print("Loading and normalizing rules...")
    rules = build_normalized_dataset(
        str(properties_path),
        str(sets_path)
    )
    
    print("\nGenerating synthetic texts...")
    text_json_pairs = generate_texts_for_rules(rules)
    
    print(f"\nGenerated {len(text_json_pairs)} text-JSON pairs from {len(rules)} rules")
    print(f"Average {len(text_json_pairs) / len(rules):.2f} texts per rule")
    
    # Show some examples
    print("\n" + "="*80)
    print("EXAMPLE TEXT-JSON PAIRS (5 samples)")
    print("="*80)
    
    for i, (text, json_str) in enumerate(text_json_pairs[:5], 1):
        print(f"\n--- Example {i} ---")
        print(f"Input Text: {text}")
        print(f"Target JSON: {json_str[:200]}..." if len(json_str) > 200 else f"Target JSON: {json_str}")

