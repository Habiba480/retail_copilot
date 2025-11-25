from .agent.graph_hybrid import repair_loop
import json

if __name__ == "__main__":
    # Interactive single question
    question = input("Enter a question: ")
    result = repair_loop(question)
    print(json.dumps(result, indent=2))
