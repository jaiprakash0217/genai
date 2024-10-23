from pyscript import Element
def print_hello(event):
        Element("output").write("Hello, World!")
        Element("helloBtn").element.onclick = print_hello
