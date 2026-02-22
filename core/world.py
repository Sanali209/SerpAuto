import uuid
from typing import Dict, Type, Set, List
from .component import BaseComponent
from .entity import Entity

class World:
    def __init__(self):
        # Structure: {ComponentClass: {EntityID: ComponentInstance}}
        self._components: Dict[Type[BaseComponent], Dict[Entity, BaseComponent]] = {}
        # Stores which entities have which component for fast lookup
        self._entities_with_component: Dict[Type[BaseComponent], Set[Entity]] = {}
        self._entities: Set[Entity] = set()

    def add_entity(self) -> Entity:
        ent = uuid.uuid4()
        self._entities.add(ent)
        return ent

    def add_component(self, entity: Entity, component: BaseComponent):
        comp_type = type(component)

        # Initialize storage for this component type if needed
        if comp_type not in self._components:
            self._components[comp_type] = {}
            self._entities_with_component[comp_type] = set()

        self._components[comp_type][entity] = component
        self._entities_with_component[comp_type].add(entity)

    def remove_component(self, entity: Entity, comp_type: Type[BaseComponent]):
        if comp_type in self._components and entity in self._components[comp_type]:
            del self._components[comp_type][entity]
            self._entities_with_component[comp_type].remove(entity)

    def get_component(self, entity: Entity, comp_type: Type[BaseComponent]):
        return self._components.get(comp_type, {}).get(entity)

    def get_components(self, comp_type: Type[BaseComponent]) -> Dict[Entity, BaseComponent]:
        """Returns all components of a specific type mapping Entity -> Component"""
        return self._components.get(comp_type, {})

    def get_entities_with(self, *component_types: Type[BaseComponent]) -> Set[Entity]:
        """Returns IDs of entities that have ALL requested components (Intersection)"""
        if not component_types:
            return set()

        # Start with the set of entities for the first component
        first_type = component_types[0]
        result_set = set(self._entities_with_component.get(first_type, set()))

        # Intersect with the rest (very fast in Python)
        for comp_type in component_types[1:]:
            result_set &= self._entities_with_component.get(comp_type, set())

        return result_set
