import sys
import os
import unittest

# Ensure root is in sys.path
sys.path.insert(0, os.getcwd())

# Discover and run specific tests
test_files = [
    'tests/test_perception_cv.py',
    'tests/test_cognitive_context.py',
    'tests/test_os_actions.py',
    'tests/test_actor_learner.py'
]

loader = unittest.TestLoader()
suite = unittest.TestSuite()

for test_file in test_files:
    if os.path.exists(test_file):
        # Convert path to module name
        module_name = test_file.replace('/', '.').replace('\\', '.').replace('.py', '')
        try:
            suite.addTests(loader.loadTestsFromName(module_name))
        except Exception as e:
            print(f"Failed to load {test_file}: {e}")

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
