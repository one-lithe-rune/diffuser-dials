from config.args import paths

with open(paths.container_stylesheet, "r") as file:
    head_style = f"<style>\n{file.read()}\n</style>"
