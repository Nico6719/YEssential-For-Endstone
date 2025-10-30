from .main import YEssentialPlugin

def create_plugin():
    return YEssentialPlugin()

__all__ = [
    'YEssentialPlugin',
    'create_plugin'
]
