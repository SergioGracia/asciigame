import curses
from ...core.state import WorldState
from ...core.logger import logger
from ...core.entities.person import Person
from ...core.entities.town import Town

class CursesRenderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.map_win = None
        self.stat_win = None
        self.log_win = None
        self.camera_focus = None
        self.show_legend = False
        
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN) # MEADOW
            curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_GREEN) # FOREST
            curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLUE)  # WATER
            curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_YELLOW)# DESERT
            
        self._init_windows()

    def _init_windows(self):
        self.stdscr.erase()
        sh, sw = self.stdscr.getmaxyx()
        if sh < 20 or sw < 80: return
        top_h = int(sh * 0.65)
        log_h = sh - top_h - 2
        map_w = int(sw * 0.65)
        stat_w = sw - map_w
        self.map_win = curses.newwin(top_h, map_w, 0, 0)
        self.stat_win = curses.newwin(top_h, stat_w, 0, map_w)
        self.log_win = curses.newwin(log_h, sw, top_h, 0)
        self.stdscr.refresh()

    def render(self, world_state: WorldState):
        sh, sw = self.stdscr.getmaxyx()
        if not self.map_win: self._init_windows(); return

        self.map_win.erase()
        self.stat_win.erase()
        self.log_win.erase()
        
        people = [e for e in world_state.get_all_entities() if isinstance(e, Person)]
        if not self.camera_focus and people: self.camera_focus = people[0]

        cam_x, cam_y = int(self.camera_focus.x), int(self.camera_focus.y)
        mh, mw = self.map_win.getmaxyx()
        mid_x, mid_y = mw // 2, mh // 2
        scenario = world_state.scenario
        is_night = world_state.is_night()
        
        # 1. MAPA Y CONSTRUCCIONES
        for wy in range(cam_y - mid_y, cam_y + mid_y):
            for wx in range(cam_x - mid_x, cam_x + mid_x):
                ex, ey = mid_x + wx - cam_x, mid_y + wy - cam_y
                if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                    biome_id = scenario.get_biome_id(wx, wy)
                    stats = scenario.get_biome_stats(biome_id)
                    char, pair_id = stats.get("char", " "), stats.get("pair_id", 10)
                    attr = curses.A_DIM
                    
                    if (wx, wy) in world_state.built_structures:
                        struct = world_state.built_structures[(wx, wy)]
                        char, pair_id, attr = struct["char"], 5, curses.A_BOLD
                    
                    try: self.map_win.addch(ey, ex, char, attr | curses.color_pair(pair_id))
                    except: pass

        # 2. EDIFICIOS (Towns)
        for entity in world_state.get_all_entities():
            if isinstance(entity, Town):
                for (dx, dy), tile in entity.tiles.items():
                    tx, ty = entity.x + dx, entity.y + dy
                    ex, ey = int(mid_x + tx - cam_x), int(mid_y + ty - cam_y)
                    if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                        char = tile["char"]
                        cp = 5 if tile["type"] == "WALL" else 4 if tile["type"] == "DOOR" else 10
                        try: self.map_win.addch(ey, ex, char, curses.color_pair(cp) | curses.A_BOLD)
                        except: pass
                continue

            # 3. ENTIDADES
            ex, ey = int(mid_x + entity.x - cam_x), int(mid_y + entity.y - cam_y)
            if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                from ...core.entities.wolf import Wolf
                from ...core.entities.shop import Shop
                if isinstance(entity, Wolf): char, cp, attr = "W", 3, curses.A_BOLD
                elif isinstance(entity, Shop): char, cp, attr = "S", 2, curses.A_BOLD
                elif isinstance(entity, Person):
                    char = entity.name[0].upper()
                    if entity.state == "PANICKING": char = "!"
                    cp, attr = 1, curses.A_BOLD
                else: char, cp, attr = "H", 2, curses.A_BOLD
                try: self.map_win.addch(ey, ex, char, curses.color_pair(cp) | attr)
                except: pass

        # 4. STATUS Y RELOJ (RESTAURADO)
        self.stat_win.box()
        h_int = int(world_state.time_of_day)
        time_str = f"{h_int:02d}:00"
        self.stat_win.addstr(0, 2, f" {time_str} {'NIGHT' if is_night else 'DAY'} ", curses.A_REVERSE)
        
        for i, p in enumerate(people[:8]):
            y = i * 5 + 1
            is_foc = (p == self.camera_focus)
            self.stat_win.addstr(y, 1, f"{'>>' if is_foc else '  '} {p.name[:8]}", curses.color_pair(1) | (curses.A_REVERSE if is_foc else curses.A_BOLD))
            self.stat_win.addstr(y+1, 1, f" > {p.state[:12]}", curses.color_pair(5))
            self.stat_win.addstr(y+2, 1, f" G:{int(p.wealth)}  S:{int(p.stress)}", curses.color_pair(5))
            ebar = "I" * int(p.energy // 10)
            self.stat_win.addstr(y+3, 1, f" [{ebar.ljust(10, '.')}]", curses.color_pair(2))

        # 5. LOGS
        self.log_win.box()
        logs = logger.get_logs()
        for i, entry in enumerate(reversed(logs)):
            if i < (sh - mh - 4):
                try:
                    msg = entry
                    self.log_win.addstr(i + 1, 1, msg[:sw-2])
                except: pass

        self.map_win.box()
        self.map_win.addstr(0, 2, f" MUNDO: {scenario.name} ", curses.A_BOLD)
        self.map_win.noutrefresh()
        self.stat_win.noutrefresh()
        self.log_win.noutrefresh()
        curses.doupdate()
        if self.show_legend: self._render_legend_modal(scenario)

    def toggle_legend(self): self.show_legend = not self.show_legend
    def _render_legend_modal(self, scenario):
        sh, sw = self.stdscr.getmaxyx()
        h, w = 18, 55
        y, x = (sh-h)//2, (sw-w)//2
        lw = curses.newwin(h, w, y, x); lw.box()
        for i, (c, d, cp) in enumerate(scenario.legend_def):
            if i+2 < h-1: lw.addstr(i+2, 2, c.ljust(10), curses.color_pair(cp) | curses.A_BOLD); lw.addstr(i+2, 12, d)
        lw.refresh()
