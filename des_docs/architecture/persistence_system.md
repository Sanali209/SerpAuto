# Persistence System

The Persistence System (`systems/persistence.py`) handles the serialization and restoration of the engine's state. It is critical for "Time Travel" debugging, saving agent workflows, and snapshotting learning environments.

## 💾 World Snapshots

The system can serialize the entire ECS `World` state into a JSON format.

### Serialization Flow
1. **Iterate**: The system iterates over all registered component types in the `World`.
2. **Serialize**: Each component (a Pydantic model) is serialized using its `model_dump()`.
3. **Map**: A map is built: `{ComponentClass: {EntityID: ComponentData}}`.

### API
- `PersistenceSystem.snapshot_world(world, filepath)`: Saves the current world state.
- `PersistenceSystem.load_snapshot(world, filepath)`: Restores the world state.

---

## 🗺️ Project Blueprints

Blueprints store logic-level configurations that are not tied to specific entity instances, such as:
- **Behavior Tree** definitions (JSON).
- **Perception Pipeline** DAG configurations.

### API
- `PersistenceSystem.save_blueprint(config_data, filepath)`
- `PersistenceSystem.load_blueprint(filepath) -> dict`

---

## ⏳ Time Travel Debugging

By combining snapshots and blueprints, the engine can "Rewind" state:
1. **Pause**: The tick loop is stopped.
2. **Load**: A previous snapshot is loaded into the `World`.
3. **Resume**: The engine continues ticking from the restored state.

> [!IMPORTANT]
> When loading a snapshot, all existing entities in the `World` are cleared. Ensure any unsaved state is snapshotted before loading.
