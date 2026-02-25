from typing import Dict, Set, Type, TypeVar, Optional, Tuple, Iterator, List
from uuid import UUID

from serpentine.core.entity import EntityID, create_entity_id
from serpentine.core.component import BaseComponent
from serpentine.utils.logging import configure_logging

logger = configure_logging()

T = TypeVar("T", bound=BaseComponent)

class World:
    def __init__(self):
        self._entities: Set[EntityID] = set()
        # Map ComponentType -> {EntityID -> ComponentInstance}
        self._components: Dict[Type[BaseComponent], Dict[EntityID, BaseComponent]] = {}
        # Cache for query results: Tuple[ComponentType, ...] -> Set[EntityID]
        self._query_cache: Dict[Tuple[Type[BaseComponent], ...], Set[EntityID]] = {}

    def create_entity(self, uid: Optional[UUID] = None) -> EntityID:
        entity_id = EntityID(uid) if uid else create_entity_id()
        self._entities.add(entity_id)
        logger.debug(f"Entity created: {entity_id}")
        return entity_id

    def delete_entity(self, entity_id: EntityID):
        if entity_id not in self._entities:
            return

        # Remove all components associated with this entity
        # We need to find which component types this entity has.
        # This is slightly inefficient if we don't store a reverse map or list of components per entity.
        # Optimization: Store Dict[EntityID, Set[Type[BaseComponent]]]
        # But for now, iterating over _components is O(NumComponentTypes), which is small.

        components_to_remove = []
        for comp_type, entities in self._components.items():
            if entity_id in entities:
                components_to_remove.append(comp_type)

        for comp_type in components_to_remove:
            self.remove_component(entity_id, comp_type)

        self._entities.remove(entity_id)
        logger.debug(f"Entity deleted: {entity_id}")

    def add_component(self, entity_id: EntityID, component: BaseComponent):
        if entity_id not in self._entities:
            raise ValueError(f"Entity {entity_id} does not exist.")

        comp_type = type(component)
        if comp_type not in self._components:
            self._components[comp_type] = {}

        self._components[comp_type][entity_id] = component

        # Invalidate queries containing this component type
        self._invalidate_queries(comp_type)

    def remove_component(self, entity_id: EntityID, component_type: Type[BaseComponent]):
        if component_type in self._components and entity_id in self._components[component_type]:
            del self._components[component_type][entity_id]
            self._invalidate_queries(component_type)

    def get_component(self, entity_id: EntityID, component_type: Type[T]) -> Optional[T]:
        if component_type in self._components:
            return self._components[component_type].get(entity_id) # type: ignore
        return None

    def get_components(self, component_type: Type[T]) -> Dict[EntityID, T]:
        """
        Returns all components of a specific type as a dictionary {EntityID: Component}.
        """
        return self._components.get(component_type, {}) # type: ignore

    def has_component(self, entity_id: EntityID, component_type: Type[BaseComponent]) -> bool:
        return component_type in self._components and entity_id in self._components[component_type]

    def _invalidate_queries(self, changed_component_type: Type[BaseComponent]):
        """Invalidates cache for any query involving the changed component type."""
        keys_to_remove = []
        for query_key in self._query_cache.keys():
            if changed_component_type in query_key:
                keys_to_remove.append(query_key)

        for key in keys_to_remove:
            del self._query_cache[key]

    def get_entities_with(self, *component_types: Type[BaseComponent]) -> Iterator[Tuple[EntityID, ...]]:
        """
        Efficiently retrieves entities having all specified components.
        Returns an iterator of (EntityID, component1, component2, ...).
        """
        if not component_types:
            return iter([])

        # Check cache
        cache_key = tuple(sorted(component_types, key=lambda t: t.__name__))

        if cache_key in self._query_cache:
            entity_ids = self._query_cache[cache_key]
        else:
            # Perform intersection
            # Start with the smallest set for efficiency
            sorted_types = sorted(component_types, key=lambda t: len(self._components.get(t, {})))

            # Get the set of IDs for the first (smallest) component type
            first_type = sorted_types[0]
            if first_type not in self._components:
                self._query_cache[cache_key] = set()
                return iter([])

            entity_ids = set(self._components[first_type].keys())

            # Intersect with the rest
            for comp_type in sorted_types[1:]:
                if comp_type not in self._components:
                    entity_ids = set()
                    break
                entity_ids.intersection_update(self._components[comp_type].keys())

            self._query_cache[cache_key] = entity_ids

        # Yield results
        # We need to return the components in the order requested in the arguments, not sorted key order
        for entity_id in entity_ids:
            components = []
            try:
                for comp_type in component_types:
                    components.append(self._components[comp_type][entity_id])
                yield (entity_id, *components)
            except KeyError:
                # Should not happen if cache logic is correct and single-threaded,
                # but might if modified during iteration (which is unsafe anyway)
                continue
