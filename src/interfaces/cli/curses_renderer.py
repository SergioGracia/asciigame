import curses
from ...core.state import WorldState
from ...core.logger import logger
from ...core.entities.person import Person

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
            # Biomas
            curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN) # MEADOW
            curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_GREEN) # FOREST
            curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLUE)  # SWAMP
            curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_YELLOW)# DESERT
            curses.init_pair(14, curses.COLOR_WHITE, curses.COLOR_BLACK) # STREET
            curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_WHITE) # SIDEWALK
            curses.init_pair(16, curses.COLOR_WHITE, curses.COLOR_BLACK) # INTERIOR
            curses.init_pair(17, curses.COLOR_BLACK, curses.COLOR_GREEN) # PARK
            
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
        
        # --- CAMERA ---
        if not self.camera_focus:
            people = [e for e in world_state.get_all_entities() if isinstance(e, Person)]
            if people: self.camera_focus = people[0]

        cam_x, cam_y = 0, 0
        if self.camera_focus:
            cam_x, cam_y = int(self.camera_focus.x), int(self.camera_focus.y)

        # --- MAP ---
        mh, mw = self.map_win.getmaxyx()
        mid_x, mid_y = mw // 2, mh // 2
        scenario = world_state.scenario
        is_night = world_state.is_night()
        night_attr = curses.A_DIM if is_night else 0
        
        for wy in range(cam_y - mid_y, cam_y + mid_y):
            for wx in range(cam_x - mid_x, cam_x + mid_x):
                ex, ey = mid_x + wx - cam_x, mid_y + wy - cam_y
                if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                    biome_id = scenario.get_biome_id(wx, wy)
                    stats = scenario.get_biome_stats(biome_id)
                    char, pair_id = stats.get("char", " "), stats.get("pair_id", 10)
                    if scenario.is_door(wx, wy): char, pair_id = "+", 4
                    elif (wx, wy) in world_state.decorations: char = world_state.decorations[(wx, wy)]
                    
                    try: self.map_win.addch(ey, ex, char, night_attr | curses.color_pair(pair_id))
                    except: pass

        # ENTITIES
        for entity in world_state.get_all_entities():
            ex, ey = int(mid_x + entity.x - cam_x), int(mid_y + entity.y - cam_y)
            if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                from ...core.entities.wolf import Wolf
                if isinstance(entity, Wolf): char, cp = "W", 3
                elif isinstance(entity, Person): char, cp = entity.name[0].upper(), 1
                else: char, cp = "H", 2
                try: self.map_win.addch(ey, ex, char, night_attr | curses.color_pair(cp) | curses.A_BOLD)
                except: pass

        # STATUS WINDOW
        self.stat_win.box()
        h_int = int(world_state.time_of_day)
        self.stat_win.addstr(0, 2, f" STATUS ({h_int:02d}:00) ", curses.A_BOLD)
        people = [e for e in world_state.get_all_entities() if isinstance(e, Person)]
        for i, p in enumerate(people[:8]):
            y = i * 4 + 1
            if y + 3 < mh - 1:
                self.stat_win.addstr(y, 1, f"{p.name[:10]}", curses.color_pair(1) | curses.A_BOLD)
                self.stat_win.addstr(y+1, 1, f" Wealth: {p.wealth}G", curses.color_pair(4))
                self.stat_win.addstr(y+2, 1, f" Stress: {int(p.stress)}", curses.color_pair(3))
                self.stat_win.addstr(y+3, 1, f" Energy: [{'#'*(p.energy//20)}]", curses.color_pair(2))

        # LOGS
        self.log_win.box()
        self.log_win.addstr(0, 2, " HISTORY ", curses.A_BOLD)
        logs = logger.get_logs()
        lh, lw = self.log_win.getmaxyx()
        for i, entry in enumerate(reversed(logs)):
            if i < lh - 2:
                try: self.log_win.addstr(lh - 2 - i, 1, entry[:sw-2])
                except: pass

        self.map_win.box()
        self.map_win.noutrefresh()
        self.stat_win.noutrefresh()
        self.log_win.noutrefresh()
        curses.doupdate()
        if self.show_legend: self._render_legend_modal(scenario)

    def toggle_legend(self): self.show_legend = not self.show_legend
    def _render_legend_modal(self, scenario):
        sh, sw = self.stdscr.getmaxyx()
        h, w = 18, 50
        y, x = (sh-h)//2, (sw-w)//2
        lw = curses.newwin(h, w, y, x); lw.box()
        for i, (c, d, cp) in enumerate(scenario.legend_def):
            if i+2 < h-1: lw.addstr(i+2, 2, c.ljust(5), curses.color_pair(cp) | curses.A_BOLD); lw.addstr(i+2, 10, d)
        lw.refresh()
