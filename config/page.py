from config.paths import BasePaths

with open(BasePaths.container_stylesheet, 'r') as file:
    head_style = f"<style>\n" + file.read() + "\n</style>"
