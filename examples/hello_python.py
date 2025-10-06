print("Hello, World!")

try:
    name = input("Enter your name: ")
    print(f"Hello, {name}! Welcome to UMLC!")
except EOFError:
    print("Hello, User! Welcome to UMLC! (Running in non-interactive mode)")
except Exception as e:
    print(f"An error occurred: {e}")

print("Program completed successfully!")
