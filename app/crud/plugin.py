#app/crud/plugin.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.plugin import Plugin
from app.core.exceptions import PluginNotFoundError, PluginValidationError
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("DevOS.Plugins")

def create_plugin(db: Session, data: Dict) -> Plugin:
    name = data.get("name")
    if not name or not name.strip():
        raise PluginValidationError("Plugin name is required.")
    name = name.strip()

    if get_plugin_by_name(db, name):
        raise PluginValidationError(f"Plugin with name '{name}' already exists.")

    config_json_data = data.get("config_json", {})
    if isinstance(config_json_data, str):
        try:
            config_dict = json.loads(config_json_data)
        except json.JSONDecodeError:
            raise PluginValidationError("Invalid JSON format for configuration.")
    elif isinstance(config_json_data, dict):
        config_dict = config_json_data
    else:
        raise PluginValidationError("Configuration must be a valid JSON string or a dictionary.")

    plugin = Plugin(
        name=name,
        description=data.get("description", "").strip(),
        config_json=config_dict,
        is_active=data.get("is_active", True),
        version=data.get("version"),
        author=data.get("author"),
        subscription_level=data.get("subscription_level"),
        is_private=bool(data.get("is_private", False)),
        ui_component=data.get("ui_component"),
        tags=data.get("tags", []),
    )
    try:
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        logger.info(f"Plugin '{plugin.name}' created with ID {plugin.id}.")
        return plugin
    except IntegrityError:
        db.rollback()
        raise PluginValidationError(f"Database error: Could not create plugin '{name}'. It might violate a database constraint.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating plugin {name}: {e}")
        raise

def get_plugin(db: Session, plugin_id: int) -> Plugin:
    plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
    if not plugin:
        raise PluginNotFoundError(f"Plugin with ID {plugin_id} not found.")
    return plugin

def get_plugin_by_name(db: Session, name: str) -> Optional[Plugin]:
    return db.query(Plugin).filter(Plugin.name == name).first()

def get_all_plugins(db: Session, filters: Optional[Dict] = None) -> List[Plugin]:
    query = db.query(Plugin)
    if filters:
        if "is_active" in filters:
            query = query.filter(Plugin.is_active == filters["is_active"])
        if "subscription_level" in filters:
            query = query.filter(Plugin.subscription_level == filters["subscription_level"])
        if "is_private" in filters:
            query = query.filter(Plugin.is_private == filters["is_private"])
        if "tag" in filters:
            tag = filters["tag"]
            query = query.filter(Plugin.tags.contains([tag]))
    return query.order_by(Plugin.name).all()

def update_plugin(db: Session, plugin_id: int, data: Dict) -> Plugin:
    plugin = get_plugin(db, plugin_id)

    if "name" in data:
        new_name = data["name"].strip()
        if not new_name:
            raise PluginValidationError("Plugin name cannot be empty.")
        if new_name != plugin.name:
            existing_plugin = get_plugin_by_name(db, new_name)
            if existing_plugin and existing_plugin.id != plugin_id:
                raise PluginValidationError(f"Plugin with name '{new_name}' already exists.")
        plugin.name = new_name

    if "description" in data:
        plugin.description = data["description"].strip()

    if "config_json" in data:
        config_json_data = data["config_json"]
        if isinstance(config_json_data, str):
            try:
                plugin.config_json = json.loads(config_json_data)
            except json.JSONDecodeError:
                raise PluginValidationError("Invalid JSON format for configuration.")
        elif isinstance(config_json_data, dict):
            plugin.config_json = config_json_data
        else:
            raise PluginValidationError("Configuration must be a valid JSON string or a dictionary.")

    if "is_active" in data:
        plugin.is_active = bool(data["is_active"])
        logger.info(f"Plugin '{plugin.name}' active status set to {plugin.is_active}.")

    if "version" in data:
        plugin.version = data["version"]

    if "author" in data:
        plugin.author = data["author"]

    if "subscription_level" in data:
        plugin.subscription_level = data["subscription_level"]

    if "is_private" in data:
        plugin.is_private = bool(data["is_private"])

    if "ui_component" in data:
        plugin.ui_component = data["ui_component"]

    if "tags" in data:
        plugin.tags = data["tags"]

    try:
        db.commit()
        db.refresh(plugin)
        logger.info(f"Plugin '{plugin.name}' (ID: {plugin.id}) updated.")
        return plugin
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating plugin {plugin.name}: {e}")
        raise

def delete_plugin(db: Session, plugin_id: int) -> bool:
    plugin = get_plugin(db, plugin_id)
    try:
        db.delete(plugin)
        db.commit()
        logger.info(f"Plugin '{plugin.name}' (ID: {plugin.id}) deleted.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting plugin ID {plugin_id}: {e}")
        raise

def activate_plugin(db: Session, plugin_id: int) -> Plugin:
    plugin = get_plugin(db, plugin_id)
    if not plugin.is_active:
        plugin.is_active = True
        db.commit()
        db.refresh(plugin)
        logger.info(f"Plugin '{plugin.name}' activated.")
    return plugin

def deactivate_plugin(db: Session, plugin_id: int) -> Plugin:
    plugin = get_plugin(db, plugin_id)
    if plugin.is_active:
        plugin.is_active = False
        db.commit()
        db.refresh(plugin)
        logger.info(f"Plugin '{plugin.name}' deactivated.")
    return plugin

def get_active_plugins_summary(db: Session) -> str:
    active_plugins = db.query(Plugin.name).filter(Plugin.is_active == True).all()
    if not active_plugins:
        return "No plugins are currently active."
    return "Active plugins: " + ", ".join([name for (name,) in active_plugins]) + "."

def run_plugin_action(db: Session, plugin_name: str, action_name: str, project_context: dict, plugin_params: dict = None) -> str:
    # Заглушка — доработай под настоящую логику!
    plugin = get_plugin_by_name(db, plugin_name)
    if not plugin:
        return f"Error: Plugin '{plugin_name}' not found."

    if not plugin.is_active:
        return f"Error: Plugin '{plugin_name}' is not active. Please activate it first."

    logger.info(f"Attempting to run action '{action_name}' from plugin '{plugin_name}' for project: {project_context.get('name')}")
    additional_params = plugin_params or {}
    logger.info(f"Plugin action '{action_name}' for plugin '{plugin_name}' called with project_context keys: {list(project_context.keys())} and additional_params: {additional_params}")

    if plugin_name == "EchoTest" and action_name == "echo":
        message_to_echo = additional_params.get("message", "No message provided for echo.")
        return f"Plugin '{plugin_name}' simulated echoing: '{message_to_echo}' for project '{project_context.get('name')}'."

    return f"Plugin '{plugin_name}' action '{action_name}' called (simulated). Params: {additional_params}. Project: '{project_context.get('name')}'."
