from pygame import Rect
from pygame import transform
from pygame import draw
from pygame import image
from pygame import Surface

from pygame.font import Font
from pygame.font import init as init_font

# TODO: create a better abstract class.
class VisualElement:
    '''
    Base class for all visual elements.
    '''

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def get_rect(self):
        '''
        Get the rect of the element.
        '''
        return Rect(
            self.x, self.y,
            self.size, self.size
        )


class ImageButton (VisualElement):
    '''
    A button that displays an image. Performs an action when clicked.
    The image is resized to fit the button's size.
    '''

    def __init__(self, x, y, size, image=None):
        super().__init__(x, y, size)

        self.rect = None
        
        if image:
            self.set_image(image)
        else:
            self.image = None

    def set_image(self, image):
        '''
        Set the image of the button.

        Args:
            image (pygame.Surface): The image to use.
        '''
        self.image = transform.scale(image, (self.size, self.size))
        self.rect = Rect(
            self.x, self.y,
            self.image.get_width(), self.image.get_height()
        )

    def draw(self, screen):
        '''
        Draw the button on the screen.
        '''
        screen.blit(self.image, (self.x, self.y))


class PatternSlider (VisualElement):
    '''
    A slider used to select a pattern. Patterns are displayed one at a time
    and can be cycled through. ImageButtons are used to navigate the slider.
    '''
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

        self.patterns = []
        self.names = []

        self.index = 0

        self.prev_button = ImageButton(
            self.x - (self.size // 2) - 10,
            self.y + (self.size // 4),
            self.size // 2)
        self.prev_button.set_image(image.load('assets/img/back-bttn.png'))

        self.next_button = ImageButton(
            self.x + self.size + 10,
            self.y + (self.size // 4),
            self.size // 2)
        self.next_button.set_image(image.load('assets/img/next-bttn.png'))

        init_font()
        self.font = Font('assets/font/Pixellari.ttf', 16)

    def add_pattern(self, pattern):
        '''
        Add a pattern to the slider.
        '''
        self.patterns.append(pattern)
        
        self.names.append(
            self.font.render(pattern.name, True, (255, 255, 255))
        )

    def selected(self):
        '''
        Get the selected item.
        '''
        return self.patterns[self.index]

    def next(self):
        '''
        Select the next item.
        '''
        self.index = (self.index + 1) % len(self.patterns)

    def previous(self):
        '''
        Select the previous item.
        '''
        self.index = (self.index - 1) % len(self.patterns)

    def draw_layout(self, x, y, screen):
        '''
        Draw the layout of the selected item.
        '''

        # TODO: center the pattern in the slider (horizontally)
        current_pattern = self.patterns[self.index]
        cell_size = self.size // current_pattern.size

        for rows in current_pattern.layout:
            for cell in rows:
                if cell:
                    draw.rect(
                        screen,
                        (255, 255, 255),
                        (x, y, cell_size, cell_size))
                x += cell_size
            x = self.x
            y += cell_size

    def draw(self, screen):
        '''
        Draw the slider on the screen.
        '''

        self.draw_layout(self.x, self.y, screen)

        self.next_button.y = self.y + (self.size // 4)
        self.prev_button.y = self.y + (self.size // 4)

        self.next_button.draw(screen)
        self.prev_button.draw(screen)
        
        screen.blit(
            self.names[self.index], 
            (self.x + (self.size // 2) - (self.names[self.index].get_width() // 2), 
            self.y + self.size + 10))


class Panel (VisualElement):
    '''
    A simple background panel that is drawn behind other graphical elements.
    '''

    def __init__(self, x, y, width, height, color, alpha):
        super().__init__(x, y, {'w': width, 'h': height})
        
        self.color = color
        self.alpha = alpha
        
        self.panel = Surface((self.size['w'], self.size['h']))
        self.panel.fill(self.color)
        self.panel.set_alpha(self.alpha)

    def set_width(self, width):
        '''
        Set the width of the panel.
        '''
        self.size['w'] = width
        self.panel = Surface((self.size['w'], self.size['h']))
        self.panel.fill(self.color)
        self.panel.set_alpha(self.alpha)

    def draw(self, screen):
        '''
        Draw the panel on the screen.
        '''

        screen.blit(self.panel, (self.x, self.y))


class MenuBar (VisualElement):
    '''
    A MenuBar is a panel at the top of the screen that contains several menus.
    Each menu has it's own set of menu items.
    The menus are displayed horizontally in the order they were added.
    '''

    def __init__(self, width, height, color):
        super().__init__(0, 0, {'w': width, 'h': height})
        self.background = Panel(0, 0, self.size['w'], self.size['h'], color, 255)

        self.menus = []

        self.active_menu = None

    def add_menu(self, menu):
        '''
        Adds a menu to the MenuBar and calculates it's position.
        '''
        self.menus.append(menu)

        curr_x = self.x
        pad = 10
        for menu in self.menus:
            menu.x = curr_x + pad // 2
            menu.y = self.y + (self.size['h'] // 4)
            menu._position_items()

            curr_x += menu.text.get_width() + pad
    
    def clicked_menu(self, pos):
        '''
        Determines wich menu on the bar was clicked. Or if none were clicked.
        This method is called per mouse click.
        '''

        x, y = pos

        if y > self.size['h']:
            self.active_menu = False
            return
        
        pad = 10
        for menu in self.menus:            
            if x < menu.x + menu.text.get_width() + pad:
                if self.active_menu:
                    self.active_menu.is_active = False
                self.active_menu = menu
                self.active_menu.is_active = True
                return
        
        self.active_menu = False

    def draw(self, screen):
        '''
        Render the MenuBar on the screen.
        '''

        self.background.draw(screen)

        for menu in self.menus:
            screen.blit(menu.text, (menu.x, menu.y))
        
        if self.active_menu:
            self.active_menu.draw(screen)



class Menu():
    '''
    A Menu is a list of menu items that perform actions when clicked.
    The items are displayed vertically in the order they were added.

    A Menu is meant to be used in a MenuBar.
    '''

    def __init__(self, text):
        self.x = None
        self.y = None
        
        init_font()
        self.font = Font('assets/font/Pixellari.ttf', 18)

        self.text = self.font.render(text, True, (255, 255, 255))
        self.items = []

        self.background = None

        self.is_active = False
    
    def add_item(self, item):
        '''
        Adds an item to the menu. If the item is another Menu, the item
        becomes a submenu. If it is a MenuItem, the item is a clickable
        button.
        '''
        # TODO: check if item is Menu or MenuItem
        item.default_text = self.font.render(item.text, True, (255, 255, 255))
        item.hover_text = self.font.render(item.text, True, (100, 120, 175))
        
        item.text = item.default_text

        self.items.append(item)

    def _position_items(self):
        '''
        Private function that position all of the menu's items.
        Called after the y value of the MenuBar is passed to the Menu. 
        '''
        curr_y = self.y + self.text.get_height() + 10
        max_width = 0
        
        for item in self.items:
            item.x = self.x + 5
            item.y = curr_y
            
            if item.text.get_width() > max_width:
                max_width = item.text.get_width()

            curr_y += item.text.get_height() + 15
        
        for item in self.items:
            item.width = max_width

        self.background = Panel(
            self.x, self.y + self.text.get_height(), max_width + 15, 
            curr_y - (self.y + self.text.get_height()) - 10,
            (11, 20, 26), 255)

    def draw(self, screen):
        self.background.draw(screen)
        for item in self.items:
            screen.blit(item.text, (item.x, item.y))


class MenuItem():
    '''
    A MenuItem works like a button in the sense that it performs an action when clicked.
    '''
    def __init__(self, text):
        self.x = None
        self.y = None
        self.width = None

        self.text = text

        self.default_text = None
        self.hover_text = None
    
    def hover(self, pos):
        x, y = pos
        if x > self.x and x < self.x + self.width:
            if y > self.y and y < self.y + self.text.get_height() + 5:
                return True
        return False
        