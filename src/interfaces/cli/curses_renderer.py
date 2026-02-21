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
        self.camera_focus = None # Entidad a la que sigue la cámara
        
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
            
        self._init_windows()

    def _init_windows(self):
        self.stdscr.erase()
        sh, sw = self.stdscr.getmaxyx()
        if sh < 24 or sw < 80: return

        top_h = int(sh * 0.60)
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
        
        # --- 1. CONFIGURACIÓN CÁMARA ---
        # Si no hay foco, enfocamos al primer ciudadano
        if not self.camera_focus:
            people = [e for e in world_state.get_all_entities() if isinstance(e, Person)]
            if people: self.camera_focus = people[0]

        # Centro lógico de la cámara
        cam_x, cam_y = 0, 0
        if self.camera_focus:
            cam_x, cam_y = int(self.camera_focus.x), int(self.camera_focus.y)

        # --- 2. DIBUJAR MAPA (CON OFFSET DE CÁMARA) ---
        self.map_win.box()
        mh, mw = self.map_win.getmaxyx()
        mid_x, mid_y = mw // 2, mh // 2
        
        self.map_win.addstr(0, 2, f" 🌍 MUNDO EXTENSO - Foco: {self.camera_focus.name if self.camera_focus else 'Hogar'} ", curses.A_BOLD)
        
        # Dibujar decoraciones visibles
        for (dx, dy), char in world_state.decorations.items():
            # Posición en pantalla = (Posición mundo - Cámara) + Centro ventana
            ex, ey = mid_x + dx - cam_x, mid_y + dy - cam_y
            if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                try: self.map_win.addch(ey, ex, char, curses.A_DIM)
                except: pass

        # Dibujar todas las entidades visibles
        for entity in world_state.get_all_entities():
            ex, ey = int(mid_x + entity.x - cam_x), int(mid_y + entity.y - cam_y)
            if 1 <= ex < mw - 1 and 1 <= ey < mh - 1:
                color = curses.color_pair(1) if isinstance(entity, Person) else curses.color_pair(2)
                char = entity.name[0].upper() if isinstance(entity, Person) else "H"
                try: self.map_win.addch(ey, ex, char, color | curses.A_BOLD)
                except: pass

        # --- 3. DIBUJAR STATS (TOP CIUDADANOS) ---
        self.stat_win.box()
        self.stat_win.addstr(0, 2, " 👥 POBLACIÓN ", curses.A_BOLD)
        people = [e for e in world_state.get_all_entities() if isinstance(e, Person)]
        # Limitar lista de stats para no desbordar
        for i, p in enumerate(people[:8]):
            y_base = i * 3 + 1
            if y_base + 2 < mh - 1:
                mood = "😊" if p.stress < 20 else "😰" if p.stress < 60 else "💀"
                energy_bar = "█" * (p.energy // 25)
                self.stat_win.addstr(y_base, 1, f"{p.name[:8].ljust(8)} {mood}", curses.color_pair(1))
                self.stat_win.addstr(y_base + 1, 1, f" {p.wealth}G | S:{p.stress} | E:[{energy_bar.ljust(4)}]", curses.color_pair(5))

        # --- 4. DIBUJAR LOGS ---
        self.log_win.box()
        self.log_win.addstr(0, 2, " 📜 HISTORIAL DE EVENTOS ", curses.A_BOLD)
        logs = logger.get_logs()
        lh, lw = self.log_win.getmaxyx()
        for i, entry in enumerate(reversed(logs)):
            if i < lh - 2:
                color = curses.color_pair(5)
                if any(x in entry for x in ["atracado", "⚖️", "🕵️"]): color = curses.color_pair(3)
                elif any(x in entry for x in ["✨", "madera", "llegó"]): color = curses.color_pair(4)
                try: self.log_win.addstr(lh - 2 - i, 1, entry[:lw-2], color)
                except: pass

        # --- 5. BARRA DE ESTADO ---
        try:
            status = f" Q: Salir | Foco: {self.camera_focus.name if self.camera_focus else 'H'} | Población: {len(people)} "
            self.stdscr.addstr(sh-1, 0, status[:sw-1].ljust(sw-1), curses.A_REVERSE)
        except: pass

        self.map_win.noutrefresh()
        self.stat_win.noutrefresh()
        self.log_win.noutrefresh()
        curses.doupdate()
