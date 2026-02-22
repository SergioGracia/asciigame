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
        self.zoom = 1.0 # 1.0: Normal, >1: Zoom Out, <1: Zoom In
        
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
        
        all_entities = world_state.get_all_entities()
        if not self.camera_focus and all_entities: self.camera_focus = all_entities[0]

        cam_x, cam_y = float(self.camera_focus.x), float(self.camera_focus.y)
        mh, mw = self.map_win.getmaxyx()
        mid_x, mid_y = mw // 2, mh // 2
        scenario = world_state.scenario
        is_night = world_state.is_night()
        
        # 1. MAPA Y CONSTRUCCIONES (CON ZOOM)
        for screen_y in range(1, mh - 1):
            for screen_x in range(1, mw - 1):
                # Coordenadas del mundo basadas en zoom
                wx = cam_x + (screen_x - mid_x) * self.zoom
                wy = cam_y + (screen_y - mid_y) * self.zoom
                
                # 1. TERRENO Y ESTRUCTURAS
                biome_id = scenario.get_biome_id(wx, wy)
                char = scenario.get_ground_char(int(wx), int(wy), biome_id)
                stats = scenario.get_biome_stats(biome_id)
                pair_id = stats.get("pair_id", 10)
                
                # 2. SOMBREADO DINÁMICO (Relieve)
                local_noise = scenario._noise(wx * 0.1, wy * 0.1)
                attr = curses.A_BOLD if local_noise > 0 else curses.A_DIM
                
                # 3. COLORES ESPECIALES (Ruinas/Cuevas)
                if char in ["#", "X"]: pair_id = 5; attr = curses.A_BOLD # Muros
                elif char == "0": pair_id = 3; attr = curses.A_BOLD # Entrada oscura
                
                try: self.map_win.addch(screen_y, screen_x, char, attr | curses.color_pair(pair_id))
                except: pass

        # 2. ENTIDADES (CON ZOOM)
        from ...core.entities.wolf import Wolf
        from ...core.entities.shop import Shop
        
        for entity in all_entities:
            ex = mid_x + (entity.x - cam_x) / self.zoom
            ey = mid_y + (entity.y - cam_y) / self.zoom
            
            if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                if isinstance(entity, Wolf): char, cp, attr = "W", 3, curses.A_BOLD
                elif isinstance(entity, Shop): char, cp, attr = "S", 2, curses.A_BOLD
                elif isinstance(entity, Person):
                    char = entity.name[0].upper()
                    cp, attr = 1, curses.A_BOLD
                else: char, cp, attr = "H", 2, curses.A_BOLD
                try: self.map_win.addch(int(ey), int(ex), char, curses.color_pair(cp) | attr)
                except: pass

        # 4. STATUS Y RELOJ
        self.stat_win.box()
        h_int = int(world_state.time_of_day)
        time_str = f"{h_int:02d}:00"
        self.stat_win.addstr(0, 2, f" {time_str} {'NIGHT' if is_night else 'DAY'} ", curses.A_REVERSE)
        self.stat_win.addstr(2, 2, f" ZOOM: x{1.0/self.zoom:.2f} ", curses.A_BOLD)
        self.stat_win.addstr(4, 2, f" POS: {int(cam_x)},{int(cam_y)} ", curses.color_pair(1))

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
