# Serpentine Engine: Developer Documentation Standards

To maintain a high-quality, searchable, and consistent technical knowledge base for the project, all documentation in `des_docs/` must follow these rules.

## 1. Filenaming Convention
*   **Snake Case**: Use `snake_case.md` for all files (e.g., `ecs_hierarchy.md`, not `ECSHierarchy.md` or `ecs hierarchy.md`).
*   **No Spaces**: Never use spaces in filenames.
*   **Meaningful Names**: Filenames should reflect the technical component or system being described.

## 2. Directory Structure
Documentation should be organized into the following sub-directories:
*   `/architecture/`: High-level engine design, ECS patterns, and core systems.
*   `/modes/`: Deep dives into specific engine operation modes (Play, Gym, Teacher).
*   `/api_ml/`: Technical specs for perception nodes, LLM adapters, and MLOps pipelines.
*   `/planning/`: Project tracking, roadmaps, and task logs.

## 3. Document Structure
Every design document should ideally contain the following sections:
1.  **Overview**: 1-2 sentences explaining the purpose of the component/system.
2.  **Architecture/Concept**: High-level explanation of how it works.
3.  **Implementation Details**: Specific code snippets, component definitions (Pydantic), or system logic.
4.  **Cross-Links**: Links to related documents.

## 4. Language & Tone
*   **Primary Language**: Documentation should be primarily in **English** or clearly marked if bilingual. Technical terms (ECS, Component, Node) must always be in English.
*   **Tone**: Professional and technical. Avoid conversational logs (chat outputs) in final design documents unless as a "Design Discovery" appendix.
*   **Formatting**: Use GitHub-flavored Markdown. Bold important components like `TransformComponent`.

## 6. Standardized Terminology
To ensure the engine speaks a unified language, use the following terms in all documentation:
- **Observation**: Output of Perception (What the agent sees).
- **Intent**: Output of Mind (What the agent wants).
- **Command**: Output of Execution (What the engine does).
- **Snapshot**: A serialized World state for persistence.
- **Registry V2**: The metadata discovery layer for systems and components.
