import uuid
from typing import Dict, Set, Type, Any, Tuple, TypeVar, Optional
from components.base import BaseComponent

Entity = uuid.UUID
T = TypeVar('T', bound=BaseComponent)

class World:
    def __init__(self):
        # Storage: {ComponentType: {EntityID: ComponentInstance}}
        self._components: Dict[Type[BaseComponent], Dict[Entity, BaseComponent]] = {}
        # Index: {ComponentType: set(EntityID)}
        self._entities_with_component: Dict[Type[BaseComponent], Set[Entity]] = {}
        # Query Cache: {Tuple[ComponentType]: set(EntityID)}
        self._queries: Dict[Tuple[Type[BaseComponent], ...], Set[Entity]] = {}
        # All Entities
        self._entities: Set[Entity] = set()

    def create_entity(self) -> Entity:
        """Creates a new entity ID."""
        entity = uuid.uuid4()
        self._entities.add(entity)
        return entity

    def delete_entity(self, entity: Entity):
        """Removes an entity and all its components."""
        if entity not in self._entities:
            return

        # Find all components attached to this entity
        # This is slow, maybe we need an entity -> components map?
        # For now, iterate component types.
        for comp_type in list(self._components.keys()):
            if entity in self._components[comp_type]:
                self.remove_component(entity, comp_type)

        self._entities.discard(entity)

    def add_component(self, entity: Entity, component: BaseComponent):
        """Adds a component to an entity and updates queries."""
        comp_type = type(component)

        # 1. Initialize storage for this type if needed
        if comp_type not in self._components:
            self._components[comp_type] = {}
            self._entities_with_component[comp_type] = set()

        # 2. Add to storage
        self._components[comp_type][entity] = component
        self._entities_with_component[comp_type].add(entity)

        # 3. Update active queries (Reactive Update)
        # Check if this entity now satisfies any existing query
        for query_sig, query_set in self._queries.items():
            if comp_type in query_sig:
                # If the entity has all components in the signature, add it
                if self.has_components(entity, *query_sig):
                    query_set.add(entity)

    def remove_component(self, entity: Entity, comp_type: Type[BaseComponent]):
        """Removes a component from an entity and updates queries."""
        if comp_type in self._components and entity in self._components[comp_type]:
            del self._components[comp_type][entity]
            self._entities_with_component[comp_type].discard(entity)

            # Update queries
            for query_sig, query_set in self._queries.items():
                if comp_type in query_sig:
                    query_set.discard(entity)

    def has_components(self, entity: Entity, *comp_types: Type[BaseComponent]) -> bool:
        """Checks if an entity has all specified component types."""
        for ct in comp_types:
            if ct not in self._components or entity not in self._components[ct]:
                return False
        return True

    def get_component(self, entity: Entity, comp_type: Type[T]) -> Optional[T]:
        """Retrieves a component instance for an entity."""
        return self._components.get(comp_type, {}).get(entity)

    def get_entities_with(self, *component_types: Type[BaseComponent]) -> Set[Entity]:
        """Returns a set of entities that have ALL specified components.

        Uses caching and set intersection for O(1) or O(N_small) performance.
        """
        if not component_types:
            return set()

        # Sort to ensure signature consistency (e.g. (A, B) == (B, A))
        signature = tuple(sorted(component_types, key=lambda x: x.__name__))

        # 1. Check Cache
        if signature in self._queries:
            return self._queries[signature]

        # 2. Compute Intersection (Cold Start)
        # Start with the smallest set ideally, but here we just take the first one
        first_type = signature[0]
        result = set(self._entities_with_component.get(first_type, set()))

        for ct in signature[1:]:
            result &= self._entities_with_component.get(ct, set())

        # 3. Cache the result
        self._queries[signature] = result
        return result
