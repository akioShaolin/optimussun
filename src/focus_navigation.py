"""Apoio pequeno e reutilizável para foco em janelas auxiliares Tkinter."""

import tkinter as tk


def _usable(widget):
    try:
        return widget.winfo_exists() and widget.winfo_viewable() and str(widget.cget("state")) != "disabled"
    except (AttributeError, tk.TclError):
        return False


def focus_first(window, preferred=None):
    """Foca um controle útil depois que geometria e estados estiverem prontos."""
    def apply():
        if not window.winfo_exists():
            return
        target = preferred if preferred is not None and _usable(preferred) else None
        if target is None:
            try:
                candidate = window.nametowidget(window.tk.call("tk_focusNext", window._w))
                target = candidate if candidate is not window and _usable(candidate) else None
            except (KeyError, tk.TclError):
                target = None
        if target is not None:
            target.focus_set()

    window.after_idle(apply)


def restore_focus_on_destroy(window, opener):
    """Devolve o foco sem interferir na modalidade existente da janela."""
    if opener is None:
        return

    def restore(event):
        if event.widget is not window:
            return
        try:
            owner = opener.winfo_toplevel()
            owner.after_idle(lambda: opener.focus_set() if _usable(opener) else None)
        except tk.TclError:
            pass

    window.bind("<Destroy>", restore, add="+")


def keep_focused_widget_visible(window, canvas):
    """Rola um canvas quando Tab leva o foco para fora de sua área visível."""
    def reveal(event):
        widget = event.widget
        try:
            if widget.winfo_toplevel() is not window or widget is canvas:
                return
            canvas.update_idletasks()
            top = widget.winfo_rooty() - canvas.winfo_rooty()
            bottom = top + widget.winfo_height()
            if top < 0:
                canvas.yview_scroll(-1, "units")
            elif bottom > canvas.winfo_height():
                canvas.yview_scroll(1, "units")
        except tk.TclError:
            pass

    window.bind("<FocusIn>", reveal, add="+")


def prepare_toplevel(window, opener=None, initial=None, canvas=None):
    """Instala somente foco inicial/retorno e, opcionalmente, rolagem por foco."""
    restore_focus_on_destroy(window, opener)
    if canvas is not None:
        keep_focused_widget_visible(window, canvas)
    focus_first(window, initial)
