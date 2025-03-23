from chatbot import ChatBot


def main():
    # Initialize the chatbot with our training data
    chatbot = ChatBot()

    print("ChatBot initialized! Type 'quit' to exit.")
    print("-" * 50)

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("ChatBot: Goodbye!")
            break

        # Get response from chatbot
        response = chatbot.get_response(user_input)
        print(f"ChatBot: {response}")
        print("-" * 50)


if __name__ == "__main__":
    main()
