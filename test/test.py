# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_baby_cpu(dut):
    dut._log.info("Starting TinyTapeout Baby CPU Test")

    # 10 ns clock period = 100 MHz
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # -----------------------------
    # Reset sequence
    # -----------------------------
    dut._log.info("Applying reset")

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1

    await ClockCycles(dut.clk, 1)

    # -----------------------------
    # Test 1
    # ui_in -> acc -> uo_out
    # -----------------------------
    test_value_1 = 0xAA

    dut._log.info(f"Testing ui_in = 0x{test_value_1:02X}")

    dut.ui_in.value = test_value_1

    # Program flow:
    # Cycle 1 -> INP
    # Cycle 2 -> OUT
    # Cycle 3 -> OUTIO
    # Cycle 4 -> JMP
    await ClockCycles(dut.clk, 4)

    assert dut.uo_out.value.integer == test_value_1, \
        f"Expected uo_out = 0x{test_value_1:02X}, got 0x{dut.uo_out.value.integer:02X}"

    dut._log.info("Test 1 passed")

    # -----------------------------
    # Test 2
    # Another input pattern
    # -----------------------------
    test_value_2 = 0x3C

    dut._log.info(f"Testing ui_in = 0x{test_value_2:02X}")

    dut.ui_in.value = test_value_2

    await ClockCycles(dut.clk, 4)

    assert dut.uo_out.value.integer == test_value_2, \
        f"Expected uo_out = 0x{test_value_2:02X}, got 0x{dut.uo_out.value.integer:02X}"

    dut._log.info("Test 2 passed")

    # -----------------------------
    # Test OUTIO pulse behavior
    # -----------------------------
    dut._log.info("Checking OUTIO behavior")

    dut.ui_in.value = 0xF0

    # Wait until OUTIO instruction executes
    await ClockCycles(dut.clk, 3)

    assert dut.uio_out.value.integer == 0xF0, \
        "uio_out did not match expected value"

    assert dut.uio_oe.value.integer == 0xFF, \
        "uio_oe should be enabled during OUTIO"

    dut._log.info("OUTIO behavior verified")

    dut._log.info("All tests passed successfully")
