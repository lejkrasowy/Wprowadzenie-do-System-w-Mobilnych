import random
import os
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Simulator:
    def __init__(self, channels, lam, mean_time, sigma, min_time, max_time, queue_limit, sim_time):
        self.channels_count = channels
        self.lam = lam
        self.mean_time = mean_time
        self.sigma = sigma
        self.min_time = min_time
        self.max_time = max_time
        self.queue_limit = queue_limit
        self.sim_time = sim_time
        self.reset()

    def reset(self):
        self.time = 0
        self.channels = [0] * self.channels_count
        self.queue = deque()

        self.generated = 0
        self.served = 0
        self.rejected = 0
        self.total_wait = 0

        self.rho_history = []
        self.q_history = []
        self.w_history = []

        self.arrivals = self.generate_arrivals()
        self.arrival_index = 0

    def generate_service_time(self):
        while True:
            value = random.gauss(self.mean_time, self.sigma)
            if self.min_time <= value <= self.max_time:
                return max(1, round(value))

    def generate_arrivals(self):
        arrivals = []
        t = 0.0
        while t < self.sim_time:
            t += random.expovariate(self.lam)
            if t <= self.sim_time:
                arrivals.append((t, self.generate_service_time()))
        return arrivals

    def free_channel_index(self):
        for i, ch in enumerate(self.channels):
            if ch == 0:
                return i
        return None

    def step(self):
        t = self.time

        for i in range(self.channels_count):
            if self.channels[i] > 0:
                self.channels[i] -= 1
                if self.channels[i] == 0:
                    self.served += 1

        while self.arrival_index < len(self.arrivals) and self.arrivals[self.arrival_index][0] <= t:
            arrival_time, service_time = self.arrivals[self.arrival_index]
            self.generated += 1

            free = self.free_channel_index()
            if free is not None:
                self.channels[free] = service_time
            elif len(self.queue) < self.queue_limit:
                self.queue.append((arrival_time, service_time))
            else:
                self.rejected += 1

            self.arrival_index += 1

        while self.queue and self.free_channel_index() is not None:
            free = self.free_channel_index()
            arrival_time, service_time = self.queue.popleft()
            self.total_wait += (t - arrival_time)
            self.channels[free] = service_time

        busy = sum(1 for ch in self.channels if ch > 0)
        rho = busy / self.channels_count if self.channels_count > 0 else 0
        q = len(self.queue)
        w = self.total_wait / self.served if self.served > 0 else 0

        self.rho_history.append((t, rho))
        self.q_history.append((t, q))
        self.w_history.append((t, w))

        self.time += 1

    def results(self):
        avg_rho = sum(v for _, v in self.rho_history) / len(self.rho_history) if self.rho_history else 0
        avg_q = sum(v for _, v in self.q_history) / len(self.q_history) if self.q_history else 0
        avg_w = sum(v for _, v in self.w_history) / len(self.w_history) if self.w_history else 0

        return {
            "generated": self.generated,
            "served": self.served,
            "rejected": self.rejected,
            "avg_rho": avg_rho,
            "avg_q": avg_q,
            "avg_w": avg_w
        }

    def format_number(self, value):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return text.replace(".", ",")

    def save_report_txt_format(self, filename):
        lines = [
            "Parametry symulacji:\n",
            "\n",
            f"Liczba kanalow: {self.channels_count}\n",
            f"Dlugosc kolejki: {self.queue_limit}\n",
            f"Lambda: {self.lam}\n",
            f"Srednia dlugosc rozmowy: {self.mean_time}\n",
            f"Odchylenie: {self.sigma}\n",
            f"Minimalny czas polaczenia: {self.min_time}\n",
            f"Maksymalny czas polaczenia: {self.max_time}\n",
            f"Czas symulacji: {self.sim_time}\n",
            "\n",
            "Ro\t\tQ\t\tW\n"
        ]

        sum_rho = 0
        sum_q = 0
        sum_w = 0

        for i in range(len(self.rho_history)):
            sum_rho += self.rho_history[i][1]
            sum_q += self.q_history[i][1]
            sum_w += self.w_history[i][1]

            avg_rho = sum_rho / (i + 1)
            avg_q = sum_q / (i + 1)
            avg_w = sum_w / (i + 1)

            lines.append(
                f"{self.format_number(avg_rho)}\t\t"
                f"{self.format_number(avg_q)}\t\t"
                f"{self.format_number(avg_w)}\n"
            )

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(lines)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator stacji bazowej")
        self.root.geometry("1200x700")

        self.sim = None
        self.running = False
        self.after_id = None

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=10)

        right = ttk.Frame(main)
        right.pack(side="right", fill="both", expand=True)

        params_frame = ttk.LabelFrame(left, text="Parametry", padding=10)
        params_frame.pack(fill="x", pady=5)

        self.inputs = {}
        fields = {
            "Liczba kanałów": "10",
            "Długość kolejki": "10",
            "Lambda": "1",
            "Średnia długość rozmowy": "20",
            "Odchylenie": "5",
            "Minimalny czas połączenia": "10",
            "Maksymalny czas połączenia": "30",
            "Czas symulacji": "30",
            "Opóźnienie [ms]": "100"
        }

        for i, (label, default) in enumerate(fields.items()):
            ttk.Label(params_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(params_frame, width=18)
            entry.insert(0, default)
            entry.grid(row=i, column=1, pady=2)
            self.inputs[label] = entry

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=5)

        ttk.Button(btns, text="Start", command=self.start).pack(fill="x", pady=2)
        ttk.Button(btns, text="Stop", command=self.stop).pack(fill="x", pady=2)
        ttk.Button(btns, text="Reset", command=self.reset).pack(fill="x", pady=2)

        stats_frame = ttk.LabelFrame(left, text="Statystyki", padding=10)
        stats_frame.pack(fill="x", pady=5)

        self.stats = {}
        for label in ["Czas", "Wygenerowane", "Obsłużone", "Odrzucone", "Śr. rho", "Śr. Q", "Śr. W", "Kolejka"]:
            var = tk.StringVar(value="0")
            self.stats[label] = var
            row = len(self.stats) - 1
            ttk.Label(stats_frame, text=label + ":").grid(row=row, column=0, sticky="w", pady=2)
            ttk.Label(stats_frame, textvariable=var).grid(row=row, column=1, sticky="w", pady=2)

        channels_frame = ttk.LabelFrame(left, text="Kanały", padding=10)
        channels_frame.pack(fill="both", expand=True, pady=5)

        self.canvas = tk.Canvas(channels_frame, width=300, height=300, bg="white")
        self.canvas.pack(fill="both", expand=True)

        chart_frame = ttk.LabelFrame(right, text="Wykresy", padding=10)
        chart_frame.pack(fill="both", expand=True)

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        self.fig.tight_layout(pad=2)

        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True)

        self.clear_plots()

    def read_values(self):
        try:
            return {
                "channels": int(self.inputs["Liczba kanałów"].get()),
                "queue": int(self.inputs["Długość kolejki"].get()),
                "lam": float(self.inputs["Lambda"].get()),
                "mean_time": float(self.inputs["Średnia długość rozmowy"].get()),
                "sigma": float(self.inputs["Odchylenie"].get()),
                "min_time": int(self.inputs["Minimalny czas połączenia"].get()),
                "max_time": int(self.inputs["Maksymalny czas połączenia"].get()),
                "sim_time": int(self.inputs["Czas symulacji"].get()),
                "delay": int(self.inputs["Opóźnienie [ms]"].get())
            }
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne liczby.")
            return None

    def create_simulator(self):
        values = self.read_values()
        if not values:
            return False

        self.sim = Simulator(
            values["channels"],
            values["lam"],
            values["mean_time"],
            values["sigma"],
            values["min_time"],
            values["max_time"],
            values["queue"],
            values["sim_time"]
        )

        self.clear_plots()
        return True

    def start(self):
        if self.sim is None and not self.create_simulator():
            return

        if not self.running:
            self.running = True
            self.loop()

    def loop(self):
        if not self.running or self.sim is None:
            return

        if self.sim.time <= self.sim.sim_time:
            self.sim.step()
            self.refresh()
            delay = int(self.inputs["Opóźnienie [ms]"].get())
            self.after_id = self.root.after(delay, self.loop)
        else:
            self.running = False
            self.update_plots()

            filename = os.path.join(os.getcwd(), "wyniki_naszej_symulacji.txt")
            self.sim.save_report_txt_format(filename)

            messagebox.showinfo("Koniec", f"Symulacja zakończona.\nPlik zapisany:\n{filename}")

    def stop(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def reset(self):
        self.stop()
        self.sim = None
        for var in self.stats.values():
            var.set("0")
        self.canvas.delete("all")
        self.clear_plots()

    def refresh(self):
        if self.sim is None:
            return

        r = self.sim.results()

        self.stats["Czas"].set(str(self.sim.time))
        self.stats["Wygenerowane"].set(str(r["generated"]))
        self.stats["Obsłużone"].set(str(r["served"]))
        self.stats["Odrzucone"].set(str(r["rejected"]))
        self.stats["Śr. rho"].set(f"{r['avg_rho']:.4f}")
        self.stats["Śr. Q"].set(f"{r['avg_q']:.4f}")
        self.stats["Śr. W"].set(f"{r['avg_w']:.4f}")
        self.stats["Kolejka"].set(str(len(self.sim.queue)))

        self.draw_channels()

    def draw_channels(self):
        self.canvas.delete("all")
        if self.sim is None:
            return

        box_w, box_h = 120, 45
        cols = 2

        for i, ch in enumerate(self.sim.channels):
            row = i // cols
            col = i % cols
            x1 = 10 + col * (box_w + 10)
            y1 = 10 + row * (box_h + 10)
            x2 = x1 + box_w
            y2 = y1 + box_h

            if ch == 0:
                color = "lightgreen"
                text = f"Kanał {i+1}\nWOLNY"
            else:
                color = "lightcoral"
                text = f"Kanał {i+1}\n{ch}s"

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text)

    def clear_plots(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.set_title("rho")
        self.ax2.set_title("Q")
        self.ax3.set_title("W")

        self.fig.tight_layout(pad=2)
        self.plot_canvas.draw()

    def update_plots(self):
        if self.sim is None:
            return

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.set_title("rho")
        self.ax2.set_title("Q")
        self.ax3.set_title("W")

        self.ax1.plot([x for x, _ in self.sim.rho_history], [y for _, y in self.sim.rho_history])
        self.ax2.plot([x for x, _ in self.sim.q_history], [y for _, y in self.sim.q_history])
        self.ax3.plot([x for x, _ in self.sim.w_history], [y for _, y in self.sim.w_history])

        self.fig.tight_layout(pad=2)
        self.plot_canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()