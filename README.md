# Deep Learning Model to Recommend Construction Assemblies

A deep learning system that fine-tunes T5/FLAN-T5 models to convert natural language descriptions of construction requirements into structured JSON format, based on ASHRAE 90.1-2013 construction rules.

## Overview

This project implements a text-to-JSON generation pipeline for construction assembly recommendations. It processes construction rules from ASHRAE 90.1-2013, normalizes them into a unified schema, generates synthetic training data, and fine-tunes transformer models to understand and convert natural language construction requirements into structured JSON outputs.

## Features

- **Dataset Building**: Normalizes construction properties and sets into a unified rule schema
- **Synthetic Text Generation**: Creates natural language descriptions for training data
- **Model Fine-tuning**: Fine-tunes T5/FLAN-T5 models for text-to-JSON generation
- **Inference**: Interactive and batch inference with automatic JSON correction
- **Two Rule Types**: Supports both performance rules (U-values, SHGC, etc.) and assignment rules (construction type assignments)

## Project Structure

```
DL-Construction-Recommendation/
├── data/
│   ├── construction_properties.json    # Performance rules data
│   └── construction_sets.json           # Assignment rules data
├── src/
│   ├── dataset_builder.py              # Normalizes JSON data into unified schema
│   ├── synthetic_text_gen.py           # Generates synthetic text descriptions
│   ├── build_dataset.py                # Main script to build training dataset
│   ├── train_t5.py                     # Fine-tuning script for T5/FLAN-T5
│   └── run_inference.py                # Inference script for trained models
├── dataset/                             # Generated training dataset (JSONL)
├── models/                              # Saved fine-tuned models
└── README.md
```

## Installation

### Prerequisites

- Python 3.7+
- CUDA-capable GPU (recommended for training)

### Dependencies

Install the required packages:

```bash
pip install torch transformers datasets numpy
```

Or create a `requirements.txt`:

```txt
torch>=1.9.0
transformers>=4.20.0
datasets>=2.0.0
numpy>=1.21.0
```

## Usage

### 1. Build the Training Dataset

First, normalize the construction data and generate synthetic text descriptions:

```bash
cd src
python build_dataset.py
```

This will:
- Load `construction_properties.json` and `construction_sets.json`
- Normalize them into performance and assignment rules
- Generate 1-3 synthetic text descriptions per rule
- Create a JSONL dataset at `./dataset/construction_ashrae_2013.jsonl`

### 2. Train the Model

Fine-tune a T5/FLAN-T5 model on the generated dataset:

```bash
python train_t5.py \
    --model_name google/flan-t5-base \
    --dataset_path ./dataset/construction_ashrae_2013.jsonl \
    --output_dir ./models/flan_t5_construction_ashrae_2013 \
    --learning_rate 5e-5 \
    --batch_size 8 \
    --num_epochs 5
```

**Arguments:**
- `--model_name`: HuggingFace model name (default: `google/flan-t5-base`)
- `--dataset_path`: Path to JSONL training dataset
- `--output_dir`: Directory to save the fine-tuned model
- `--learning_rate`: Learning rate (default: 5e-5)
- `--batch_size`: Training batch size (default: 8)
- `--num_epochs`: Number of training epochs (default: 5)
- `--weight_decay`: Weight decay for regularization (default: 0.01)

### 3. Run Inference

Use the trained model to generate JSON from natural language:

**Interactive mode:**
```bash
python run_inference.py --model_path ./models/flan_t5_construction_ashrae_2013
```

**Single inference:**
```bash
python run_inference.py \
    --model_path ./models/flan_t5_construction_ashrae_2013 \
    --input_text "In climate zone 5, exterior walls of type SteelFramed must not exceed a U-factor of 0.064." \
    --no-interactive
```

**Arguments:**
- `--model_path`: Path to fine-tuned model directory
- `--input_text`: Input text for single inference (optional)
- `--interactive`: Run in interactive mode (default: True)
- `--no-interactive`: Disable interactive mode

## Data Schema

### Normalized Rule Structure

Each rule in the dataset follows this unified schema:

```json
{
  "rule_id": "unique-uuid",
  "standard": "ASHRAE 90.1-2013",
  "domain": "Construction",
  "rule_category": "performance" | "assignment",
  "inputs": {
    "climate_zone": "string | null",
    "building_type": "string | null",
    "space_type": "string | null",
    "surface_type": "string | null",
    "construction_type": "string | null",
    "building_category": "string | null",
    "minimum_percent_of_surface": "number | null",
    "maximum_percent_of_surface": "number | null"
  },
  "outputs": {
    "construction_name": "string | null",
    "assigned_construction_type": "string | null",
    "max_u_value": "number | null",
    "max_f_factor": "number | null",
    "max_c_factor": "number | null",
    "max_shgc": "number | null",
    "min_vt": "number | null",
    "min_vt_shgc": "number | null"
  },
  "units": {
    "u_value": "string | null",
    "f_factor": "string | null",
    "c_factor": "string | null",
    "shgc": null,
    "vt": null
  },
  "notes": {
    "u_value_includes_interior_film": "boolean | null",
    "u_value_includes_exterior_film": "boolean | null"
  }
}
```

### Rule Categories

1. **Performance Rules**: Specify maximum U-values, SHGC, F-factors, C-factors, or minimum visible transmittance
2. **Assignment Rules**: Specify which construction type to use for specific surface types

## Training Dataset Format

The JSONL dataset contains one example per line:

```json
{"input_text": "In climate zone 5, exterior walls of type SteelFramed must not exceed a U-factor of 0.064.", "target_json": "{\"rule_id\":\"...\",\"rule_category\":\"performance\",...}"}
```

## Example Workflow

1. **Prepare data**: Place `construction_properties.json` and `construction_sets.json` in the `data/` directory
2. **Build dataset**: Run `build_dataset.py` to create the training dataset
3. **Train model**: Run `train_t5.py` to fine-tune the model
4. **Test inference**: Use `run_inference.py` to generate JSON from natural language

## Model Details

- **Base Model**: FLAN-T5-base (or T5-base)
- **Task**: Sequence-to-sequence text-to-JSON generation
- **Input**: Natural language construction requirement descriptions
- **Output**: Structured JSON following the normalized rule schema
- **Training**: Uses HuggingFace Transformers `Seq2SeqTrainer`

## Notes

- The synthetic text generator creates regulatory-style sentences that avoid copyrighted ASHRAE content
- The inference script includes automatic JSON correction for common formatting issues
- Training automatically splits data into train/eval sets (10% eval by default)
- Models are saved with tokenizers for easy loading

## License

See LICENSE file for details.
