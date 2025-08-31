import yaml
from pathlib import Path
from fastapi import HTTPException


def read_config_yaml():
    """Reads config.yaml from project root"""
    # Path from utils.py to project root
    # backend/app/api/v1/endpoints/utils.py → project root (5 levels up)
    config_path = Path(__file__).parent.parent.parent.parent.parent.parent / "config.yaml"
    
    if not config_path.exists():
        raise HTTPException(
            status_code=404,
            detail="config.yaml not found in project root"
        )
    
    try:
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        if not config_data:
            raise HTTPException(
                status_code=422,
                detail="config.yaml is empty"
            )
        
        return config_data
        
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid YAML format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading config file: {str(e)}"
        )
