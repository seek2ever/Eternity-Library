class HelloPython:
    """打印信息并进行简单问候"""
    def __init__(self, name, age):
        self.name = name
        self.age = age
        print(f"Hello {self.name} Python!")


people = HelloPython("Chris", 24)
print(people)
