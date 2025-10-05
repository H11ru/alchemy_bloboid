import pygame
from utilities import safemax

class Font:
    def __init__(self, surf=None, font=None, font_size=20, color=(255,255,255), border_color=(0,0,0), border_thickness=2, border_radius=0, bg_color=None, padding=4, wrap_width=None):
        self.font_size = font_size
        self.color = color
        self.border_color = border_color
        self.border_thickness = border_thickness
        self.border_radius = border_radius
        self.bg_color = bg_color
        self.padding = padding
        self.wrap_width = wrap_width
        self.surf = surf

        # is this a sysfont?
        try:
            self.font = pygame.font.Font(font, font_size)
        except:
            try:
                self.font = pygame.font.SysFont(font, font_size)
            except:
                self.font = pygame.font.SysFont(None, font_size)

    def bake_word_wraps(self, string, width):
        # Handles literal newlines and splits long words with hyphens if needed
        lines = []
        for paragraph in string.split('\n'):
            words = paragraph.split(' ')
            current_line = ""
            for word in words:
                # If the word itself is too long, split it with hyphens
                while self.font.size(word)[0] > width:
                    # Find max chars that fit
                    for i in range(1, len(word)+1):
                        if self.font.size(word[:i] + '-')[0] > width:
                            break
                    # If nothing fits, forcibly split at 1
                    split_at = max(1, i-1)
                    part = word[:split_at] + '-'
                    if current_line:
                        lines.append(current_line)
                        current_line = ""
                    lines.append(part)
                    word = word[split_at:]
                test_line = (current_line + " " + word) if current_line else word
                if self.font.size(test_line)[0] > width and current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)
            current_line = ""
        return lines

    def render(self, text, surface=None):
        # Handle word wrap and line breaks
        lines = self.bake_word_wraps(text, self.wrap_width) if self.wrap_width else text.split('\n')
        rendered_lines = [self._render_line(line) for line in lines]
        width = safemax([r.get_width() for r in rendered_lines])
        height = sum(r.get_height() for r in rendered_lines)

        if not self.surf:
            if not surface:
                surf = pygame.Surface((width + 2*self.padding, height + 2*self.padding), pygame.SRCALPHA)
            else:
                surf = surface
                surf.fill((0,0,0,0))
        else:
            surf = self.surf
            surf.fill((0,0,0,0))
        if self.bg_color:
            pygame.draw.rect(surf, self.bg_color, surf.get_rect(), border_radius=self.border_radius)

        y = self.padding
        for r in rendered_lines:
            surf.blit(r, (self.padding, y))
            y += r.get_height()
        return surf

    def _render_line(self, text):
        base = self.font.render(text, True, self.color)
        w, h = base.get_size()
        pad = self.border_thickness if self.border_thickness > 0 else 0
        surf = pygame.Surface((w + 2*pad, h + 2*pad), pygame.SRCALPHA)
        # Draw border
        if self.border_thickness > 0:
            for dx in range(-self.border_thickness, self.border_thickness+1):
                for dy in range(-self.border_thickness, self.border_thickness+1):
                    if dx == 0 and dy == 0:
                        continue
                    surf.blit(self.font.render(text, True, self.border_color), (dx+pad, dy+pad))
        # Draw main text
        surf.blit(base, (pad, pad))
        return surf

    def _wrap_text(self, text):
        if not self.wrap_width:
            return text.split('\n')
        words = text.split(' ')
        lines = []
        current = ""
        for word in words:
            test = current + (" " if current else "") + word
            if '\n' in word:
                parts = word.split('\n')
                for i, part in enumerate(parts):
                    if i == 0:
                        test = current + (" " if current else "") + part
                        if self.font.size(test)[0] > self.wrap_width and current:
                            lines.append(current)
                            current = part
                        else:
                            current = test
                    else:
                        lines.append(current)
                        current = part
                continue
            if self.font.size(test)[0] > self.wrap_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        return lines

# Example usage:
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 300))
    pygame.display.set_caption("Text API Demo")

    font_path = "c:/Users/juhor/Stuffs/test101/glyphs_ttf/blocky.ttf"
    renderer = Font(
        font=font_path,
        font_size=40,
        color=(255,255,255),
        border_color=(0,0,0),
        border_thickness=2,
        border_radius=10,
        bg_color=(30,30,30),
        padding=8,
        wrap_width=700
    )

    text = "The quick brown fox\njumped over the lazy dog. This is a long line that should wrap automatically!"
    surf = renderer.render(text)

    screen.fill((50, 50, 50))
    screen.blit(surf, (30, 30))
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()