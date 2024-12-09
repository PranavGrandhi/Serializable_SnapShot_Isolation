# variable.py
class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        # You can add more attributes here if needed

    def __repr__(self):
        return f"{self.name}: {self.value}"
