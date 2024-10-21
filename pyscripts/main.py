        from pyscript import Element

        # Function to print "Hello, World!" (it must accept the event argument)
        def print_hello(event):
            Element("textvalue1").write("Hello, World!")

        # Bind the print_hello function to the button's click event
        Element("run").element.onclick = print_hello
