from pyscript import Element
from pyscript import config
print(config.get("files"))
def print_hello(event):
        Element("output").write("Hello, World!")
        Element("helloBtn").element.onclick = print_hello
