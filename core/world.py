import uuid
import json
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

    def clear(self):
        """Removes all entities and components from the world"""
        self._entities.clear()
        self._components.clear()
        self._entities_with_component.clear()

    def add_entity(self, uid: uuid.UUID = None) -> Entity:
        """Add a new entity. If uid is provided, use it (for deserialization)."""
        ent = uid if uid else uuid.uuid4()
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

    def serialize(self) -> str:
        """Dump entire world state to JSON string."""
        state = {
            "entities": [str(e) for e in self._entities],
            "components": {}
        }

        for comp_type, entity_map in self._components.items():
            class_name = comp_type.__name__
            state["components"][class_name] = {}
            for entity_id, comp_instance in entity_map.items():
                # Use Pydantic's model_dump to serialize
                # mode='json' is CRITICAL to serialize UUIDs to strings automatically
                state["components"][class_name][str(entity_id)] = comp_instance.model_dump(mode='json')

        return json.dumps(state, indent=2)

    def deserialize(self, json_str: str, component_registry: Dict[str, Type[BaseComponent]]):
        """Restore world state from JSON string."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")

        self.clear()

        # 1. Restore Entities
        for entity_str in data.get("entities", []):
            self.add_entity(uid=uuid.UUID(entity_str))

        # 2. Restore Components
        components_data = data.get("components", {})
        for class_name, entity_map in components_data.items():
            if class_name not in component_registry:
                print(f"Warning: Component class '{class_name}' not found in registry. Skipping.")
                continue

            comp_class = component_registry[class_name]

            for entity_id_str, comp_data in entity_map.items():
                try:
                    entity_id = uuid.UUID(entity_id_str)
                    if entity_id not in self._entities:
                        # Should have been created in step 1, but safe to add if missing
                        self.add_entity(uid=entity_id)

                    # Use Pydantic's model_validate to reconstruct
                    comp_instance = comp_class.model_validate(comp_data)
                    self.add_component(entity_id, comp_instance)
                except Exception as e:
                    print(f"Error deserializing {class_name} for {entity_id_str}: {e}")
