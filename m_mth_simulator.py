
from pymodbus.server import StartTcpServer
from pymodbus.simulator import SimData, SimDevice, DataType

# Local simulation only
HOST = "127.0.0.1"
PORT = 5020
UNIT_ID = 1

# Simulated digital input values
di_values = [True, False, True, True, False, False, True, False]

# Simulated digital outputs: initially OFF
do_values = [False] * 8

# Define separate Modbus address spaces:
# tuple order = coils, discrete inputs, holding registers, input registers
device = SimDevice(
    id=UNIT_ID,
    simdata=(
        [
            SimData(
                address=2000,
                values=do_values,
                datatype=DataType.BITS
            )
        ],
        [
            SimData(
                address=0,
                values=di_values,
                datatype=DataType.BITS,
                readonly=True
            )
        ],
        [
            SimData(
                address=3000,
                values=[0] * 8,
                datatype=DataType.REGISTERS
            )
        ],
        [
            SimData(
                address=1000,
                values=[250, 500, 750, 1000],
                datatype=DataType.REGISTERS
            )
        ]
    )
)

print("M-MT-H Modbus TCP simulator")
print(f"Listening on {HOST}:{PORT}")
print("Unit ID:", UNIT_ID)
print("Digital output addresses: 2000-2007")
print("Digital input addresses: 0-7")
print("Analog input addresses: 1000-1003")
print("Analog output addresses: 3000-3007")
print("Press Ctrl+C to stop.")

StartTcpServer(
    context=[device],
    address=(HOST, PORT)
)
