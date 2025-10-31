from pathlib import Path
from loguru import logger
import os
from aitrados_api.common_lib.utils import get_value_by_dict_path
import sys
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print(f"⚠️ Current Python version ({sys.version.split()[0]}) does not have 'tomllib' built-in.")
        print("\n❌ ERROR: Neither 'tomllib' nor 'tomli' library could be found.")
        print("Please install the 'tomli' library to proceed by running:")
        print(">>> pip install tomli")







class TomlManager:
    c={}
    @classmethod
    def assign_env_variable(cls,env_key,toml_key_path,default_value=None,split_str='.'):
        value=get_value_by_dict_path(cls.c, toml_key_path,default_value=None,split_str=split_str)
        if value is None or  value.strip()=="":
            value=default_value
        if value is not None:
            os.environ[env_key]=str(value)
            logger.info(f"Set env variable {env_key} from toml config, value: {value}")

    @classmethod
    def get_value(cls,toml_key_path,default_value=None,split_str='.'):
        return get_value_by_dict_path(cls.c, toml_key_path, default_value=default_value, split_str=split_str)
    @classmethod
    def load_toml_file(cls,file=None):
        config_path=None
        if file:
            config_path_ = Path(file)
            if config_path_.exists():
                config_path=config_path_
            else:
                raise FileNotFoundError(f"toml file not found: {config_path_}")
        else:
            possible_paths = [
                Path.cwd() / 'config.toml',
                Path.cwd() / '../config.toml',
                Path.cwd() / '../../config.toml',
                Path.cwd() / '../../../config.toml',
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
            if not  config_path:
                logger.warning(f"No found any config.toml in common path {possible_paths}\nPlease Input file parameter")
                return {}


        try:
            with open(config_path, 'rb') as f:
                if data:=tomllib.load(f):
                    cls.c.update(data)
            return cls.c
        except Exception as e:
            logger.warning(f"Configuration file format error ({config_path}): {e}")
            return {}

