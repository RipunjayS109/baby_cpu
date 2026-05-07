# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_baby_cpu(dut):

    dut._log.info("Start Baby CPU Test")

    # 10 ns clock period = 100 MHz
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # -------------------------------------------------
    # Reset
    # -------------------------------------------------
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1

    await ClockCycles(dut.clk, 1)

    # After reset output should be zero
    assert int(dut.uo_out.value) == 0

    # -------------------------------------------------
    # Test Pattern 1
    # -------------------------------------------------
    test_val1 = 0xAA

    dut._log.info(f"Applying ui_in = 0x{test_val1:02X}")

    dut.ui_in.value = test_val1

    # Cycle 1 -> INP
    # Cycle 2 -> OUT
    await ClockCycles(dut.clk, 2)

    out1 = int(dut.uo_out.value)

    dut._log.info(f"uo_out = 0x{out1:02X}")

    assert out1 == test_val1, \
        f"Expected 0x{test_val1:02X}, got 0x{out1:02X}"

    # -------------------------------------------------
    # OUTIO verification
    # -------------------------------------------------
    # Next cycle executes OUTIO
    await ClockCycles(dut.clk, 1)

    io_out = int(dut.uio_out.value)
    io_oe = int(dut.uio_oe.value)

    dut._log.info(f"uio_out = 0x{io_out:02X}")
    dut._log.info(f"uio_oe  = 0x{io_oe:02X}")

    assert io_out == test_val1, \
        f"Expected uio_out = 0x{test_val1:02X}, got 0x{io_out:02X}"

    assert io_oe == 0xFF, \
        f"Expected uio_oe = 0xFF, got 0x{io_oe:02X}"

    # -------------------------------------------------
    # Test Pattern 2
    # -------------------------------------------------
    test_val2 = 0x3C

    dut._log.info(f"Applying ui_in = 0x{test_val2:02X}")

    dut.ui_in.value = test_val2

    # Wait through JMP + INP + OUT
    await ClockCycles(dut.clk, 3)

    out2 = int(dut.uo_out.value)

    dut._log.info(f"uo_out = 0x{out2:02X}")

    assert out2 == test_val2, \
        f"Expected 0x{test_val2:02X}, got 0x{out2:02X}"

    dut._log.info("All tests passed successfully")
