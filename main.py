from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from game_objects import Food, Person
from world import World, LocationManager
from kivy.logger import Logger, LOG_LEVELS

Logger.setLevel(LOG_LEVELS["critical"])

class SimulationViewport(Widget):
    pass

class SimulationController(Widget):
    pass
        
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = "vertical"
        
        self.sim_view = SimulationViewport(size_hint=(1,.7), pos=(100,50))
        
        self.add_widget(self.sim_view)
        self.add_widget(SimulationController(size_hint=(1, .3)))

class SimulationGUIApp(App):
    def build(self):
        main_screen = MainScreen(size=(1000,1000))

        self.sim_view = main_screen.sim_view

        return main_screen
        
    def run_sim(self, num_people: int, num_food: int):
        self.current_simulation = World(num_people, num_food)
        self.current_sim_event = Clock.schedule_interval(self.tick_sim, 1/30)
    
    def tick_sim(self, dt):
        if not hasattr(self, "current_simulation"):
            return
        
        self.current_simulation.tick()

        self.draw_simulation()

    def draw_simulation(self):
        screen_width = self.sim_view.width
        screen_height = self.sim_view.height

        world_width = self.current_simulation.world_width
        world_height = self.current_simulation.world_height

        block_width = screen_width // world_width
        block_height = screen_height // world_height

        self.sim_view.canvas.clear()

        location_manager = self.current_simulation.location_manager
        things = location_manager.things

        color_floor = 0.3

        for thing in things:
            x,  y = location_manager.get_thing_coordinates(thing)

            with self.sim_view.canvas:
                if isinstance(thing, Food):
                    color_strength = thing.Amount / thing.MaxAmount
                    color_strength = max([color_floor, color_strength])

                    Color(0.,color_strength,0.)
                elif isinstance(thing, Person):
                    color_strength = thing.Energy / thing.EnergyMax
                    color_strength = max(color_floor, color_strength)
                    if thing.alive:
                        Color(color_strength,0.,0.)
                    else:
                        Color(0.,0.,1.)
                
                pos_screen_x = x * block_width + self.sim_view.pos[0]
                pos_screen_y = y * block_height + self.sim_view.pos[1]

                Rectangle(pos=(pos_screen_x, pos_screen_y), size=(block_width, block_height))

    


if __name__ == "__main__":

    SimulationGUIApp().run()
