from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty, OptionProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle
from math import sin, cos, sqrt
from random import randint

class PivotGame(Widget):
    """Pivot Game"""

    # Getting references to widgets from kv file
    ball = ObjectProperty(None)
    menu = ObjectProperty(None)
    score_label = ObjectProperty(None)
    score_label2 = ObjectProperty(None)
    target = ObjectProperty(None)
    # Game states
    state = OptionProperty("started", options=["playing","killed"])
    # Score counter
    score = NumericProperty(-1)

    number_of_opponents = [2,3,5,7,11,13,17,19,23,29,31,37,41,43]
    level = 0
    opponents = []

    def update(self, dt):
        """Run the game

        It does:
            - checks if ball is touch wall
            - show labels based on game state
            - moves the ball
            - moves the target
            - counts score
        """

        if self.ball.is_touching_border():
            self.state = "killed"
            self.ball.reset_position()

        if self.state == "started":
            self.menu.canvas.opacity = 1
            self.ball.canvas.opacity = 0
            self.score_label.canvas.opacity = 0
            self.target.canvas.opacity = 0

        elif self.state == "playing":

            if self.ball.is_touching(self.target):
                self.target.move()
                self.score += 1
                if self.score % 5 == 0:
                    self.level += 1

            self.menu.canvas.opacity = 0
            self.ball.canvas.opacity = 1
            self.score_label.canvas.opacity = 0
            self.target.canvas.opacity = 1
            self.ball.move(dt)
            self.set_score(self.score)

            for o in self.opponents:
                if self.ball.is_touching(o):
                    self.state = "killed"
                    print self.ball.pos, self.ball.size
                    print o.pos, o.size
                o.move()

        elif self.state == "killed":
            self.menu.canvas.opacity = 1
            self.ball.canvas.opacity = 0
            self.set_score(self.score)
            self.score_label.canvas.opacity = 1
            self.target.canvas.opacity = 0
            self.target.move()

            for o in self.opponents:
                self.remove_widget(o)
            self.opponents = []

    def update_opponent(self, dt):
        if self.state == "started":
            pass
        elif self.state == "playing":
            if len(self.opponents) < self.number_of_opponents[self.level]:
                p = (-50,randint(0,self.parent.height))
                temp_op = PivotOpponent(pos=p, size=(50,50))
                self.add_widget(temp_op,9999)
                self.opponents.append(temp_op)
        elif self.state == "killed":
            pass

    def set_score(self, num):
        """Set score on label in corner and label at the end"""
        self.score_label.text = "Score " + str(num)
        self.score_label2.text = "Score " + str(num)

class PivotApp(App):
    """Pivot App"""

    def build(self):
        """Create Game

        It create game, set scheduled running of update and listen to keyboard.
        """
        self.game = PivotGame()

        Clock.schedule_interval(self.game.update, 1.0/30.0)

        Clock.schedule_interval(self.game.update_opponent, 5.0)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        self._keyboard.bind(on_key_up = self._on_keyboard_up)

        return self.game

    def _keyboard_closed(self):
        """Not quiet sure..."""
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Start game whenn spacebar pressed"""
        if keycode[1] == 'spacebar':
            if self.game.state == "started":
                self.game.state = "playing"
            elif self.game.state == "killed":
                self.game.score = 0
                self.game.state = "playing"
            elif self.game.state == "playing":
                self.game.ball.turn()

    def _on_keyboard_up(self, *args):
        """No action set on key up"""
        pass

class PivotBall(Widget):
    """Player's ball widget"""

    angle = NumericProperty(0)
    r = NumericProperty(5.5)
    was_turn = BooleanProperty(True)
    border = NumericProperty(10)

    def reset_position(self):
        """Reset ball to center and initial behaviour"""
        self.x = self.parent.center_x - self.size[0]
        self.y = self.parent.center_y
        self.was_turn = BooleanProperty(True)
        self.angle = 0

    def is_touching_border(self):
        """Check if ball is touching border"""
        if (self.x < self.border or
            self.x + self.size[0] > self.parent.width - self.border):
            return True
        elif (self.y < self.border or
            self.y + self.size[1] > self.parent.height - self.border):
            return True
        else:
            return False

    def is_touching(self, other_object):
        """Check if ball and target center are in touching distance"""
        dist = sqrt((self.center[0] - other_object.center[0]) ** 2 +
                    (self.center[1] - other_object.center[1]) ** 2)
        touch_dist_x = self.size[0] / 2 + other_object.size[0] / 2
        touch_dist_y = self.size[1] / 2 + other_object.size[1] / 2

        if (dist < touch_dist_x or dist < touch_dist_y):
            return True

    def move(self, dt):
        """Move ball in circle"""
        if self.was_turn:
            self.angle += 0.1
        else:
            self.angle -= 0.1
        self.x = self.x + sin(self.angle) * self.r
        self.y = self.y + cos(self.angle) * self.r


    def turn(self):
        """Make ball to circle in oposite direction"""
        self.was_turn = not self.was_turn

class PivotTarget(Widget):
    """Target ball that player is chasing"""

    def move(self):
        """Move target ball within the window"""
        i = 10
        self.x = randint(self.size[0] + i,
                                self.parent.width - self.size[0] - i)
        self.y = randint(self.size[0] + i,
                                self.parent.height - self.size[0] - i)

class PivotOpponent(Widget):

    speed = NumericProperty(5)

    def move(self):
        if (self.x - self.size[0] > self.parent.width or
            self.x + self.size[0] < 0):
            self.x -= self.speed
            self.speed *= -1
            self.y = randint(0,self.parent.height)

        self.x += self.speed



if __name__ == '__main__':
    PivotApp().run()
