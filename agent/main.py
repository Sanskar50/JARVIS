import sys
import os

# Ensure the project root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_controller import AgentController


def main():
    print("Starting Agent Application...")
    controller = AgentController()
    # Example usage
    try:
        controller.run()
        response = controller.get_aqi("Lucknow")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
