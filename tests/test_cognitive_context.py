import unittest
import json
from components.core import PerceptionComponent, MemoryComponent
from brain.adapters_impl import ContextBuilder

class TestCognitiveContext(unittest.TestCase):
    def test_context_builder(self):
        perception = PerceptionComponent()
        perception.visible_entities = [{"box": [0,0,10,10], "label": "test"}]
        perception.raw_context = {"screen_size": [1920, 1080]}
        
        memory = MemoryComponent()
        memory.blackboard = {"goal": "survive"}
        memory.history = ["action1", "action2"]
        
        prompt = ContextBuilder.build_prompt(perception, memory)
        data = json.loads(prompt)
        
        self.assertIn("perception", data)
        self.assertIn("blackboard", data)
        self.assertEqual(data["blackboard"]["goal"], "survive")
        self.assertEqual(len(data["recent_actions"]), 2)

if __name__ == '__main__':
    unittest.main()
