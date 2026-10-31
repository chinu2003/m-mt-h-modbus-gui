# Mitsubishi M-MT-H Modbus TCP GUI

A Python desktop application for communicating with a Mitsubishi M-MT-H device over Modbus TCP. The project is intended for learning, bench testing, and controlled commissioning.

> **Safety:** This is not a safety-rated control system. Verify every Modbus address, module configuration, data type, scaling, and output range against the official Mitsubishi manual before connecting to real equipment. Test output writes with the controlled machine in a safe state. Keep hardwired interlocks and emergency stops independent of this application.

## Features

- Connect to a Modbus TCP server using an IP address and TCP port.
- Display digital input and digital output states.
- Command digital outputs ON/OFF.
- Read analog input registers and analog output holding registers.
- Write raw analog output register values.
- Display communication messages and write read-back results.
- Run against a local Modbus simulator instead of physical hardware.

## Project files

A simple repository layout is:

```text
m-mt-h-modbus-gui/
├── m_mth_gui.py
├── m_mth_simulator.py
├── README.md
└── .gitignore
```

Keep the GUI and simulator scripts in the same project folder.

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or later
- `pip`
- Git for Windows
- A Mitsubishi M-MT-H device for hardware testing, or a compatible local Modbus TCP simulator

The Python `py` launcher is optional. The commands below use `python`, which works when Python is installed and available on PATH.

## 1. Check Python

Open Command Prompt and run:

```cmd
python --version
python -m pip --version
```

If `python` is not recognized, install Python from <https://www.python.org/downloads/windows/> and enable **Add python.exe to PATH** during installation. Close and reopen Command Prompt after installation.

## 2. Create the project folder

```cmd
mkdir "E:\Modular Check"
cd /d "E:\Modular Check"
```

Copy `m_mth_gui.py` and `m_mth_simulator.py` into this folder.

## 3. Create a virtual environment (recommended)

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

When activated, Command Prompt normally displays `(.venv)` at the start of the prompt. Use this environment whenever you work on this project.

## 4. Install PyModbus

```cmd
python -m pip install pymodbus
python -c "import pymodbus; print(pymodbus.__version__)"
```

Record the installed PyModbus version. PyModbus APIs have changed between releases. The simulator must use the API supported by the installed version. Newer releases use `SimData` and `SimDevice`; older datastore examples using `ModbusDeviceContext`, `ModbusSequentialDataBlock`, or `setValues()` may produce deprecation warnings or errors.

If you need a reproducible environment, after confirming both scripts work, save the dependency version:

```cmd
python -m pip freeze > requirements.txt
```

On another PC, dependencies can then be installed with:

```cmd
python -m pip install -r requirements.txt
```

## 5. Configure the connection

At the top of `m_mth_gui.py`, configure the target:

```python
PLC_IP = "192.168.3.100"
PLC_PORT = 502
UNIT_ID = 1
```

For local simulation, use:

```python
PLC_IP = "127.0.0.1"
PLC_PORT = 5020
UNIT_ID = 1
```

Use the real device address only when you intend to communicate with the physical M-MT-H. Ensure the PC and device are on compatible network subnets and that TCP port 502 is reachable.

## 6. Configure I/O addresses

The example project has these starting-address variables:

```python
DI_START = 0
DO_START = 2000
AI_START = 1000
AO_START = 3000
```

They represent the example map used in the sample code:

| Variable | Purpose | Example start address |
|---|---|---:|
| `DI_START` | Discrete inputs | `0` |
| `DO_START` | Coils / digital outputs | `2000` |
| `AI_START` | Input registers / analog inputs | `1000` |
| `AO_START` | Holding registers / analog outputs | `3000` |

**These are example addresses, not a substitute for the exact address map of the installed M-MT-H firmware and I/O modules.** Modbus addresses are often documented using different reference-number conventions. Confirm whether the manual uses zero-based protocol offsets or reference notation, and adjust the Python addresses accordingly.

The sample GUI displays a limited number of points for demonstration. Extend the display only after confirming the available I/O points and address ranges.

## 7. Run with the simulator

1. Configure `m_mth_gui.py` to use `127.0.0.1` and port `5020`.
2. Open the first Command Prompt in the project folder and activate the environment if needed:

   ```cmd
   cd /d "E:\Modular Check"
   .venv\Scripts\activate
   ```

3. Start the simulator:

   ```cmd
   python m_mth_simulator.py
   ```

4. Keep that window open.
5. Open a second Command Prompt, go to the same folder, activate `.venv`, and start the GUI:

   ```cmd
   cd /d "E:\Modular Check"
   .venv\Scripts\activate
   python m_mth_gui.py
   ```

6. Click **Connect** in the GUI.
7. Check the displayed digital and analog values.
8. Test digital output commands and confirm that the GUI reads back the simulated output state.
9. Test analog writes only against the simulator.

If the simulator fails to start, check the installed version and consult the matching PyModbus documentation: <https://pymodbus.readthedocs.io/>. The simulator API is version-dependent. Do not assume an old `ModbusDeviceContext.setValues()` example will work with a release that uses `SimData` and `SimDevice`.

## 8. Run against the physical M-MT-H

Before connecting to physical hardware:

1. Stop the simulator.
2. Confirm the M-MT-H IP address, subnet, TCP port, Unit ID, firmware version, and Modbus server settings.
3. Confirm that no other Modbus TCP client is occupying the device connection if the device supports only one client.
4. Change the GUI configuration to the real device IP and port.
5. Verify every digital and analog address against the official Mitsubishi manual and the installed module configuration.
6. Confirm output electrical ratings, signal ranges, scaling, and machine safe-state requirements.
7. Start with read-only tests.
8. Test one output at a time under an approved safe test procedure.
9. Verify the physical signal independently. A successful Modbus write response or register read-back does not prove that the connected actuator or process behaved as intended.

Do not use arbitrary addresses or raw analog values on live equipment. Analog register values in the sample are raw integers; they are not automatically volts, milliamps, temperature, or engineering units.

## 9. Common commands

Run the GUI:

```cmd
python m_mth_gui.py
```

Run the simulator:

```cmd
python m_mth_simulator.py
```

Check Python:

```cmd
python --version
```

Check PyModbus:

```cmd
python -c "import pymodbus; print(pymodbus.__version__)"
```

Install dependencies:

```cmd
python -m pip install pymodbus
```

## 10. Create a Git repository

Install Git for Windows from <https://git-scm.com/download/win>. Open a new Command Prompt and verify:

```cmd
git --version
```

Set your Git author details (use the name and email associated with your GitHub account):

```cmd
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Go to the project directory:

```cmd
cd /d "E:\Modular Check"
```

Initialize Git and inspect the files:

```cmd
git init
git status
```

Create a `.gitignore` file so the virtual environment and Python cache are not committed. In Command Prompt:

```cmd
notepad .gitignore
```

Paste and save:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.env
.idea/
.vscode/
```

Add and commit the project:

```cmd
git add m_mth_gui.py m_mth_simulator.py README.md .gitignore
git commit -m "Initial Mitsubishi M-MT-H Modbus TCP GUI"
```

If you created `requirements.txt`, add it too:

```cmd
git add requirements.txt
git commit -m "Add Python dependencies"
```

## 11. Create a GitHub repository and push

1. Sign in at <https://github.com/>.
2. Select **New repository**.
3. Enter a repository name, for example `m-mt-h-modbus-gui`.
4. Choose Public or Private as appropriate.
5. For an existing local project, do not initialize the GitHub repository with a README, license, or `.gitignore`; this avoids an unnecessary first-commit merge.
6. Create the repository.
7. Copy the repository HTTPS URL from GitHub. It will look like:

   ```text
   https://github.com/YOUR-USERNAME/m-mt-h-modbus-gui.git
   ```

8. In Command Prompt, add the remote and push:

   ```cmd
   cd /d "E:\Modular Check"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/m-mt-h-modbus-gui.git
   git push -u origin main
   ```

Replace the example URL with your actual repository URL. GitHub may prompt you to authenticate. Follow the browser sign-in or credential-manager prompt. Do not put a GitHub password or personal access token directly into the remote URL or commit it to the repository.

### Later updates

After editing your code:

```cmd
git status
git add .
git commit -m "Describe the changes"
git push
```

Use a meaningful commit message, for example:

```cmd
git commit -m "Improve digital output readback"
```

## 12. Troubleshooting

| Problem | Checks |
|---|---|
| `python` is not recognized | Install Python and enable Add Python to PATH; reopen Command Prompt. |
| `No module named pymodbus` | Activate `.venv` and run `python -m pip install pymodbus`. |
| `py` is not recognized | Use `python` instead of `py`. |
| Simulator API error | Check `python -c "import pymodbus; print(pymodbus.__version__)"` and use documentation for that release. |
| GUI cannot connect to simulator | Start the simulator first; confirm GUI uses `127.0.0.1:5020`. |
| GUI cannot connect to M-MT-H | Check IP/subnet, Ethernet, server settings, port 502, and whether another client is connected. |
| Write acknowledged but output does not operate | Verify address mapping, module configuration, wiring, interlocks, output power, and physical state. |
| Analog value looks incorrect | Confirm module type, configured signal range, signedness, scaling, and word format. |

## 13. Suggested repository checklist

- [ ] `m_mth_gui.py` is present.
- [ ] `m_mth_simulator.py` is present and tested with the installed PyModbus version.
- [ ] `README.md` is present.
- [ ] `.gitignore` excludes `.venv/` and `__pycache__/`.
- [ ] No passwords, tokens, customer data, or sensitive network information are committed.
- [ ] Example addresses are clearly labelled as examples until verified.
- [ ] Simulator testing is completed before any live output test.
- [ ] `git status` is clean after pushing.

## References

- Mitsubishi Electric: <https://www.mitsubishielectric.in/>
- PyModbus documentation: <https://pymodbus.readthedocs.io/>
- PyModbus 4.0 upgrade guide: <https://pymodbus.readthedocs.io/en/dev/source/upgrade_40.html>
- Git documentation: <https://git-scm.com/doc>
- GitHub documentation: <https://docs.github.com/>
