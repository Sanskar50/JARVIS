import sys
import os

# Ensure the project root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_controller import AgentController
from agent.observability.tracing import logger

def main():
    logger.info("Starting Agent Application...")
    controller = AgentController()
    
    # Example usage
    try:
        controller.run()
        # In a real loop, you might accept input from CLI or API
        response = controller.process_request("Hello Agent")
        print(response)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
