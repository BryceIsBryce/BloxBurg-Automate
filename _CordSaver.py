from pynput import mouse, keyboard
from typing import List, Tuple

class MouseCoordinateLogger:
    def __init__(self):
        self.Coordinates: List[Tuple[int, int]] = []
        self.MouseListener = mouse.Listener(on_move=self.OnMouseMove)
        self.KeyboardListener = keyboard.Listener(on_press=self.OnKeyPress)

    def OnMouseMove(self, x, y):
        self.CurrentPosition = (x, y)

    def OnKeyPress(self, key):   
        if key == keyboard.Key.space:
            self.Coordinates.append(self.CurrentPosition)
            print(f"Coordinate logged: {self.CurrentPosition}")
        elif key == keyboard.Key.esc:
            # Stop listener
            return False

    def Start(self):
        with self.MouseListener as mListener, self.KeyboardListener as kListener:
            mListener.join()
            kListener.join()

if __name__ == "__main__":
    Logger = MouseCoordinateLogger()
    Logger.Start()
   