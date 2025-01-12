from MainWidget import gui
        
if __name__ == '__main__':
    try:
        gui_ = gui()
    except KeyboardInterrupt as e:
        gui.config.save_config()
        print("Saving config")