#!/usr/bin/env python3
"""STAGE OS desktop: text, audio, file manager, and networking launcher."""
import os
import json
import time
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from pathlib import Path
try:
    from .operations import create_document, save_document, import_file, trash_file, restore_file
    from .backup import backup_texts, restore_texts
except ImportError:
    from operations import create_document, save_document, import_file, trash_file, restore_file
    from backup import backup_texts, restore_texts

try:
    from .library import AUDIO_EXT, TEXT_EXT, list_media, read_text, MAX_TEXT_BYTES
except ImportError:
    from library import AUDIO_EXT, TEXT_EXT, list_media, read_text, MAX_TEXT_BYTES

LIBRARY = Path(os.environ.get('STAGE_OS_LIBRARY', str(Path.home() / 'StageOS' / 'library'))).expanduser()

class Audio:
    def __init__(self): self.process = None
    def play(self, path):
        self.stop()
        if not shutil.which('mpv'): raise RuntimeError('mpv saknas')
        self.process = subprocess.Popen(['mpv','--no-video','--no-terminal','--really-quiet','--',str(path)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=1)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait()
        self.process = None
    def playing(self): return self.process is not None and self.process.poll() is None

class Desktop:
    def __init__(self, root):
        self.root=root; self.root.title('STAGE OS | STUDIO DESKTOP'); self.root.geometry('1200x760'); self.root.minsize(850,540); self.root.configure(bg='#0b111a')
        LIBRARY.mkdir(parents=True, exist_ok=True)
        self.audio=Audio(); self.text_windows=[]; self.selected=None
        self.trash=LIBRARY.parent/'trash'
        self.status=tk.StringVar(value='STAGE OS | Klar')
        style=ttk.Style(); style.theme_use('clam')
        style.configure('TButton', padding=9, font=('DejaVu Sans',10,'bold'), background='#263849', foreground='#e9f3f6', borderwidth=0)
        style.map('TButton',background=[('active','#315b61')])
        self.setlist_path=LIBRARY.parent/'setlist.json'
        self.setlist=self.load_setlist()
        top=tk.Frame(root,bg='#18232b'); top.pack(fill='x')
        tk.Label(top,text='◉ STAGE OS',font=('DejaVu Sans',22,'bold'),fg='#6df0c1',bg='#18232b').pack(side='left',padx=20,pady=12)
        for name,fn in [('LÅTTEXTER',self.open_selected_text),('LJUD',self.toggle_audio),('NY TEXT',self.new_text),('IMPORTERA',self.import_files),('NÄTVERK',self.network),('SETLIST',self.show_setlist),('PAPPERSKORG',self.show_trash),('BACKUP',self.backup_dialog),('UPPDATERA',self.refresh)]:
            ttk.Button(top,text=name,command=fn).pack(side='left',padx=3)
        body=tk.PanedWindow(root,orient='horizontal',sashwidth=6,bg='#26333b'); body.pack(fill='both',expand=True,padx=14,pady=14)
        sidebar=tk.Frame(body,bg='#18232b'); body.add(sidebar,minsize=220,width=340)
        tk.Label(sidebar,text='01 / BIBLIOTEK',fg='#6df0c1',bg='#18232b',font=('DejaVu Sans',13,'bold')).pack(anchor='w',padx=12,pady=10)
        self.listbox=tk.Listbox(sidebar,font=('DejaVu Sans',12),bg='#10161c',fg='white',selectbackground='#2b7351',exportselection=False)
        self.listbox.pack(fill='both',expand=True,padx=8,pady=8)
        self.listbox.bind('<<ListboxSelect>>',self.select)
        self.listbox.bind('<Double-Button-1>',lambda e:self.open_selected_text() if self.is_text() else self.toggle_audio())
        preview=tk.Frame(body,bg='#10161c'); body.add(preview,minsize=350)
        tk.Label(preview,text='02 / FÖRHANDSVISNING',font=('DejaVu Sans',13,'bold'),fg='#6df0c1',bg='#10161c').pack(anchor='w',padx=14,pady=8)
        self.preview=tk.Text(preview,wrap='word',font=('DejaVu Sans Mono',16),bg='#0b1014',fg='#f4f4f4',insertbackground='white',state='disabled')
        self.preview.pack(fill='both',expand=True,padx=12,pady=8)
        bottom=tk.Frame(root,bg='#18232b'); bottom.pack(fill='x')
        ttk.Button(bottom,text='SPELA / STOPPA',command=self.toggle_audio).pack(side='left',padx=8,pady=7)
        ttk.Button(bottom,text='ÖPPNA I EGET FÖNSTER',command=self.open_selected_text).pack(side='left',padx=8)
        ttk.Button(bottom,text='TA BORT FIL',command=self.delete_selected).pack(side='left',padx=8)
        ttk.Button(bottom,text='+ SETLIST',command=self.add_setlist).pack(side='left',padx=8)
        ttk.Button(bottom,text='BYT NAMN',command=self.rename_selected).pack(side='left',padx=8)
        ttk.Button(bottom,text='ÖPPNA MAPP',command=self.open_folder).pack(side='left',padx=8)
        tk.Label(bottom,textvariable=self.status,bg='#18232b',fg='#d8e7e0').pack(side='right',padx=14)
        self.files=[]; self.refresh(); self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.bind_all('<Control-n>',lambda e:self.new_text())
        self.root.bind_all('<Control-o>',lambda e:self.import_files())
        self.listbox.bind('<Delete>',lambda e:self.delete_selected())

    def backup_dialog(self):
        choice = messagebox.askyesnocancel('STAGE OS Backup', 'Ja: säkerhetskopiera TXT/MD till vald mapp.\nNej: återställ från ZIP (befintliga filer skrivs inte över).')
        if choice is None: return
        try:
            if choice:
                directory = filedialog.askdirectory(title='Välj plats för säkerhetskopia')
                if directory:
                    archive = backup_texts(LIBRARY, directory)
                    messagebox.showinfo('Säkerhetskopia', f'Sparad: {archive}')
            else:
                archive = filedialog.askopenfilename(title='Välj STAGE OS ZIP', filetypes=[('ZIP', '*.zip')])
                if archive:
                    files = restore_texts(LIBRARY, archive)
                    self.refresh()
                    messagebox.showinfo('Återställning', f'{len(files)} filer återställda')
        except (OSError, ValueError, FileExistsError) as exc:
            messagebox.showerror('Säkerhetskopia', str(exc))

    def refresh(self):
        previous=self.selected
        self.files=list_media(LIBRARY); self.listbox.delete(0,'end')
        for p in self.files: self.listbox.insert('end',('♫ ' if p.suffix.lower() in AUDIO_EXT else '≡ ')+p.name)
        if previous in self.files:
            i=self.files.index(previous); self.listbox.selection_set(i); self.listbox.see(i)
        self.status.set(f'{len(self.files)} filer  •  {LIBRARY}')

    def select(self,_event=None):
        ix=self.listbox.curselection()
        if not ix:return
        self.selected=self.files[ix[0]]
        self.preview.configure(state='normal'); self.preview.delete('1.0','end')
        if self.is_text():
            try:self.preview.insert('end','\n'.join(read_text(self.selected)))
            except (OSError,UnicodeError,ValueError) as exc:self.preview.insert('end',str(exc))
        else:self.preview.insert('end',f'Ljudfil: {self.selected.name}\n\nTryck SPELA / STOPPA. Ljudet fortsätter medan textfönster är öppna.')
        self.preview.configure(state='disabled')

    def is_text(self):return self.selected is not None and self.selected.suffix.lower() in TEXT_EXT

    def toggle_audio(self):
        if self.audio.playing():self.audio.stop(); self.status.set('Ljud stoppat');return
        if not self.selected or self.selected.suffix.lower() not in AUDIO_EXT:
            messagebox.showinfo('STAGE OS','Välj en ljudfil i biblioteket.');return
        try:self.audio.play(self.selected);self.status.set('Spelar: '+self.selected.name)
        except (OSError,RuntimeError) as exc:messagebox.showerror('Ljudfel',str(exc))

    def open_selected_text(self):
        if not self.is_text():messagebox.showinfo('STAGE OS','Välj en textfil.');return
        self.open_text(self.selected)

    def open_text(self,path):
        win=tk.Toplevel(self.root);win.title('STAGE OS | '+path.name);win.geometry('950x650');win.configure(bg='black')
        bar=tk.Frame(win,bg='#18232b');bar.pack(fill='x')
        tk.Label(bar,text=path.name,fg='#91f2a4',bg='#18232b',font=('DejaVu Sans',14,'bold')).pack(side='left',padx=10)
        content=tk.Text(win,wrap='word',bg='black',fg='white',insertbackground='white',font=('DejaVu Sans Mono',25),undo=True)
        content.pack(fill='both',expand=True)
        try:content.insert('1.0','\n'.join(read_text(path)))
        except (OSError,UnicodeError,ValueError) as exc:content.insert('1.0',str(exc))
        speed=tk.DoubleVar(value=1.0);running=tk.BooleanVar(value=False)
        def scroll_tick():
            if not win.winfo_exists():return
            if running.get():content.yview_scroll(1,'units')
            win.after(max(150,int(1200/max(0.25,speed.get()))),scroll_tick)
        def save():
            data=content.get('1.0','end-1c').encode('utf-8')
            if len(data)>MAX_TEXT_BYTES:messagebox.showerror('För stor','Textfilen är för stor');return
            try:save_document(LIBRARY,path.name,content.get('1.0','end-1c'));self.refresh();self.status.set('Sparat: '+path.name)
            except (OSError,ValueError) as exc:messagebox.showerror('Kunde inte spara',str(exc))
        ttk.Button(bar,text='SPARA',command=save).pack(side='right',padx=5)
        win.bind('<Control-s>',lambda e:(save(),'break')[1])
        ttk.Button(bar,text='AUTO PÅ/AV',command=lambda:running.set(not running.get())).pack(side='right',padx=5)
        ttk.Button(bar,text='A+',command=lambda:content.configure(font=('DejaVu Sans Mono',min(70,int(content.cget('font').split()[-1])+3)))).pack(side='right',padx=5)
        ttk.Button(bar,text='A-',command=lambda:content.configure(font=('DejaVu Sans Mono',max(12,int(content.cget('font').split()[-1])-3)))).pack(side='right',padx=5)
        ttk.Scale(bar,from_=0.25,to=5.0,variable=speed,orient='horizontal',length=110).pack(side='right',padx=5)
        win.bind('<F11>',lambda e:win.attributes('-fullscreen',not bool(win.attributes('-fullscreen'))))
        win.bind('<Escape>',lambda e:win.attributes('-fullscreen',False))
        win.bind('<space>',lambda e:running.set(not running.get()) if not content.edit_modified() else None)
        win.after(1000,scroll_tick);self.text_windows.append(win)

    def new_text(self):
        name=simpledialog.askstring('Ny låttext','Filnamn (utan .txt):',parent=self.root)
        if not name:return
        name=name.strip()
        if not name or name in ('.','..') or '/' in name or '\\' in name or any(ord(c)<32 for c in name):
            messagebox.showerror('Fel','Ogiltigt filnamn');return
        try:target=create_document(LIBRARY,name)
        except (ValueError,OSError) as exc:messagebox.showerror('Fel',str(exc));return
        self.refresh();self.selected=target;self.open_text(target)

    def import_files(self):
        paths=filedialog.askopenfilenames(title='Importera text och ljud')
        count=0
        for name in paths:
            source=Path(name)
            try:import_file(LIBRARY,source);count+=1
            except (OSError,ValueError):continue
        self.refresh();self.status.set(f'Importerade {count} filer')

    def delete_selected(self):
        if not self.selected:return
        if messagebox.askyesno('Papperskorg',f'Flytta {self.selected.name} till papperskorgen?'):
            try:trash_file(LIBRARY,self.trash,self.selected.name);self.selected=None;self.refresh()
            except (OSError,ValueError) as exc:messagebox.showerror('Fel',str(exc))

    def show_trash(self):
        win=tk.Toplevel(self.root);win.title('STAGE OS | PAPPERSKORG');win.geometry('650x450');win.configure(bg='#10161c')
        tk.Label(win,text='PAPPERSKORG',font=('DejaVu Sans',17,'bold'),fg='#6df0c1',bg='#10161c').pack(pady=12)
        entries=tk.Listbox(win,bg='#17212b',fg='white',font=('DejaVu Sans',11),selectbackground='#236c62')
        entries.pack(fill='both',expand=True,padx=15,pady=8)
        self.trash.mkdir(parents=True,exist_ok=True)
        files=sorted((p for p in self.trash.iterdir() if p.is_file() and not p.is_symlink()),reverse=True)
        for file in files:entries.insert('end',file.name)
        def restore():
            idx=entries.curselection()
            if not idx:return
            try:restore_file(LIBRARY,files[idx[0]]);win.destroy();self.refresh()
            except (OSError,ValueError) as exc:messagebox.showerror('Återställning',str(exc))
        ttk.Button(win,text='ÅTERSTÄLL MARKERAD',command=restore).pack(pady=12)

    def network(self):
        if shutil.which('nm-connection-editor'):
            subprocess.Popen(['nm-connection-editor'],stdin=subprocess.DEVNULL)
        else:messagebox.showinfo('Nätverk','NetworkManager saknas. Använd nmcli från terminalen.')

    def load_setlist(self):
        try:
            data=json.loads(self.setlist_path.read_text(encoding='utf-8'))
            return [x for x in data if isinstance(x,str) and '/' not in x and '\\' not in x][:500]
        except (OSError,ValueError,TypeError):return []

    def save_setlist(self):
        self.setlist_path.parent.mkdir(parents=True,exist_ok=True)
        temp=self.setlist_path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.setlist,ensure_ascii=False,indent=2),encoding='utf-8')
        temp.replace(self.setlist_path)

    def add_setlist(self):
        if not self.is_text():
            messagebox.showinfo('Setlist','Välj en textfil först.');return
        if self.selected.name not in self.setlist:
            self.setlist.append(self.selected.name);self.save_setlist()
        self.status.set('Tillagd i setlist: '+self.selected.name)

    def show_setlist(self):
        win=tk.Toplevel(self.root);win.title('STAGE OS | SETLIST');win.geometry('550x580');win.configure(bg='#10161c')
        tk.Label(win,text='SETLIST / LIVE MODE',fg='#6df0c1',bg='#10161c',font=('DejaVu Sans',17,'bold')).pack(pady=16)
        items=tk.Listbox(win,font=('DejaVu Sans',15),bg='#17212b',fg='white',selectbackground='#236c62',exportselection=False)
        items.pack(fill='both',expand=True,padx=18,pady=10)
        def update():
            items.delete(0,'end')
            for i,name in enumerate(self.setlist,1):items.insert('end',f'{i:02}   {name}')
        def chosen():
            selection=items.curselection()
            return selection[0] if selection else None
        def launch(_=None):
            i=chosen()
            if i is None:return
            path=LIBRARY/self.setlist[i]
            if path.is_file() and not path.is_symlink() and path.suffix.lower() in TEXT_EXT:self.open_text(path)
            else:messagebox.showwarning('Saknad fil','Låten finns inte längre i biblioteket.')
        def move(delta):
            i=chosen()
            if i is None or not 0<=i+delta<len(self.setlist):return
            self.setlist[i],self.setlist[i+delta]=self.setlist[i+delta],self.setlist[i]
            self.save_setlist();update();items.selection_set(i+delta)
        def remove():
            i=chosen()
            if i is not None:self.setlist.pop(i);self.save_setlist();update()
        items.bind('<Double-Button-1>',launch)
        bar=tk.Frame(win,bg='#10161c');bar.pack(pady=12)
        for label,action in [('ÖPPNA',launch),('UPP',lambda:move(-1)),('NER',lambda:move(1)),('TA BORT',remove)]:
            ttk.Button(bar,text=label,command=action).pack(side='left',padx=5)
        update()

    def rename_selected(self):
        if not self.selected:return
        old=self.selected
        name=simpledialog.askstring('Byt namn','Nytt filnamn:',initialvalue=old.name,parent=self.root)
        if not name or name==old.name:return
        if name!=Path(name).name or name in ('.','..') or any(ord(c)<32 for c in name) or Path(name).suffix.lower()!=old.suffix.lower():
            messagebox.showerror('Ogiltigt namn','Behåll filändelsen och använd ett enkelt filnamn.');return
        new=LIBRARY/name
        if new.exists():messagebox.showerror('Finns redan','En fil med namnet finns redan.');return
        old.rename(new)
        self.setlist=[name if x==old.name else x for x in self.setlist];self.save_setlist()
        self.selected=new;self.refresh()

    def open_folder(self):
        if shutil.which('xdg-open'):subprocess.Popen(['xdg-open',str(LIBRARY)],stdin=subprocess.DEVNULL)
        else:messagebox.showinfo('Bibliotek',str(LIBRARY))

    def close(self):self.audio.stop();self.root.destroy()

def main():
    root=tk.Tk();Desktop(root);root.mainloop()

if __name__=='__main__':main()
