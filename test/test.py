# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_baby_cpu(dut):

    dut._log.info("Starting Baby CPU Test")

    # 10 ns clock -> 100 MHz
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # -------------------------
    # Reset
    # -------------------------
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1

    dut._log.info("Reset released")

    # Wait for CPU to start properly
    await ClockCycles(dut.clk, 2)

    # -------------------------
    # Test Pattern 1
    # -------------------------
    test_val = 0xAA

    dut.ui_in.value = test_val

    dut._log.info(f"Applying ui_in = 0x{test_val:02X}")

    # Wait enough cycles for:
    # INP -> OUT -> OUTIO
    await ClockCycles(dut.clk, 5)

    observed = dut.uo_out.value.to_unsigned()

    dut._log.info(f"uo_out = 0x{observed:02X}")

    assert observed == test_val, \
        f"Expected 0x{test_val:02X}, got 0x{observed:02X}"

    # -------------------------
    # Verify OUTIO
    # -------------------------
    io_out = dut.uio_out.value.to_unsigned()
    io_oe = dut.uio_oe.value.to_unsigned()

    dut._log.info(f"uio_out = 0x{io_out:02X}")
    dut._log.info(f"uio_oe  = 0x{io_oe:02X}")

    assert io_out == test_val, "uio_out mismatch"

    # uio_oe may pulse for one cycle only
    # so don't strictly assert it unless sampled exactly

    # -------------------------
    # Test Pattern 2
    # -------------------------
    test_val2 = 0x3C

    dut.ui_in.value = test_val2

    dut._log.info(f"Applying ui_in = 0x{test_val2:02X}")

    await ClockCycles(dut.clk, 5)

    observed2 = dut.uo_out.value.to_unsigned()

    dut._log.info(f"uo_out = 0x{observed2:02X}")

    assert observed2 == test_val2, \
        f"Expected 0x{test_val2:02X}, got 0x{observed2:02X}"

    dut._log.info("All tests passed")
