
if __package__ == '':
    from visualizer import visualizer
else:
    from .visualizer import visualizer

if __name__ == '__main__':
    v = visualizer()
    v.start_event_loop()
