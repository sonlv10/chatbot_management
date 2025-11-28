"""
Rasa Training Service - Auto generate and train Rasa models from training data
"""
import os
import yaml
import subprocess
from typing import List, Dict
from pathlib import Path
from datetime import datetime


class RasaTrainingService:
    """Service to convert training data to Rasa format and train models"""
    
    def __init__(self, base_path: str = "/app/models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def get_bot_folder(self, bot_id: int) -> Path:
        """Get folder path for bot"""
        bot_folder = self.base_path / f"bot_{bot_id}"
        bot_folder.mkdir(parents=True, exist_ok=True)
        return bot_folder
    
    def generate_config_yml(self, bot_id: int, language: str = "vi") -> str:
        """Generate config.yml for Rasa"""
        config = {
            "recipe": "default.v1",
            "language": language,
            "pipeline": [
                {"name": "WhitespaceTokenizer"},
                {"name": "RegexFeaturizer"},
                {"name": "LexicalSyntacticFeaturizer"},
                {"name": "CountVectorsFeaturizer"},
                {
                    "name": "CountVectorsFeaturizer",
                    "analyzer": "char_wb",
                    "min_ngram": 1,
                    "max_ngram": 4
                },
                {
                    "name": "DIETClassifier",
                    "epochs": 100,
                    "constrain_similarities": True
                },
                {"name": "EntitySynonymMapper"},
                {"name": "ResponseSelector", "epochs": 100}
            ],
            "policies": [
                {"name": "MemoizationPolicy"},
                {"name": "RulePolicy"},
                {
                    "name": "UnexpecTEDIntentPolicy",
                    "max_history": 5,
                    "epochs": 100
                },
                {
                    "name": "TEDPolicy",
                    "max_history": 5,
                    "epochs": 100,
                    "constrain_similarities": True
                }
            ],
            "assistant_id": f"bot_{bot_id}"
        }
        
        bot_folder = self.get_bot_folder(bot_id)
        config_file = bot_folder / "config.yml"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)
        
        return str(config_file)
    
    def generate_nlu_yml(self, bot_id: int, training_data: List[Dict]) -> str:
        """Generate nlu.yml from training data"""
        # Group by intent
        intents = {}
        for item in training_data:
            intent = item.get('intent', 'general')
            if not intent:
                intent = 'general'
            
            if intent not in intents:
                intents[intent] = []
            
            intents[intent].append(item['user_message'])
        
        # Write to file manually (yaml.dump doesn't handle literal blocks well)
        bot_folder = self.get_bot_folder(bot_id)
        data_folder = bot_folder / "data"
        data_folder.mkdir(exist_ok=True)
        
        nlu_file = data_folder / "nlu.yml"
        
        with open(nlu_file, 'w', encoding='utf-8') as f:
            f.write('version: "3.1"\n\n')
            f.write('nlu:\n')
            
            for intent, examples in intents.items():
                f.write(f'  - intent: {intent}\n')
                f.write('    examples: |\n')
                for ex in examples:
                    f.write(f'      - {ex}\n')
                f.write('\n')
        
        return str(nlu_file)
    
    def generate_domain_yml(self, bot_id: int, training_data: List[Dict]) -> str:
        """Generate domain.yml from training data"""
        # Get unique intents and responses
        intents = set()
        responses = {}
        
        for item in training_data:
            intent = item.get('intent', 'general')
            if not intent:
                intent = 'general'
            
            intents.add(intent)
            
            # Store response for this intent
            response_key = f"utter_{intent}"
            if response_key not in responses:
                responses[response_key] = []
            
            responses[response_key].append({"text": item['bot_response']})
        
        # Build domain
        domain = {
            "version": "3.1",
            "intents": sorted(list(intents)),
            "responses": responses,
            "session_config": {
                "session_expiration_time": 60,
                "carry_over_slots_to_new_session": True
            }
        }
        
        # Write to file
        bot_folder = self.get_bot_folder(bot_id)
        domain_file = bot_folder / "domain.yml"
        
        with open(domain_file, 'w', encoding='utf-8') as f:
            yaml.dump(domain, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        return str(domain_file)
    
    def generate_rules_yml(self, bot_id: int, training_data: List[Dict]) -> str:
        """Generate rules.yml from training data"""
        # Get unique intents
        intents = set()
        for item in training_data:
            intent = item.get('intent', 'general')
            if not intent:
                intent = 'general'
            intents.add(intent)
        
        # Build rules
        rules_data = {
            "version": "3.1",
            "rules": []
        }
        
        for intent in sorted(intents):
            rule = {
                "rule": f"Respond to {intent}",
                "steps": [
                    {"intent": intent},
                    {"action": f"utter_{intent}"}
                ]
            }
            rules_data["rules"].append(rule)
        
        # Write to file
        bot_folder = self.get_bot_folder(bot_id)
        data_folder = bot_folder / "data"
        data_folder.mkdir(exist_ok=True)
        
        rules_file = data_folder / "rules.yml"
        
        with open(rules_file, 'w', encoding='utf-8') as f:
            yaml.dump(rules_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        return str(rules_file)
    
    def train_model(self, bot_id: int, language: str = "vi", use_finetune: bool = True) -> Dict:
        """
        Train Rasa model for bot
        Args:
            bot_id: Bot ID
            language: Language code
            use_finetune: If True and existing model found, use incremental training (faster)
        Returns: dict with status, model_path, accuracy, etc.
        """
        bot_folder = self.get_bot_folder(bot_id)
        model_folder = bot_folder / "models"
        model_folder.mkdir(exist_ok=True)
        
        model_name = f"bot_{bot_id}"
        existing_model = model_folder / f"{model_name}.tar.gz"
        
        # Check if we can use finetune
        can_finetune = use_finetune and existing_model.exists()
        
        # Build Rasa command
        if can_finetune:
            # Incremental training - faster, preserves old knowledge
            cmd = [
                "rasa", "train",
                "--data", str(bot_folder / "data"),
                "--domain", str(bot_folder / "domain.yml"),
                "--config", str(bot_folder / "config.yml"),
                "--out", str(model_folder),
                "--fixed-model-name", model_name,
                "--finetune", str(existing_model),
                "--epoch-fraction", "0.5"  # Train 50% of epochs for incremental
            ]
        else:
            # Full training from scratch
            cmd = [
                "rasa", "train",
                "--data", str(bot_folder / "data"),
                "--domain", str(bot_folder / "domain.yml"),
                "--config", str(bot_folder / "config.yml"),
                "--out", str(model_folder),
                "--fixed-model-name", model_name
            ]
        
        try:
            # Run training
            result = subprocess.run(
                cmd,
                cwd=str(bot_folder),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                model_path = model_folder / f"{model_name}.tar.gz"
                
                # Parse output for metrics
                output = result.stdout
                accuracy = None
                vocab_size = None
                training_mode = "finetune" if can_finetune else "full"
                
                # Extract metrics from output
                for line in output.split('\n'):
                    if 'accuracy' in line.lower():
                        try:
                            accuracy = float(line.split(':')[-1].strip())
                        except:
                            pass
                    if 'vocabulary' in line.lower() or 'vocab' in line.lower():
                        try:
                            vocab_size = int(line.split(':')[-1].strip())
                        except:
                            pass
                
                return {
                    "status": "success",
                    "model_path": str(model_path),
                    "accuracy": accuracy,
                    "vocabulary_size": vocab_size,
                    "training_mode": training_mode,
                    "output": output
                }
            else:
                return {
                    "status": "error",
                    "error_message": result.stderr,
                    "output": result.stdout
                }
        
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error_message": "Training timeout (10 minutes exceeded)"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def prepare_and_train(self, bot_id: int, training_data: List[Dict], language: str = "vi", use_finetune: bool = True) -> Dict:
        """
        Full pipeline: generate all files and train model
        
        Args:
            bot_id: Bot ID
            training_data: List of dicts with keys: user_message, bot_response, intent
            language: Language code (default: vi)
            use_finetune: If True, use incremental training when possible (default: True)
        
        Returns:
            Dict with training results
        """
        try:
            # 1. Generate config.yml
            self.generate_config_yml(bot_id, language)
            
            # 2. Generate nlu.yml
            self.generate_nlu_yml(bot_id, training_data)
            
            # 3. Generate domain.yml
            self.generate_domain_yml(bot_id, training_data)
            
            # 4. Generate rules.yml
            self.generate_rules_yml(bot_id, training_data)
            
            # 5. Train model (with finetune if available)
            result = self.train_model(bot_id, language, use_finetune=use_finetune)
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Failed to prepare training: {str(e)}"
            }
