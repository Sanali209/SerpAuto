# Production Mode

**Production Mode** is designed for high-performance, headless deployment of agents in "live" environments (e.g., scraping at scale, server-side automation).

## ⚙️ Configuration & Orchestration

In **Production Mode**, the engine boots only the core logic and telemetry systems. It uses the **Registry V2** to filter for systems compatible with `EngineMode.PRODUCTION`.

### Typical Systems
- **`TelemetrySystem`**: Performance metrics and health-checks.
- **`MessageRouterSystem`**: Standardized swarm communication.
- **`AI_BrainSystem`**: Core cognitive execution.

## 🌐 External API

When launched with `--api`, the engine starts a FastAPI server. This allows external tools to:
- **Query State**: Get JSON representations of entities.
- **Inject Actions**: Force an agent to take a specific action via the `ActionBufferComponent`.
- **Receive Events**: Subscribe to high-level domain events.

## 🚀 Launching
```bash
python main.py --mode PRODUCTION --api --headless
```

---

## 🏎️ Performance Considerations

Production mode is optimized for:
1. **CPU Efficiency**: No overhead from OpenGL or UI handling.
2. **Async I/O**: Maximum utilization of `asyncio` for multi-agent scaling.
3. **Telemetry**: Minimal logging overhead with structured output.
