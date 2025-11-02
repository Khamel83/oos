#!/usr/bin/env python3
"""
SOLO CREATOR MECHA SUIT - Model Selection Pipeline

Takes the full model cost table and filters down to the usable population:
1. Remove models that fail compatibility testing
2. Remove models exceeding $1/M token cost ceiling
3. Prioritize by cost-effectiveness and capability
"""

import csv
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ModelInfo:
    model_id: str
    model_name: str
    input_cost: float
    output_cost: float
    context_tokens: int
    is_free: bool
    avg_cost: float
    compatibility_status: str = "UNKNOWN"
    restrictions: List[str] = None

    def __post_init__(self):
        if self.restrictions is None:
            self.restrictions = []
        self.avg_cost = (self.input_cost + self.output_cost) / 2

class ModelSelectionPipeline:
    def __init__(self):
        self.cost_ceiling = 1.0  # $1/M token hard limit
        self.models = []
        self.compatibility_results = {}

    def load_models_from_csv(self, csv_path: str) -> List[ModelInfo]:
        """Load all models from the cost table CSV"""
        models = []

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                model = ModelInfo(
                    model_id=row['ModelID'],
                    model_name=row['ModelName'],
                    input_cost=float(row['InputCost']),
                    output_cost=float(row['OutputCost']),
                    context_tokens=int(row['ContextTokens']),
                    is_free=(float(row['InputCost']) == 0 and float(row['OutputCost']) == 0)
                )
                models.append(model)

        self.models = models
        print(f"Loaded {len(models)} models from cost table")
        return models

    def load_compatibility_results(self, results_path: str) -> Dict:
        """Load compatibility test results"""
        try:
            with open(results_path, 'r') as f:
                self.compatibility_results = json.load(f)
                print(f"Loaded compatibility results for {len(self.compatibility_results.get('results', []))} models")
        except FileNotFoundError:
            print("No compatibility results found - all models marked as UNKNOWN")
            self.compatibility_results = {'results': []}

        return self.compatibility_results

    def apply_cost_filter(self, models: List[ModelInfo]) -> Tuple[List[ModelInfo], List[ModelInfo]]:
        """Filter models by $1/M cost ceiling"""
        affordable = []
        too_expensive = []

        for model in models:
            if model.avg_cost <= self.cost_ceiling:
                affordable.append(model)
            else:
                too_expensive.append(model)

        print(f"Cost filter: {len(affordable)} affordable, {len(too_expensive)} too expensive")
        return affordable, too_expensive

    def apply_compatibility_filter(self, models: List[ModelInfo]) -> Tuple[List[ModelInfo], List[ModelInfo]]:
        """Filter out incompatible models based on test results"""
        compatible = []
        incompatible = []

        # Create lookup of compatibility results
        compat_lookup = {result['model_id']: result for result in self.compatibility_results.get('results', [])}

        for model in models:
            if model.model_id in compat_lookup:
                result = compat_lookup[model.model_id]
                status = result.get('overall_status', 'UNKNOWN')
                model.compatibility_status = status

                if status == 'COMPATIBLE':
                    compatible.append(model)
                elif status == 'LIMITED':
                    # Limited models go in compatible but with restrictions noted
                    model.restrictions = result.get('restrictions', [])
                    compatible.append(model)
                else:
                    incompatible.append(model)
            else:
                # Unknown compatibility - assume compatible for non-tested models
                compatible.append(model)

        print(f"Compatibility filter: {len(compatible)} compatible, {len(incompatible)} incompatible")
        return compatible, incompatible

    def categorize_models(self, models: List[ModelInfo]) -> Dict[str, List[ModelInfo]]:
        """Categorize models by type and cost for strategic selection"""
        categories = {
            'free_tier': [],      # $0.00 - Free models
            'budget_tier': [],    # $0.01 - $0.25 - Ultra cheap
            'standard_tier': [],  # $0.26 - $0.75 - Good value
            'premium_tier': [],   # $0.76 - $1.00 - High quality within budget
            'specialized': []     # Models with specific capabilities
        }

        for model in models:
            if model.is_free:
                categories['free_tier'].append(model)
            elif model.avg_cost <= 0.25:
                categories['budget_tier'].append(model)
            elif model.avg_cost <= 0.75:
                categories['standard_tier'].append(model)
            elif model.avg_cost <= 1.0:
                categories['premium_tier'].append(model)

            # Specialized models (identified by name patterns)
            if any(keyword in model.model_name.lower() for keyword in ['coder', 'code', 'vl', 'vision']):
                categories['specialized'].append(model)

        return categories

    def create_selection_matrix(self, categories: Dict[str, List[ModelInfo]]) -> Dict:
        """Create strategic selection matrix for different use cases"""
        matrix = {
            'rapid_iteration': {
                'description': 'Quick tasks, high volume, minimal cost',
                'preferred_tiers': ['free_tier', 'budget_tier'],
                'models': []
            },
            'quality_work': {
                'description': 'Important tasks requiring high quality',
                'preferred_tiers': ['standard_tier', 'premium_tier'],
                'models': []
            },
            'technical_tasks': {
                'description': 'Code generation, debugging, architecture',
                'preferred_tiers': ['standard_tier'] + ['specialized'],
                'models': []
            },
            'emergency_fallback': {
                'description': 'When preferred models are unavailable',
                'preferred_tiers': ['free_tier', 'budget_tier'],
                'models': []
            }
        }

        # Populate models for each use case
        for use_case, config in matrix.items():
            for tier in config['preferred_tiers']:
                config['models'].extend(categories.get(tier, []))

            # Sort by cost (cheapest first) and capability
            config['models'].sort(key=lambda m: (m.avg_cost, -m.context_tokens))

        return matrix

    def generate_final_population(self) -> Dict:
        """Generate the final usable model population"""
        print("=== SOLO CREATOR MECHA SUIT - Model Selection Pipeline ===\n")

        # Step 1: Load all models
        all_models = self.load_models_from_csv('/home/ubuntu/dev/oos/model_costs.csv')

        # Step 2: Load compatibility results if available
        self.load_compatibility_results('/home/ubuntu/dev/oos/free_model_compatibility_results.json')

        # Step 3: Apply cost filter
        affordable_models, expensive_models = self.apply_cost_filter(all_models)

        # Step 4: Apply compatibility filter
        compatible_models, incompatible_models = self.apply_compatibility_filter(affordable_models)

        # Step 5: Categorize remaining models
        categories = self.categorize_models(compatible_models)

        # Step 6: Create selection matrix
        selection_matrix = self.create_selection_matrix(categories)

        # Step 7: Generate final report
        final_population = {
            'metadata': {
                'total_models_in_table': len(all_models),
                'cost_ceiling': self.cost_ceiling,
                'expensive_excluded': len(expensive_models),
                'incompatible_excluded': len(incompatible_models),
                'final_population': len(compatible_models)
            },
            'categories': {k: len(v) for k, v in categories.items()},
            'selection_matrix': selection_matrix,
            'models_by_category': {},
            'excluded_models': {
                'too_expensive': [{'name': m.model_name, 'cost': m.avg_cost} for m in expensive_models[:10]],
                'incompatible': [{'name': m.model_name, 'status': m.compatibility_status} for m in incompatible_models[:10]]
            }
        }

        # Add full model lists by category
        for category, models in categories.items():
            final_population['models_by_category'][category] = [
                {
                    'model_id': m.model_id,
                    'model_name': m.model_name,
                    'avg_cost': m.avg_cost,
                    'context_tokens': m.context_tokens,
                    'compatibility': m.compatibility_status,
                    'restrictions': m.restrictions
                }
                for m in models
            ]

        return final_population

    def save_results(self, population: Dict, output_path: str):
        """Save the final population to JSON"""
        with open(output_path, 'w') as f:
            json.dump(population, f, indent=2)
        print(f"\nFinal population saved to: {output_path}")

    def print_summary(self, population: Dict):
        """Print summary of the selection process"""
        metadata = population['metadata']
        categories = population['categories']

        print(f"\n=== SELECTION SUMMARY ===")
        print(f"Starting models: {metadata['total_models_in_table']}")
        print(f"Excluded for cost > ${metadata['cost_ceiling']}/M: {metadata['expensive_excluded']}")
        print(f"Excluded for incompatibility: {metadata['incompatible_excluded']}")
        print(f"Final usable population: {metadata['final_population']}")

        print(f"\n=== FINAL MODEL BREAKDOWN ===")
        for category, count in categories.items():
            print(f"{category.replace('_', ' ').title()}: {count} models")

        print(f"\n=== TOP RECOMMENDED MODELS ===")
        for use_case, config in population['selection_matrix'].items():
            print(f"\n{use_case.replace('_', ' ').title()}: {config['description']}")
            top_models = config['models'][:3]
            for model in top_models:
                print(f"  • {model.model_name} (${model.avg_cost:.3f}/M)")

def main():
    """Run the complete model selection pipeline"""
    pipeline = ModelSelectionPipeline()

    # Generate final population
    population = pipeline.generate_final_population()

    # Save results
    pipeline.save_results(population, '/home/ubuntu/dev/oos/final_model_population.json')

    # Print summary
    pipeline.print_summary(population)

    return population

if __name__ == "__main__":
    main()