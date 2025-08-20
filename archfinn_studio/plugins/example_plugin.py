# plugins/example_plugin.py
def custom_action(state, args):
    print(f"[PLUGIN] Running custom action with args: {args}")
    return True  # success