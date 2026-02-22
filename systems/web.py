from core.system import BaseSystem
from core.world import World
from components.standard import DOMNodeComponent, PayloadExtractionComponent

class WebExtractionSystem(BaseSystem):
    """Simulates extracting data from DOM nodes."""

    async def update(self, world: World, dt: float):
        # Find all nodes marked for extraction
        targets = world.get_entities_with(DOMNodeComponent, PayloadExtractionComponent)

        for ent in targets:
            dom_node = world.get_component(ent, DOMNodeComponent)
            payload = world.get_component(ent, PayloadExtractionComponent)

            if dom_node and payload:
                # Simulated logic: if class is "price-tag", extract price
                if dom_node.attributes.get("class") == "price-tag":
                    if not payload.validation_status:
                        payload.extracted_data["price"] = dom_node.extracted_text
                        payload.validation_status = True
