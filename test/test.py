# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_baby_cpu(dut):

    dut._log.info("Starting Baby CPU Test")

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

    dut._log.info("Reset released")

    # Allow CPU to begin execution
    await ClockCycles(dut.clk, 2)

    # -------------------------------------------------
    # Test 1
    # -------------------------------------------------
    test_val1 = 0xAA

    dut._log.info(f"Applying ui_in = 0x{test_val1:02X}")

    dut.ui_in.value = test_val1

    # Wait for:
    # INP -> OUT -> OUTIO -> JMP
    await ClockCycles(dut.clk, 5)

    observed1 = dut.uo_out.value.to_unsigned()

    dut._log.info(f"uo_out = 0x{observed1:02X}")

    assert observed1 == test_val1, \
        f"Expected 0x{test_val1:02X}, got 0x{observed1:02X}"

    dut._log.info("Test 1 passed")

    # -------------------------------------------------
    # Test 2
    # -------------------------------------------------
    test_val2 = 0x3C

    dut._log.info(f"Applying ui_in = 0x{test_val2:02X}")

    dut.ui_in.value = test_val2

    await ClockCycles(dut.clk, 5)

    observed2 = dut.uo_out.value.to_unsigned()

    dut._log.info(f"uo_out = 0x{observed2:02X}")

    assert observed2 == test_val2, \
        f"Expected 0x{test_val2:02X}, got 0x{observed2:02X}"

    dut._log.info("Test 2 passed")

    # -------------------------------------------------
    # Optional OUTIO pulse test
    # -------------------------------------------------
    test_val3 = 0xF0

    dut._log.info(f"Applying ui_in = 0x{test_val3:02X} for OUTIO test")

    dut.ui_in.value = test_val3

    # Align exactly with OUTIO cycle
    await ClockCycles(dut.clk, 3)

    io_out = dut.uio_out.value.to_unsigned()
    io_oe = dut.uio_oe.value.to_unsigned()

    dut._log.info(f"uio_out = 0x{io_out:02X}")
    dut._log.info(f"uio_oe  = 0x{io_oe:02X}")

    assert io_out == test_val3, \
        f"Expected uio_out = 0x{test_val3:02X}, got 0x{io_out:02X}"

    assert io_oe == 0xFF, \
        f"Expected uio_oe = 0xFF, got 0x{io_oe:02X}"

    dut._log.info("OUTIO test passed")

    dut._log.info("All tests passed successfully")
