import os

KEY_FILE: str = ".deepeval"
PYTEST_RUN_TEST_NAME: str = "CONFIDENT_AI_RUN_TEST_NAME"
LOGIN_PROMPT = "\n✨ View your evaluation results in the local dashboard at http://localhost:8501 🎉"
RESULTS_DIR = os.path.join(os.getcwd(), ".deepeval_results")
