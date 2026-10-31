
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pymodbus.client import ModbusTcpClient

# ==================================================
# MITSUBISHI M-MT-H MODBUS TCP CONFIGURATION
# ==================================================
# PLC_IP = "192.168.3.100"
# PLC_PORT = 502
# UNIT_ID = 1

# PLC_IP = "127.0.0.1"
PLC_IP = "192.168.3.100"
PLC_PORT = 502
UNIT_ID = 1

DI_START = 0
DO_START = 2000
AI_START = 1000
AO_START = 3000

client = None
connected = False

# ==================================================
# CREATE MAIN WINDOW
# ==================================================
root = tk.Tk()
root.title("Mitsubishi M-MT-H - Modbus TCP I/O Monitor")
root.geometry("950x720")
root.minsize(800, 600)

style = ttk.Style()
style.theme_use("clam")

style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
style.configure("Section.TLabelframe.Label",
                font=("Segoe UI", 10, "bold"))

# ==================================================
# HELPER FUNCTIONS
# ==================================================
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")

    log_box.configure(state="normal")
    log_box.insert("end", f"[{timestamp}] {message}\n")
    log_box.see("end")
    log_box.configure(state="disabled")


def set_indicator(label, value):
    label.configure(
        text="ON" if value else "OFF",
        foreground="green" if value else "gray"
    )


def show_error(title, message):
    messagebox.showerror(title, message)


def read_registers(function, address, count):
    """Read registers and report communication errors."""
    if not connected or client is None:
        log("ERROR: Connect to the device first.")
        return None

    try:
        result = function(
            address=address,
            count=count,
            device_id=UNIT_ID
        )

        if result.isError():
            log(f"READ ERROR at address {address}: {result}")
            return None

        return result

    except Exception as exc:
        log(f"COMMUNICATION ERROR: {exc}")
        return None


# ==================================================
# CONNECT / DISCONNECT
# ==================================================
def connect_device():
    global client, connected

    if connected:
        log("Already connected.")
        return

    try:
        client = ModbusTcpClient(
            host=PLC_IP,
            port=PLC_PORT,
            timeout=2
        )

        if client.connect():
            connected = True
            connection_label.configure(
                text="CONNECTED", foreground="green"
            )
            connect_button.configure(text="Disconnect")
            log(f"Connected to {PLC_IP}:{PLC_PORT}")
            refresh_io()
        else:
            client.close()
            client = None
            log("Connection failed. Check IP, cable and port 502.")
            show_error(
                "Connection Failed",
                "Cannot connect to M-MT-H.\n"
                "Check IP address, subnet and Ethernet connection."
            )

    except Exception as exc:
        connected = False
        log(f"CONNECTION ERROR: {exc}")


def disconnect_device():
    global client, connected

    connected = False

    if client is not None:
        client.close()
        client = None

    connection_label.configure(
        text="DISCONNECTED", foreground="red"
    )
    connect_button.configure(text="Connect")
    log("Disconnected from device.")


def toggle_connection():
    if connected:
        disconnect_device()
    else:
        connect_device()


# ==================================================
# READ DIGITAL AND ANALOG I/O
# ==================================================
def refresh_io():
    if not connected or client is None:
        log("Connect before reading I/O.")
        return

    # Digital inputs: read-only
    result = read_registers(
        client.read_discrete_inputs, DI_START, 16
    )

    if result is not None:
        for i in range(16):
            set_indicator(di_labels[i], result.bits[i])

    # Digital outputs: read current states
    result = read_registers(
        client.read_coils, DO_START, 16
    )

    if result is not None:
        for i in range(16):
            set_indicator(do_labels[i], result.bits[i])

    # Analog inputs: raw register values
    result = read_registers(
        client.read_input_registers, AI_START, 4
    )

    if result is not None:
        for i, value in enumerate(result.registers):
            ai_labels[i].configure(text=str(value))

    # Analog outputs: holding register values
    result = read_registers(
        client.read_holding_registers, AO_START, 4
    )

    if result is not None:
        for i, value in enumerate(result.registers):
            ao_labels[i].configure(text=str(value))

    log("I/O refresh completed.")


# ==================================================
# WRITE DIGITAL OUTPUT ON / OFF
# ==================================================
def write_output(index, state):
    if not connected or client is None:
        show_error("Not Connected", "Connect to M-MT-H first.")
        return

    address = DO_START + index
    state_text = "ON" if state else "OFF"

    confirm = messagebox.askyesno(
        "Confirm Output",
        f"Set output {index} to {state_text}?\n"
        f"Modbus address: {address}\n\n"
        "Ensure the connected machine is safe to operate."
    )

    if not confirm:
        log(f"Cancelled output {index} {state_text}.")
        return

    try:
        result = client.write_coil(
            address=address,
            value=state,
            device_id=UNIT_ID
        )

        if result.isError():
            log(f"WRITE FAILED: DO {index}: {result}")
            show_error("Write Failed", str(result))
            return

        log(f"WRITE ACKNOWLEDGED: DO {index} requested {state_text}")

        # Read back the output to verify its reported state
        check = client.read_coils(
            address=address,
            count=1,
            device_id=UNIT_ID
        )

        if check.isError():
            log(f"READ-BACK FAILED for DO {index}.")
            return

        actual_state = check.bits[0]
        set_indicator(do_labels[index], actual_state)

        if actual_state == state:
            log(f"SUCCESS: DO {index} read-back is {state_text}")
        else:
            log(f"WARNING: DO {index} read-back differs from request.")

    except Exception as exc:
        log(f"OUTPUT ERROR: {exc}")


# ==================================================
# WRITE ANALOG OUTPUT
# ==================================================
def write_analog():
    if not connected or client is None:
        show_error("Not Connected", "Connect to M-MT-H first.")
        return

    try:
        index = int(ao_index_var.get())
        value = int(analog_value_var.get())

        if not 0 <= index <= 255:
            raise ValueError("Analog output index must be 0-255.")

        if not 0 <= value <= 65535:
            raise ValueError("Raw value must be 0-65535.")

        address = AO_START + index

        confirm = messagebox.askyesno(
            "Confirm Analog Write",
            f"Address: {address}\nRaw value: {value}\n\n"
            "Verify the actual module, scaling and safe range first.\n"
            "Continue?"
        )

        if not confirm:
            log("Analog write cancelled.")
            return

        result = client.write_register(
            address=address,
            value=value,
            device_id=UNIT_ID
        )

        if result.isError():
            log(f"ANALOG WRITE FAILED: {result}")
            show_error("Write Failed", str(result))
            return

        log(f"ANALOG WRITE ACKNOWLEDGED: address {address}, value {value}")

        check = client.read_holding_registers(
            address=address,
            count=1,
            device_id=UNIT_ID
        )

        if check.isError():
            log("Analog write acknowledged, but read-back failed.")
        else:
            actual = check.registers[0]
            ao_labels[index if index < 4 else 0].configure(
                text=str(actual)
            )
            log(f"ANALOG READ-BACK: address {address}, value {actual}")

            if actual == value:
                log("SUCCESS: Analog register matches requested value.")
            else:
                log("WARNING: Analog register differs from requested value.")

    except ValueError as exc:
        show_error("Invalid Input", str(exc))
    except Exception as exc:
        log(f"ANALOG WRITE ERROR: {exc}")


# ==================================================
# BUILD GUI
# All callbacks are defined before buttons are created.
# ==================================================
header = ttk.Frame(root, padding=12)
header.pack(fill="x")

ttk.Label(
    header,
    text="M-MT-H MODBUS TCP I/O MONITOR",
    style="Title.TLabel"
).pack(side="left")

connection_label = ttk.Label(
    header,
    text="DISCONNECTED",
    foreground="red"
)
connection_label.pack(side="right")

toolbar = ttk.Frame(root, padding=(12, 0, 12, 16))
toolbar.pack(fill="x")

ttk.Label(
    toolbar,
    text=f"Device: {PLC_IP}:{PLC_PORT}"
).pack(side="left")

connect_button = ttk.Button(
    toolbar,
    text="Connect",
    command=toggle_connection
)
connect_button.pack(side="right", padx=4)

ttk.Button(
    toolbar,
    text="Refresh I/O",
    command=refresh_io
).pack(side="right", padx=4)

# Digital inputs
di_frame = ttk.LabelFrame(
    root, text="DIGITAL INPUTS - READ ONLY", padding=10
)
di_frame.pack(fill="x", padx=12, pady=5)

di_labels = []

for i in range(16):
    cell = ttk.Frame(di_frame, padding=4)
    cell.grid(row=0, column=i, sticky="nsew")
    ttk.Label(cell, text=f"DI {i}").pack()
    label = ttk.Label(
        cell, text="UNKNOWN", width=9,
        anchor="center", relief="groove", padding=5
    )
    label.pack(pady=4)
    di_labels.append(label)
    di_frame.columnconfigure(i, weight=1)

# Digital outputs
do_frame = ttk.LabelFrame(
    root, text="DIGITAL OUTPUTS - READ / WRITE", padding=10
)
do_frame.pack(fill="x", padx=12, pady=5)

do_labels = []

for i in range(16):
    row = i // 4
    col = i % 4

    cell = ttk.Frame(do_frame, padding=5)
    cell.grid(row=row, column=col, sticky="ew")
    do_frame.columnconfigure(col, weight=1)

    ttk.Label(cell, text=f"DO {i}").pack(side="left")

    label = ttk.Label(
        cell, text="UNKNOWN", width=9,
        anchor="center", relief="groove", padding=4
    )
    label.pack(side="left", padx=5)
    do_labels.append(label)

    ttk.Button(
        cell, text="ON",
        command=lambda n=i: write_output(n, True)
    ).pack(side="left", padx=2)

    ttk.Button(
        cell, text="OFF",
        command=lambda n=i: write_output(n, False)
    ).pack(side="left", padx=2)
# ========================================================================================================================
# Analog input values
ai_frame = ttk.LabelFrame(
    root, text="ANALOG INPUTS - RAW VALUES", padding=10
)
ai_frame.pack(fill="x", padx=12, pady=5)

ai_labels = []

for i in range(4):
    ttk.Label(
        ai_frame, text=f"AI {i} (address {AI_START + i})"
    ).grid(row=i // 2, column=(i % 2) * 2,
           sticky="w", padx=8, pady=4)

    label = ttk.Label(ai_frame, text="--", width=12)
    label.grid(row=i // 2, column=(i % 2) * 2 + 1,
               sticky="w", padx=8, pady=4)
    ai_labels.append(label)

# Analog output values and write controls
ao_frame = ttk.LabelFrame(
    root, text="ANALOG OUTPUTS - RAW VALUES", padding=10
)
ao_frame.pack(fill="x", padx=12, pady=5)

ao_labels = []

for i in range(4):
    ttk.Label(
        ao_frame, text=f"AO {i} (address {AO_START + i})"
    ).grid(row=0, column=i, padx=8, pady=3)

    label = ttk.Label(
        ao_frame, text="--", width=10, anchor="center"
    )
    label.grid(row=1, column=i, padx=8, pady=3)
    ao_labels.append(label)

analog_controls = ttk.Frame(ao_frame)
analog_controls.grid(
    row=2, column=0, columnspan=4, sticky="w", pady=8
)

ttk.Label(analog_controls, text="Output index:").pack(side="left")
ao_index_var = tk.StringVar(value="0")
ttk.Entry(
    analog_controls, textvariable=ao_index_var, width=6
).pack(side="left", padx=5)

ttk.Label(analog_controls, text="Raw value:").pack(side="left")
analog_value_var = tk.StringVar(value="0")
ttk.Entry(
    analog_controls, textvariable=analog_value_var, width=10
).pack(side="left", padx=5)

ttk.Button(
    analog_controls,
    text="Write Analog Value",
    command=write_analog
).pack(side="left", padx=5)

# Communication log
log_frame = ttk.LabelFrame(
    root, text="OPERATION RESULTS / COMMUNICATION LOG", padding=8
)
log_frame.pack(fill="both", expand=True, padx=12, pady=5)

log_box = tk.Text(
    log_frame, height=7, state="disabled",
    font=("Consolas", 9), wrap="word"
)
log_box.pack(fill="both", expand=True)


# Periodic refresh
def auto_refresh():
    if connected:
        refresh_io()

    root.after(2000, auto_refresh)


def close_app():
    disconnect_device()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)

log("Application ready. Click Connect to start.")
root.after(2000, auto_refresh)
root.mainloop()
