def say_hello(name: str, age: int):
    print(f"Hello {name}!, you are {age} years old.")

# Action Registry
ACTIONS = {
    "say_hello": say_hello,
}