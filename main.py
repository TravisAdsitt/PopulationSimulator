from kivy.app import App
from kivy.uix import widget, button


class SimulationGUIApp(App):
    def run_sim(self):
        print("Running!")
    pass

if __name__ == "__main__":
    SimulationGUIApp().run()
