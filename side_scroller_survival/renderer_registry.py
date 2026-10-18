"""Bind entity types to their renderers during game initialization."""

from __future__ import annotations

from entities import Bullet, Player, Zombie
from gun import Gun
from renderer import BulletRenderer, PlayerRenderer, ZombieRenderer


class RendererRegistry:
    """Store the renderer assigned to each supported entity type."""

    def __init__(self) -> None:
        self._renderers: dict[type[object], object] = {}

    def register(self, entity_type: type[object], renderer: object) -> None:
        """Bind one entity type to one renderer."""
        self._renderers[entity_type] = renderer

    @property
    def player(self) -> PlayerRenderer:
        """Return the renderer bound to the Player entity."""
        renderer = self._renderers[Player]
        if not isinstance(renderer, PlayerRenderer):
            raise RuntimeError("Player renderer is not registered")
        return renderer

    @property
    def bullet(self) -> BulletRenderer:
        """Return the renderer bound to the Bullet entity."""
        renderer = self._renderers[Bullet]
        if not isinstance(renderer, BulletRenderer):
            raise RuntimeError("Bullet renderer is not registered")
        return renderer

    @property
    def zombie(self) -> ZombieRenderer:
        """Return the renderer bound to the Zombie entity."""
        renderer = self._renderers[Zombie]
        if not isinstance(renderer, ZombieRenderer):
            raise RuntimeError("Zombie renderer is not registered")
        return renderer


def create_renderer_registry(gun: Gun) -> RendererRegistry:
    """Create the standard entity-to-renderer bindings for one game session."""
    registry = RendererRegistry()
    registry.register(Player, PlayerRenderer(gun))
    registry.register(Bullet, BulletRenderer(gun))
    registry.register(Zombie, ZombieRenderer())
    return registry
