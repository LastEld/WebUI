# app/core/exceptions.py

class ProjectValidationError(Exception):
    pass

class ProjectNotFound(Exception):
    pass

class DuplicateProjectName(Exception):
    pass

class TaskValidationError(Exception):
    pass

class TaskNotFound(Exception):
    pass

class UserValidationError(Exception):
    pass

class TeamValidationError(Exception):
    pass

class PluginValidationError(Exception):
    pass

class PluginNotFoundError(Exception):
    pass

class SettingsValidationError(Exception):
    pass

class AuthValidationError(Exception):
    pass

class AIContextValidationError(Exception):
    pass

class DevLogValidationError(Exception):
    pass

class DevLogNotFound(Exception):
    pass

class JarvisValidationError(Exception):
    pass

class TemplateValidationError(Exception):
    pass
