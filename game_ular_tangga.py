import tkinter as tk
from tkinter import messagebox
import random, math, time,  os, unittest, sys

# =====================================================
#            ===== 1. LOGIC GAME ====
# =====================================================

class GameLogic:
    def __init__(self):
        self.max_pos = 100
        self.players = {
            1: {"pos": 0, "color": "#007BFF", "name": "Player 1"},
            2: {"pos": 0, "color": "#DC3545", "name": "Player 2"}
        }
        self.turn = 1
        self.game_over = False
        self.history_file = "riwayat_ular_tangga.txt"

        # Tangga & Ular (Modern rules)
        self.snakes_and_ladders = {
            3: 22, 5: 8, 11: 26, 20: 29, 27: 56, 72: 91, 77: 96,   # Tangga (Naik)
            17: 4, 19: 7, 21: 9, 31: 15, 54: 34, 62: 18, 64: 60,   # Ular (Turun)
            87: 24, 93: 73, 95: 75, 99: 78
        }

    def roll_dice(self):
        return random.randint(1, 6)

    def move_current_player(self, steps):
        p = self.players[self.turn]
        current = p["pos"]
        new_pos = current + steps
        msg = f"Maju ke {new_pos}"
        is_jump = False

        # Cek Ular / Tangga
        if new_pos in self.snakes_and_ladders:
            dest = self.snakes_and_ladders[new_pos]
            msg = "NAIK TANGGA!" if dest > new_pos else "DIGIGIT ULAR!"
            new_pos = dest
            is_jump = True

        # Cek Finish
        if new_pos >= self.max_pos:
            new_pos = self.max_pos
            self.game_over = True
            msg = "FINISH!"

        p["pos"] = new_pos
        return new_pos, msg, is_jump

    def switch_turn(self):
        self.turn = 2 if self.turn == 1 else 1

    def reset(self):
        self.players[1]["pos"] = 0
        self.players[2]["pos"] = 0
        self.turn = 1
        self.game_over = False

    def save_winner(self, name):
        try:
            with open(self.history_file, "a") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M')}] {name} Menang\n")
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_history(self):
        if not os.path.exists(self.history_file):
            return "Belum ada riwayat."
        try:
            with open(self.history_file, "r") as f:
                lines = f.readlines()
                return "".join(lines[-5:]) if lines else "Riwayat kosong."
        except:
            return "Gagal membaca file."


# =====================================================
#      ===== 2. UNIT TEST (Sesuai Poin 13) ====
# =====================================================
# Bagian ini akan mengetes logika game secara otomatis

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        """Dijalankan sebelum setiap test"""
        self.game = GameLogic()

    def test_roll_dice_range(self):
        """Test apakah dadu menghasilkan angka 1 s.d 6"""
        result = self.game.roll_dice()
        self.assertTrue(1 <= result <= 6, "Dadu harus antara 1-6")

    def test_move_normal(self):
        """Test pergerakan biasa tanpa ular/tangga"""
        self.game.players[1]["pos"] = 0
        # Posisi 0 + 1 = 1 (Aman, tidak ada ular/tangga di 1)
        new_pos, msg, jump = self.game.move_current_player(1)
        self.assertEqual(new_pos, 1)
        self.assertFalse(jump)

    def test_ladder_mechanic(self):
        """Test naik tangga (Logic: Posisi 3 naik ke 22)"""
        self.game.players[1]["pos"] = 0
        # Roll 3 dari posisi 0 mendarat di 3 -> harus jadi 22
        new_pos, msg, jump = self.game.move_current_player(3)
        self.assertEqual(new_pos, 22)
        self.assertTrue(jump)
        self.assertIn("NAIK TANGGA", msg)

    def test_snake_mechanic(self):
        """Test turun ular (Logic: Posisi 17 turun ke 4)"""
        self.game.players[1]["pos"] = 0
        # Kita set manual ke 16, lalu maju 1 langkah ke 17
        self.game.players[1]["pos"] = 16
        new_pos, msg, jump = self.game.move_current_player(1)
        self.assertEqual(new_pos, 4) # 17 turun ke 4
        self.assertTrue(jump)
        self.assertIn("DIGIGIT ULAR", msg)

    def test_switch_turn(self):
        """Test pergantian giliran"""
        self.assertEqual(self.game.turn, 1)
        self.game.switch_turn()
        self.assertEqual(self.game.turn, 2)
        self.game.switch_turn()
        self.assertEqual(self.game.turn, 1)


# =====================================================
#          ===== 3. UI MODERN + ANIMASI ====
# =====================================================

class ModernSnakeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Ular Tangga")
        self.root.geometry("920x650")
        self.root.configure(bg="#1A252F")

        self.logic = GameLogic()
        self.cell_size = 60
        self.ox = 0
        self.oy = 0

        # Frame Utama
        self.main = tk.Frame(root, bg="#1A252F")
        self.main.pack(fill=tk.BOTH, expand=True)

        # Area Board (Kiri)
        self.canvas = tk.Canvas(self.main, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_resize)

        # Area Panel Kontrol (Kanan)
        self.panel = tk.Frame(self.main, width=200, bg="#1A252F")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.panel, text="GILIRAN", fg="white", bg="#1A252F",
                 font=("Arial", 12, "bold")).pack(pady=5)

        self.lbl_turn = tk.Label(self.panel, text="P1", fg="white",
                                 bg=self.logic.players[1]["color"],
                                 font=("Arial", 14, "bold"), width=10)
        self.lbl_turn.pack(pady=5)

        # DICE CANVAS
        self.dice_canvas = tk.Canvas(self.panel, width=90, height=90,
                                     bg="#1A252F", highlightthickness=0)
        self.dice_canvas.pack(pady=20)
        self.draw_dice_face(1)

        # Tombol Kontrol
        self.btn_p1 = tk.Button(self.panel, text="ROLL P1", bg="#007BFF",
                                fg="white", font=("Arial", 10, "bold"),
                                command=lambda: self.on_roll(1))
        self.btn_p1.pack(fill="x", padx=20, pady=5)

        self.btn_p2 = tk.Button(self.panel, text="ROLL P2", bg="gray",
                                fg="white", font=("Arial", 10, "bold"),
                                state="disabled",
                                command=lambda: self.on_roll(2))
        self.btn_p2.pack(fill="x", padx=20, pady=5)

        tk.Button(self.panel, text="RIWAYAT", bg="#3498DB", fg="white",
                  command=self.show_history).pack(fill="x", padx=20, pady=10)

        tk.Button(self.panel, text="RESET", bg="#E74C3C", fg="white",
                  command=self.reset_game).pack(fill="x", padx=20, pady=10)

        self.lbl_status = tk.Label(self.panel, text="Siap!", fg="#BDC3C7",
                                   bg="#1A252F", wraplength=180, font=("Arial", 10))
        self.lbl_status.pack(pady=5)

    # --- Animasi Pergerakan ---
    def animate_move(self, pid, start, end):
        if start == end: return
        step = 1 if end > start else -1
        
        # Animasi langkah demi langkah
        current = start
        while current != end:
            current += step
            self.logic.players[pid]["pos"] = current
            self.update_players()
            self.canvas.update()
            time.sleep(0.04) # Kecepatan animasi jalan
        
        # Final update
        self.logic.players[pid]["pos"] = end
        self.update_players()

    # --- UI Drawing Methods ---
    def on_resize(self, event):
        self.cell_size = min(event.width // 10, event.height // 10)
        self.ox = (event.width - self.cell_size * 10) // 2
        self.oy = (event.height - self.cell_size * 10) // 2
        self.refresh_board()

    def refresh_board(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_snakes_ladders()
        self.update_players()

    def get_coords(self, pos):
        if pos <= 0:
            return self.ox + 30, self.oy + 60 * 9 + 30
        row = (pos - 1) // 10
        col = (pos - 1) % 10
        if row % 2 == 1:
            col = 9 - col
        x = self.ox + (col * self.cell_size) + self.cell_size / 2
        y = self.oy + ((9 - row) * self.cell_size) + self.cell_size / 2
        return int(x), int(y)

    def draw_grid(self):
        colors = ["#F2F3F4", "#E5E7E9"]
        for r in range(10):
            for c in range(10):
                x1 = self.ox + c * self.cell_size
                y1 = self.oy + r * self.cell_size
                num = (9 - r) * 10 + (c + 1)
                self.canvas.create_rectangle(
                    x1, y1, x1+self.cell_size, y1+self.cell_size,
                    fill=colors[(r+c)%2], outline="#D5D8DC"
                )
                self.canvas.create_text(x1+15, y1+15, text=str(num),
                                        fill="#839192",
                                        font=("Arial", int(self.cell_size*0.25)))

    def draw_snakes_ladders(self):
        for s, e in self.logic.snakes_and_ladders.items():
            sx, sy = self.get_coords(s)
            ex, ey = self.get_coords(e)
            if e > s: self.draw_ladder(sx, sy, ex, ey)
            else: self.draw_snake(sx, sy, ex, ey)

    def draw_ladder(self, x1, y1, x2, y2):
        color = "#AF601A"
        self.canvas.create_line(x1-6, y1, x2-6, y2, fill=color, width=5)
        self.canvas.create_line(x1+6, y1, x2+6, y2, fill=color, width=5)
        steps = 5
        for i in range(1, steps+1):
            t = i / (steps+1)
            mx = x1 + (x2-x1)*t
            my = y1 + (y2-y1)*t
            self.canvas.create_line(mx-8, my, mx+8, my, fill=color, width=4)

    def draw_snake(self, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0: return
        nx, ny = -dy / dist, dx / dist
        pts = []
        for i in range(21):
            t = i / 20
            wave = math.sin(t * math.pi * 4) * 10
            px = x1 + dx * t + wave * nx
            py = y1 + dy * t + wave * ny
            pts.extend([px, py])
        self.canvas.create_line(*pts, fill="#C0392B", width=6, smooth=True)

    def draw_dice_face(self, n):
        self.dice_canvas.delete("all")
        self.dice_canvas.create_rectangle(10, 10, 80, 80, fill="white", outline="#BDC3C7", width=3)
        dots = {
            1: [(45, 45)],
            2: [(25, 25), (65, 65)],
            3: [(25, 25), (45, 45), (65, 65)],
            4: [(25, 25), (65, 25), (25, 65), (65, 65)],
            5: [(25, 25), (65, 25), (45, 45), (25, 65), (65, 65)],
            6: [(25, 25), (65, 25), (25, 45), (65, 45), (25, 65), (65, 65)],
        }
        for x, y in dots[n]:
            self.dice_canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")

    def update_players(self):
        self.canvas.delete("player")
        for pid in (1, 2):
            px, py = self.get_coords(self.logic.players[pid]["pos"])
            r = self.cell_size * 0.25
            offset = -r if pid == 1 else r
            color = self.logic.players[pid]["color"]
            
            # Pion
            self.canvas.create_oval(px-r+offset, py-r, px+r+offset, py+r,
                                    fill=color, outline="white", width=2, tags="player")
            # Text ID
            self.canvas.create_text(px+offset, py, text=f"P{pid}", fill="white",
                                    font=("Arial", 9, "bold"), tags="player")

    # --- Game Flow ---
    def on_roll(self, player_id):
        if self.logic.game_over: return

        # Animasi Dadu
        for _ in range(8):
            self.draw_dice_face(random.randint(1, 6))
            self.root.update()
            time.sleep(0.05)

        val = self.logic.roll_dice()
        self.draw_dice_face(val)

        old_pos = self.logic.players[self.logic.turn]["pos"]
        new_pos, msg, jumped = self.logic.move_current_player(val)
        
        self.lbl_status.config(text=f"{msg} (Dadu: {val})")
        
        # Animasi Jalan (Smooth)
        if jumped:
            # Jalan dulu ke mulut ular/bawah tangga
            # Kita perlu logic sedikit tricky untuk animasi ini, 
            # tapi untuk simplifikasi tugas, kita animasi langsung ke tujuan
            self.animate_move(self.logic.turn, old_pos, new_pos)
        else:
            self.animate_move(self.logic.turn, old_pos, new_pos)

        # Cek Menang
        if self.logic.game_over:
            winner = self.logic.players[self.logic.turn]["name"]
            messagebox.showinfo("SELAMAT!", f"{winner} Memenangkan Permainan!")
            self.logic.save_winner(winner)
            self.reset_game()
            return

        # Ganti Giliran jika tidak dapat 6
        if val != 6 and not jumped:
            self.logic.switch_turn()
        
        self.update_turn_ui()

    def update_turn_ui(self):
        turn = self.logic.turn
        self.lbl_turn.config(text=f"P{turn}", bg=self.logic.players[turn]["color"])
        if turn == 1:
            self.btn_p1.config(state="normal", bg="#007BFF")
            self.btn_p2.config(state="disabled", bg="gray")
        else:
            self.btn_p1.config(state="disabled", bg="gray")
            self.btn_p2.config(state="normal", bg="#DC3545")

    def show_history(self):
        data = self.logic.load_history()
        messagebox.showinfo("Riwayat Pemenang", data)

    def reset_game(self):
        self.logic.reset()
        self.draw_dice_face(1)
        self.update_players()
        self.lbl_status.config(text="Permainan Baru Dimulai!")
        self.update_turn_ui()


# =====================================================
#        ===== MAIN PROGRAM EXECUTOR ====
# =====================================================

if __name__ == "__main__":
    # --- JALANKAN UNIT TEST TERLEBIH DAHULU ---
    print("====================================")
    print("      MENJALANKAN UNIT TEST...      ")
    print("====================================")
    
    # Load test dari class TestGameLogic
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGameLogic)
    # Jalankan test (verbosity=2 agar detail)
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    print("====================================")
    
    # Jika test gagal, beri peringatan tapi tetap buka game (opsional)
    if not test_result.wasSuccessful():
        print("PERINGATAN: Beberapa Unit Test Gagal! Cek log di atas.")
    else:
        print("SEMUA TEST SUKSES! Membuka Game...")

    # --- JALANKAN APLIKASI GUI ---
    root = tk.Tk()
    app = ModernSnakeUI(root)
    root.mainloop()