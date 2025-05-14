#!/usr/bin/env python3
"""
DailyStatus – Tkinter + ttkbootstrap (GitHub–cyborg theme)
Generates an English stand-up report from Git diffs
using Google Gemini API.
"""

import os
import json
import threading
import datetime as dt
from pathlib import Path
from typing import List

import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.scrolled import ScrolledText
from git import Repo, InvalidGitRepositoryError

# ---------- constants ----------
APP_NAME    = "DailyStatus"
CONFIG_PATH = Path.home() / ".daily_status_config.json"
DATE_FMT    = "%Y-%m-%d"
GEMINI_URL  = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.0-flash:generateContent"
)

# ---------- settings I/O ----------
def load_config() -> dict:
    cfg = {
        "project_folder": str(Path.cwd()),
        "report_style": "short",  # short | medium | long
        "branches": [],
        "api_key": "",
        "prompt_template": ""     # persisted prompt text
    }
    if CONFIG_PATH.exists():
        try:
            cfg.update(json.loads(CONFIG_PATH.read_text()))
        except Exception:
            messagebox.showwarning(APP_NAME, "Config corrupted — using defaults.")
    return cfg

def save_config(cfg: dict):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
        messagebox.showinfo(APP_NAME, "Settings saved.")
    except Exception as e:
        messagebox.showerror(APP_NAME, f"Cannot save settings:\n{e}")

# ---------- Git helpers ----------
def list_branches(repo_path: str) -> List[str]:
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        return []
    return [h.name for h in repo.heads]

def gather_diffs(path: str, branches: List[str], date: dt.date) -> List[str]:
    try:
        repo = Repo(path)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not a Git repository.")
    branches = branches or [repo.active_branch.name]
    since = dt.datetime.combine(date, dt.time.min)
    until = dt.datetime.combine(date, dt.time.max)
    diffs: List[str] = []
    for br in branches:
        for commit in repo.iter_commits(br):
            cd = dt.datetime.fromtimestamp(commit.committed_date)
            if not (since <= cd <= until):
                continue
            if commit.parents:
                patch = repo.git.diff(commit.parents[0].hexsha, commit.hexsha)
            else:
                patch = repo.git.show(commit.hexsha)
            diffs.append(f"Commit {commit.hexsha[:7]} on {br}:\n{patch}")
    return diffs

# ---------- prompt parts ----------
sentence_map = {
    "short": "Use 2–3 sentences.",
    "medium": "Use 4–5 sentences.",
    "long": "Use 6–8 sentences."
}
example = (
    "09.04.2025:\n"
    "Added a logging system - integrated the logger into the login (auth/login/route.ts) "
    "and user creation (user/create/route.ts) endpoints, updated audit logs.\n\n"
    "10.04.2025:\n"
    "Implemented MFA for all users - added /api/mfa endpoints (QR code, TOTP), extended login logic, "
    "created migration and userMFA schema, updated middleware."
)

def build_template(project: str, date: dt.date, style: str) -> str:
    fmtd = date.strftime("%d.%m.%Y")
    return (
        f"You are an assistant that writes {style} daily stand-up updates for software engineers.\n"
        f"Project: {project}\n"
        f"Date: {date.strftime('%B %d, %Y')}\n\n"
        f"Here are the detailed code diffs for today:\n\n"
        f"{sentence_map[style]}\n\n"
        f"Generate a status in the exact format of the examples below:\n\n"
        f"{example}\n\n"
        f"Now write only the entry for {fmtd}:"
    )

def build_full_prompt(diffs: List[str], project: str, date: dt.date, style: str) -> str:
    header = build_template(project, date, style)
    diffs_block = "\n\n".join(diffs) if diffs else "No code changes today."
    parts = header.split(sentence_map[style])
    return f"{parts[0]}{diffs_block}\n\n{sentence_map[style]}{parts[1]}"

# ---------- Gemini API call ----------
def generate_with_gemini(prompt: str, api_key: str) -> str:
    url = f"{GEMINI_URL}?key={api_key}"
    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={"contents":[{"parts":[{"text": prompt}]}]},
        timeout=60
    )
    resp.raise_for_status()
    cands = resp.json().get("candidates", [])
    if not cands:
        raise RuntimeError("No response from Gemini API.")
    return "".join(p.get("text","") for p in cands[0]["content"]["parts"]).strip()

# ---------- main UI ----------
if __name__ == "__main__":
    style = Style(theme="cyborg")
    root = style.master
    root.title(APP_NAME)
    root.columnconfigure(1, weight=1)

    cfg = load_config()

    # Copy/paste bindings
    def _copy(event):
        event.widget.event_generate('<<Copy>>'); return 'break'
    def _paste(event):
        event.widget.event_generate('<<Paste>>'); return 'break'
    for cls in ['Text','Entry']:
        root.bind_class(cls, '<Control-c>', _copy)
        root.bind_class(cls, '<Control-C>', _copy)
        root.bind_class(cls, '<Control-v>', _paste)

    # generate helper
    def _generate(repo_path, branches, date_str, rpt_style, api_key, prompt_w, output_w):
        output_w.delete('1.0','end')
        output_w.insert('end','Processing...')
        try:
            date_obj = dt.datetime.strptime(date_str, DATE_FMT).date()
            diffs = gather_diffs(repo_path, branches, date_obj)
            proj = Path(repo_path).stem
            header = build_template(proj, date_obj, rpt_style)
            prompt_w.delete('1.0','end')
            prompt_w.insert('end', header)
            full = build_full_prompt(diffs, proj, date_obj, rpt_style)
            edited = prompt_w.get('1.0','end').strip()
            res = generate_with_gemini(full.replace(header, edited), api_key)
            output_w.delete('1.0','end')
            output_w.insert('end', res)
        except Exception as e:
            output_w.delete('1.0','end')
            messagebox.showerror(APP_NAME, str(e))

    # Widgets
    ttk.Label(root, text="Repository folder:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
    repo_var = tk.StringVar(value=cfg.get("project_folder",""))
    ttk.Entry(root, textvariable=repo_var, width=60, bootstyle="dark").grid(row=0, column=1, sticky="we", padx=6, pady=4)
    ttk.Button(root, text="Browse", bootstyle="secondary-outline",
               command=lambda: repo_var.set(filedialog.askdirectory()))\
               .grid(row=0, column=2, padx=6, pady=4)

    ttk.Label(root, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", padx=6, pady=4)
    date_var = tk.StringVar(value=cfg.get("date", dt.date.today().strftime(DATE_FMT)))
    ttk.Entry(root, textvariable=date_var, width=20, bootstyle="dark")\
       .grid(row=1, column=1, sticky="we", padx=6, pady=4)

    ttk.Label(root, text="Report style:").grid(row=2, column=0, sticky="e", padx=6, pady=4)
    style_var = tk.StringVar(value=cfg.get("report_style","short"))
    ttk.Combobox(root, textvariable=style_var,
                 values=["short","medium","long"], width=16,
                 state="readonly", bootstyle="dark")\
       .grid(row=2, column=1, sticky="we", padx=6, pady=4)

    ttk.Label(root, text="Gemini API key:").grid(row=3, column=0, sticky="e", padx=6, pady=4)
    key_var = tk.StringVar(value=cfg.get("api_key",""))
    ttk.Entry(root, textvariable=key_var, width=50, show="•", bootstyle="dark")\
       .grid(row=3, column=1, columnspan=2, sticky="we", padx=6, pady=4)

    ttk.Label(root, text="Branches (optional):").grid(row=4, column=0, sticky="ne", padx=6, pady=4)
    br_list = tk.Listbox(root, selectmode="multiple", height=6, exportselection=False,
                         bg=style.colors.dark, fg=style.colors.light, highlightthickness=0, bd=0)
    br_list.grid(row=4, column=1, sticky="we", padx=6, pady=4)

    ttk.Label(root, text="Editable prompt:").grid(row=5, column=0, sticky="ne", padx=6, pady=4)
    prompt_text = ScrolledText(root, width=80, height=8, bootstyle="dark")
    prompt_text.grid(row=5, column=1, columnspan=2, sticky="we", padx=6, pady=4)

    # Populate prompt_text with persisted or default template
    if cfg.get("prompt_template"):
        prompt_text.insert('end', cfg["prompt_template"])
    else:
        # default template based on current fields
        default_hdr = build_template(
            Path(repo_var.get() or ".").stem,
            dt.datetime.strptime(date_var.get(), DATE_FMT).date(),
            style_var.get()
        )
        prompt_text.insert('end', default_hdr)

    ttk.Label(root, text="Output:").grid(row=6, column=0, sticky="ne", padx=6, pady=4)
    output_text = ScrolledText(root, width=80, height=10, bootstyle="dark")
    output_text.grid(row=6, column=1, columnspan=2, sticky="we", padx=6, pady=4)

    btn_frame = ttk.Frame(root)
    btn_frame.grid(row=7, column=1, columnspan=2, pady=10, sticky="e")
    ttk.Button(btn_frame, text="Refresh branches", bootstyle="info-outline",
               command=lambda: (
                   br_list.delete(0,'end'),
                   [br_list.insert('end', b) for b in list_branches(repo_var.get())]
               )).pack(side="left", padx=5)

    def on_save():
        cfg.update({
            "project_folder": repo_var.get(),
            "date":          date_var.get(),
            "report_style":  style_var.get(),
            "branches":      [br_list.get(i) for i in br_list.curselection()],
            "api_key":       key_var.get(),
            "prompt_template": prompt_text.get('1.0','end').rstrip()
        })
        save_config(cfg)

    ttk.Button(btn_frame, text="Save settings", bootstyle="primary-outline",
               command=on_save).pack(side="left", padx=5)

    ttk.Button(btn_frame, text="Generate", bootstyle="success-outline",
               command=lambda: threading.Thread(target=lambda: _generate(
                   repo_var.get(),
                   [br_list.get(i) for i in br_list.curselection()],
                   date_var.get(),
                   style_var.get(),
                   key_var.get(),
                   prompt_text,
                   output_text
               ), daemon=True).start()
    ).pack(side="left", padx=5)

    # initial populate branches
    for b in list_branches(cfg.get("project_folder","")):
        br_list.insert('end', b)

    root.mainloop()
