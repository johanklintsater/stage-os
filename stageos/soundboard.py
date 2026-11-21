"""Manual one-shot soundboard: never auto-advance to the next track."""
import tkinter as tk
from tkinter import messagebox, ttk
from .library import AUDIO_EXT, list_media

class Soundboard:
    def __init__(self, parent, library, audio):
        self.audio=audio
        self.window=tk.Toplevel(parent)
        self.window.title("STAGE OS | SOUNDBOARD")
        self.window.geometry("860x620")
        self.window.configure(bg="#0b111a")
        tk.Label(self.window,text="SOUNDBOARD / MANUAL PLAYBACK",
                 bg="#0b111a",fg="#6df0c1",font=("DejaVu Sans",20,"bold")).pack(pady=18)
        tk.Label(self.window,text="Ett ljud åt gången • Ingen automatisk uppspelning av nästa spår",
                 bg="#0b111a",fg="#b5c8d2",font=("DejaVu Sans",11)).pack()
        self.tracks=[p for p in list_media(library) if p.suffix.lower() in AUDIO_EXT]
        self.items=tk.Listbox(self.window,bg="#18232b",fg="white",selectbackground="#296a59",
                              font=("DejaVu Sans",14),exportselection=False)
        self.items.pack(fill="both",expand=True,padx=22,pady=16)
        for p in self.tracks:self.items.insert("end",p.name)
        self.status=tk.StringVar(value="REDO")
        def play(_event=None):
            index=self.items.curselection()
            if not index:return
            try:
                self.audio.play(self.tracks[index[0]])
                self.status.set("SPELAR: "+self.tracks[index[0]].name)
            except (OSError,RuntimeError) as exc:messagebox.showerror("Ljudfel",str(exc),parent=self.window)
        def stop():
            self.audio.stop()
            self.status.set("STOPPAD")
        self.items.bind("<Double-Button-1>",play)
        bar=tk.Frame(self.window,bg="#0b111a");bar.pack(pady=8)
        ttk.Button(bar,text="▶ SPELA VALT",command=play).pack(side="left",padx=12)
        ttk.Button(bar,text="■ STOPP",command=stop).pack(side="left",padx=12)
        tk.Label(self.window,textvariable=self.status,bg="#0b111a",fg="#6df0c1").pack(pady=8)
        self.window.bind("<Escape>",lambda _e:stop())
