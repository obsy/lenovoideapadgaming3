#!/usr/bin/env python3

# https://wiki.archlinux.org/title/Lenovo_IdeaPad_Gaming_3#System_Performance_Mode

# Works with 15ARH05 (Lenovo IdeaPad Gaming 3)

# 2025 Cezary Jackiewicz <cezary@eko.one.pl>

import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

css = b"""
radiobutton:focus {
    outline: none;
    box-shadow: none;
}
"""

style_provider = Gtk.CssProvider()
style_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

CMODE_PATH = "/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00/conservation_mode"

def run_pkexec_cmd(cmd):
    try:
        result = subprocess.run(["bash", "-c", cmd],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

class AppWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Lenovo IdeaPad Gaming 3")
        self.set_border_width(20)
        self.set_default_size(400, 220)
        vbox = Gtk.VBox(spacing=20)
        self.add(vbox)

        # Battery Conservation Mode Frame
        cmode_frame = Gtk.Frame(label="Battery Conservation Mode")
        cmode_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        cmode_frame.add(cmode_box)
        vbox.pack_start(cmode_frame, False, False, 0)

        self.cmode_on = Gtk.RadioButton.new_with_label_from_widget(None, "ON")
        self.cmode_off = Gtk.RadioButton.new_with_label_from_widget(self.cmode_on, "OFF")
        cmode_btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        cmode_btn_box.set_margin_start(20)
        cmode_btn_box.set_margin_top(20)
        cmode_btn_box.pack_start(self.cmode_on, False, False, 0)
        cmode_btn_box.pack_start(self.cmode_off, False, False, 0)
        cmode_box.pack_start(cmode_btn_box, False, False, 0)

        self.cmode_status = Gtk.Label()
        cmode_box.pack_start(self.cmode_status, False, False, 0)

        # Rapid Charge Frame
        rapid_frame = Gtk.Frame(label="Rapid Charge")
        rapid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rapid_frame.add(rapid_box)
        vbox.pack_start(rapid_frame, False, False, 0)

        self.rapid_on = Gtk.RadioButton.new_with_label_from_widget(None, "ON")
        self.rapid_off = Gtk.RadioButton.new_with_label_from_widget(self.rapid_on, "OFF")
        rapid_btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        rapid_btn_box.set_margin_start(20)
        rapid_btn_box.set_margin_top(20)
        rapid_btn_box.pack_start(self.rapid_on, False, False, 0)
        rapid_btn_box.pack_start(self.rapid_off, False, False, 0)
        rapid_box.pack_start(rapid_btn_box, False, False, 0)

        self.rapid_status = Gtk.Label()
        rapid_box.pack_start(self.rapid_status, False, False, 0)

        # System Performance Mode Frame
        perf_frame = Gtk.Frame(label="System Performance Mode")
        perf_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        perf_frame.add(perf_box)
        vbox.pack_start(perf_frame, False, False, 0)

        self.perf_bs = Gtk.RadioButton.new_with_label_from_widget(None, "Battery Saving")
        self.perf_ic = Gtk.RadioButton.new_with_label_from_widget(self.perf_bs, "Intelligent Cooling")
        self.perf_ep = Gtk.RadioButton.new_with_label_from_widget(self.perf_ic, "Extreme Performance")
        perf_btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        perf_btn_box.set_margin_start(20)
        perf_btn_box.set_margin_top(20)
        perf_btn_box.pack_start(self.perf_bs, False, False, 0)
        perf_btn_box.pack_start(self.perf_ic, False, False, 0)
        perf_btn_box.pack_start(self.perf_ep, False, False, 0)
        perf_box.pack_start(perf_btn_box, False, False, 0)

        self.perf_status = Gtk.Label()
        perf_box.pack_start(self.perf_status, False, False, 0)

        # Global Save Button
        self.save_button = Gtk.Button(label="Save")
        self.save_button.connect("clicked", self.on_save_clicked)
        vbox.pack_start(self.save_button, False, False, 0)

        # Vars for current state
        self.current_cmode = None
        self.current_rapid = None
        self.current_spm = None

        self.status_label = Gtk.Label()
        vbox.pack_start(self.status_label, False, False, 0)

        self.load_settings()

    def load_settings(self):
        # Conservation Mode
        res = run_pkexec_cmd(f"cat {CMODE_PATH}")
        if res == '1':
            self.cmode_on.set_active(True)
            self.current_cmode = '1'
            self.cmode_status.set_text("")
        elif res == '0':
            self.cmode_off.set_active(True)
            self.current_cmode = '0'
            self.cmode_status.set_text("")
        else:
            self.cmode_status.set_text("Unknown status: " + res)
            self.current_cmode = None

        # Rapid Charge
        cmd = ("modprobe acpi_call; "
               "echo '\\_SB.PCI0.LPC0.EC0.QCHO' > /proc/acpi/call; "
               "cat /proc/acpi/call")
        res = run_pkexec_cmd(cmd)

        if "0x1" in res:
            self.rapid_on.set_active(True)
            self.current_rapid = '1'
            self.rapid_status.set_text("")
        elif "0x0" in res:
            self.rapid_off.set_active(True)
            self.current_rapid = '0'
            self.rapid_status.set_text("")
        else:
            self.rapid_status.set_text("Unknown status: " + res)
            self.current_rapid = None

        # System Performance Mode
        cmd = ("modprobe acpi_call; "
               "echo '\\_SB.PCI0.LPC0.EC0.SPMO' > /proc/acpi/call; "
               "cat /proc/acpi/call")
        res = run_pkexec_cmd(cmd)

        if "0x0" in res:
            self.perf_ic.set_active(True)
            self.current_spm = '0'
            self.perf_status.set_text("")
        elif "0x1" in res:
            self.perf_ep.set_active(True)
            self.current_spm = '1'
            self.perf_status.set_text("")
        elif "0x2" in res:
            self.perf_bs.set_active(True)
            self.current_spm = '2'
            self.perf_status.set_text("")
        else:
            self.rapid_status.set_text("Unknown status: " + res)
            self.current_perf = None

    def on_save_clicked(self, _):
        what_changed = []

        # Battery Conservation Mode
        new_cmode = '1' if self.cmode_on.get_active() else '0'
        if self.current_cmode is not None and new_cmode != self.current_cmode:
            cmd = f"echo {new_cmode} | tee {CMODE_PATH} > /dev/null"
            res = run_pkexec_cmd(cmd)
            what_changed.append("Battery Conservation Mode")

        # Rapid Charge
        new_rapid = '1' if self.rapid_on.get_active() else '0'
        if self.current_rapid is not None and new_rapid != self.current_rapid:
            if new_rapid == '1':
                cmd = "echo '\\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x07' > /proc/acpi/call"
            else:
                cmd = "echo '\\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x08' > /proc/acpi/call"
            res = run_pkexec_cmd(cmd)
            what_changed.append("Rapid Charge")

        # System Performance Mode
        if self.perf_ic.get_active():
            new_spm = '0'
        if self.perf_ep.get_active():
            new_spm = '1'
        if self.perf_bs.get_active():
            new_spm = '2'
        if self.current_spm is not None and new_spm != self.current_spm:
            if new_spm == '0':
                cmd = "echo '\\_SB_.GZFD.WMAA 0 0x2C 2' > /proc/acpi/call"
            if new_spm == '1':
                cmd = "echo '\\_SB_.GZFD.WMAA 0 0x2C 3' > /proc/acpi/call"
            if new_spm == '2':
                cmd = "echo '\\_SB_.GZFD.WMAA 0 0x2C 1' > /proc/acpi/call"
            res = run_pkexec_cmd(cmd)
            what_changed.append("System Performance Mode")

        if not what_changed:
            self.status_label.set_text("No changes")
        else:
            self.load_settings()
            self.status_label.set_text("Sets: " + ", ".join(what_changed))

win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
