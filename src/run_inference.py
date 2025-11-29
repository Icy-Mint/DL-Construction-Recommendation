"""
Inference Script for Fine-tuned T5/FLAN-T5 Model

Loads a fine-tuned model and generates JSON from natural language descriptions.
Includes auto-correction for invalid JSON output.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def load_model(model_path: str):
    """
    Load the fine-tuned model and tokenizer.
    
    Args:
        model_path: Path to the fine-tuned model directory
    
    Returns:
        Tuple of (tokenizer, model)
    """
    print(f"Loading model from {model_path}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    
    print(f"Model loaded on {device}")
    return tokenizer, model, device


def fix_json_string(json_str: str) -> Optional[str]:
    """
    Attempt to fix common JSON formatting issues.
    
    Args:
        json_str: Potentially malformed JSON string
    
    Returns:
        Fixed JSON string or None if unfixable
    """
    # Remove leading/trailing whitespace
    json_str = json_str.strip()
    
    # Remove markdown code blocks if present
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.IGNORECASE)
    json_str = re.sub(r'^```\s*', '', json_str, flags=re.IGNORECASE)
    json_str = re.sub(r'```\s*$', '', json_str, flags=re.IGNORECASE)
    
    # Try to extract JSON if wrapped in text
    json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    
    # Fix common issues
    # Replace single quotes with double quotes (simple cases)
    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
    
    # Fix trailing commas (remove before closing braces/brackets)
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    return json_str


def generate_json(
    text: str,
    tokenizer,
    model,
    device: str,
    max_input_length: int = 512,
    max_output_length: int = 512,
    num_beams: int = 4,
    do_sample: bool = False,
    temperature: float = 1.0
) -> Dict[str, Any]:
    """
    Generate JSON from natural language text.
    
    Args:
        text: Input natural language description
        tokenizer: Tokenizer instance
        model: Model instance
        device: Device to run inference on
        max_input_length: Maximum input sequence length
        max_output_length: Maximum output sequence length
        num_beams: Number of beams for beam search
        do_sample: Whether to use sampling
        temperature: Temperature for sampling
    
    Returns:
        Parsed JSON dictionary
    """
    # Tokenize input
    inputs = tokenizer(
        text,
        max_length=max_input_length,
        padding=True,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_output_length,
            num_beams=num_beams,
            do_sample=do_sample,
            temperature=temperature,
            early_stopping=True
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Try to parse JSON
    try:
        result = json.loads(generated_text)
        return result
    except json.JSONDecodeError:
        # Try to fix JSON
        fixed_json = fix_json_string(generated_text)
        if fixed_json:
            try:
                result = json.loads(fixed_json)
                return result
            except json.JSONDecodeError:
                pass
        
        # If still invalid, return error structure
        return {
            "error": "Failed to parse JSON",
            "raw_output": generated_text,
            "fixed_attempt": fixed_json if fixed_json else None
        }


def pretty_print_json(data: Dict[str, Any]) -> None:
    """
    Pretty print JSON data.
    
    Args:
        data: JSON dictionary to print
    """
    print("\n" + "="*80)
    print("GENERATED JSON")
    print("="*80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("="*80)


def run_inference(
    model_path: str,
    input_text: Optional[str] = None,
    interactive: bool = True
) -> None:
    """
    Run inference with the fine-tuned model.
    
    Args:
        model_path: Path to fine-tuned model directory
        input_text: Optional input text (if not provided, will prompt)
        interactive: Whether to run in interactive mode
    """
    # Load model
    tokenizer, model, device = load_model(model_path)
    
    if not interactive and input_text:
        # Single inference
        result = generate_json(input_text, tokenizer, model, device)
        pretty_print_json(result)
        return
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE INFERENCE MODE")
    print("="*80)
    print("Enter natural language descriptions to generate JSON.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            if input_text:
                text = input_text
                input_text = None  # Clear after first use
            else:
                text = input("\nInput text: ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break
            
            if not text:
                continue
            
            # Generate JSON
            print("\nGenerating JSON...")
            result = generate_json(text, tokenizer, model, device)
            
            # Pretty print
            pretty_print_json(result)
            
            # Check for errors
            if "error" in result:
                print("\n[WARNING] JSON parsing failed. Raw output:")
                print(result.get("raw_output", "N/A"))
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run inference with fine-tuned T5/FLAN-T5 model")
    parser.add_argument(
        "--model_path",
        type=str,
        default="./models/flan_t5_construction_ashrae_2013",
        help="Path to fine-tuned model directory"
    )
    parser.add_argument(
        "--input_text",
        type=str,
        default=None,
        help="Input text for single inference (if not provided, runs interactively)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="Run in interactive mode (default: True)"
    )
    parser.add_argument(
        "--no-interactive",
        action="store_false",
        dest="interactive",
        help="Disable interactive mode"
    )
    
    args = parser.parse_args()
    
    # Get absolute path
    project_root = Path(__file__).parent.parent
    model_path = project_root / args.model_path if not Path(args.model_path).is_absolute() else Path(args.model_path)
    
    if not model_path.exists():
        print(f"[ERROR] Model path does not exist: {model_path}")
        print("Please train the model first using train_t5.py")
        exit(1)
    
    # Run inference
    run_inference(
        str(model_path),
        input_text=args.input_text,
        interactive=args.interactive if args.input_text is None else False
    )

