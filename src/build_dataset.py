"""
Dataset Builder - Main Script

This script combines dataset_builder and synthetic_text_gen to create
the final JSONL dataset for training.
"""

import json
from pathlib import Path
from typing import List, Tuple
from dataset_builder import build_normalized_dataset
from synthetic_text_gen import generate_texts_for_rules


def build_jsonl_dataset(
    properties_path: str = "./data/construction_properties.json",
    sets_path: str = "./data/construction_sets.json",
    output_path: str = "./dataset/construction_ashrae_2013.jsonl"
) -> None:
    """
    Build the final JSONL dataset from normalized rules and synthetic texts.
    
    Args:
        properties_path: Path to construction_properties.json
        sets_path: Path to construction_sets.json
        output_path: Path to output JSONL file
    """
    print("="*80)
    print("BUILDING DATASET")
    print("="*80)
    
    # Step 1: Normalize rules
    print("\nStep 1: Normalizing rules...")
    rules = build_normalized_dataset(properties_path, sets_path)
    print(f"Normalized {len(rules)} rules")
    
    # Step 2: Generate synthetic texts
    print("\nStep 2: Generating synthetic texts...")
    text_json_pairs = generate_texts_for_rules(rules)
    print(f"Generated {len(text_json_pairs)} text-JSON pairs")
    
    # Step 3: Create output directory if it doesn't exist
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 4: Write JSONL file
    print(f"\nStep 3: Writing JSONL dataset to {output_path}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for input_text, target_json in text_json_pairs:
            # Each line is a JSON object with input_text and target_json
            line_data = {
                "input_text": input_text,
                "target_json": target_json
            }
            f.write(json.dumps(line_data, ensure_ascii=False) + '\n')
    
    print(f"\n[OK] Dataset saved to {output_path}")
    print(f"Total examples: {len(text_json_pairs)}")
    print(f"Average examples per rule: {len(text_json_pairs) / len(rules):.2f}")
    
    # Print some statistics
    print("\n" + "="*80)
    print("DATASET STATISTICS")
    print("="*80)
    
    # Count by rule category
    performance_count = sum(1 for r in rules if r.get("rule_category") == "performance")
    assignment_count = sum(1 for r in rules if r.get("rule_category") == "assignment")
    
    print(f"Performance rules: {performance_count}")
    print(f"Assignment rules: {assignment_count}")
    print(f"Total rules: {len(rules)}")
    print(f"Total training examples: {len(text_json_pairs)}")
    
    # Show first few examples
    print("\n" + "="*80)
    print("FIRST 3 EXAMPLES FROM DATASET")
    print("="*80)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            example = json.loads(line)
            print(f"\n--- Example {i+1} ---")
            print(f"Input: {example['input_text']}")
            target_json = json.loads(example['target_json'])
            print(f"Target (rule_id): {target_json.get('rule_id', 'N/A')}")
            print(f"Target (category): {target_json.get('rule_category', 'N/A')}")


if __name__ == "__main__":
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    properties_path = project_root / "data" / "construction_properties.json"
    sets_path = project_root / "data" / "construction_sets.json"
    output_path = project_root / "dataset" / "construction_ashrae_2013.jsonl"
    
    # Build the dataset
    build_jsonl_dataset(
        str(properties_path),
        str(sets_path),
        str(output_path)
    )

