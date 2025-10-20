"""
Data Loader - Phase 3
Loads all integrated data for query system
"""

import pandas as pd
import json
from pathlib import Path


class DataLoader:
    """Load and manage all integrated datasets"""
    
    def __init__(self, data_dir="data/integrated"):
        self.data_dir = Path(data_dir)
        self.entities = None
        self.projects = None
        self.communications = None
        self.relationships = None
        self.entity_maps = {}
        
    def load_all(self):
        """Load all datasets"""
        print("📂 Loading integrated data...")
        
        # Load CSVs
        self.entities = pd.read_csv(f"{self.data_dir}/master_entities.csv")
        self.projects = pd.read_csv(f"{self.data_dir}/enriched_projects.csv")
        self.communications = pd.read_csv(f"{self.data_dir}/unified_communications.csv")
        self.relationships = pd.read_csv(f"{self.data_dir}/entity_relationships.csv")

        # Load entity maps
        with open(f"{self.data_dir}/developer_entity_map.json", 'r') as f:
            self.entity_maps['developers'] = json.load(f)

        with open(f"{self.data_dir}/investor_entity_map.json", 'r') as f:
            self.entity_maps['investors'] = json.load(f)
        
        print(f"   ✓ Entities: {len(self.entities)}")
        print(f"   ✓ Projects: {len(self.projects)}")
        print(f"   ✓ Communications: {len(self.communications)}")
        print(f"   ✓ Relationships: {len(self.relationships)}")
        
        return self
    
    def get_entity_by_id(self, entity_id):
        """Get entity details by ID"""
        entity = self.entities[self.entities['entity_id'] == entity_id]
        return entity.iloc[0].to_dict() if not entity.empty else None
    
    def get_project_by_id(self, project_id):
        """Get project details by ID"""
        project = self.projects[self.projects['ProjectID'] == project_id]
        return project.iloc[0].to_dict() if not project.empty else None
    
    def get_developer_by_project(self, project_id):
        """Get developer for a project"""
        project = self.projects[self.projects['ProjectID'] == project_id]
        if not project.empty:
            dev_id = project.iloc[0]['DeveloperID']
            return self.get_entity_by_id(dev_id)
        return None
    
    def get_communications_by_entity(self, entity_id):
        """Get all communications mentioning an entity"""
        comms = self.communications[
            (self.communications['mentioned_developers'].str.contains(entity_id, na=False)) |
            (self.communications['mentioned_investors'].str.contains(entity_id, na=False))
        ]
        return comms
    
    def get_relationships_for_entity(self, entity_id):
        """Get all relationships for an entity"""
        rels = self.relationships[
            (self.relationships['entity_1'] == entity_id) |
            (self.relationships['entity_2'] == entity_id)
        ]
        return rels
    
    def search_entities(self, name_query):
        """Search entities by name (case insensitive)"""
        query_lower = name_query.lower()
        matches = self.entities[
            self.entities['canonical_name'].str.lower().str.contains(query_lower, na=False)
        ]
        return matches


# Global instance
data = DataLoader()