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

## 5. Maintenance & Sync
*   **Roadmap Alignment**: Any new "Phase" or major system must be added to `roadmap.md` and `tasks.md`.
*   **Crosllinking**: When adding a new file, update the parent documentation or the "Design Overview" to link to it.
