from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
PROJECT_NAME = PROJECT_ROOT.name.replace('-', '_')  # 'pytest_params'
SOURCE_DIR = PROJECT_ROOT / 'src' / PROJECT_NAME
