// SPDX-License-Identifier: Apache-2.0
//
// TinyTapeout-friendly minimal 8-bit CPU.
//
// Pin use:
//   ui_in[7:0]   : external input port, readable by the CPU
//   uo_out[7:0]  : CPU output register
//   uio_in[7:0]  : bidirectional data input when CPU reads IO
//   uio_out[7:0] : bidirectional data output when CPU writes IO
//   uio_oe[7:0]  : driven high for one cycle after OUTIO
//
// The CPU is deliberately small:
//   - 8-bit accumulator
//   - 4-bit program counter
//   - 16 x 8-bit program ROM
//   - 16 x 8-bit data RAM
//
// Instruction format:
//   [7:4] opcode, [3:0] immediate/address
//
// Opcodes:
//   0x0 NOP        no operation
//   0x1 LDI imm    acc = {4'b0000, imm}
//   0x2 ADD addr   acc = acc + ram[addr]
//   0x3 SUB addr   acc = acc - ram[addr]
//   0x4 AND addr   acc = acc & ram[addr]
//   0x5 OR  addr   acc = acc | ram[addr]
//   0x6 XOR addr   acc = acc ^ ram[addr]
//   0x7 LD  addr   acc = ram[addr]
//   0x8 ST  addr   ram[addr] = acc
//   0x9 JMP addr   pc = addr
//   0xA JZ  addr   if acc == 0, pc = addr
//   0xB JN  addr   if acc[7] == 1, pc = addr
//   0xC INP        acc = ui_in
//   0xD INIO       acc = uio_in
//   0xE OUT        out_reg = acc
//   0xF OUTIO      io_reg = acc, drive uio pins for one cycle

`timescale 1ns/1ps
`default_nettype none

module tt_um_baby_cpu (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    localparam OP_NOP   = 4'h0;
    localparam OP_LDI   = 4'h1;
    localparam OP_ADD   = 4'h2;
    localparam OP_SUB   = 4'h3;
    localparam OP_AND   = 4'h4;
    localparam OP_OR    = 4'h5;
    localparam OP_XOR   = 4'h6;
    localparam OP_LD    = 4'h7;
    localparam OP_ST    = 4'h8;
    localparam OP_JMP   = 4'h9;
    localparam OP_JZ    = 4'hA;
    localparam OP_JN    = 4'hB;
    localparam OP_INP   = 4'hC;
    localparam OP_INIO  = 4'hD;
    localparam OP_OUT   = 4'hE;
    localparam OP_OUTIO = 4'hF;

    reg [3:0] pc;
    reg [7:0] acc;
    reg [7:0] out_reg;
    reg [7:0] io_reg;
    reg       io_drive;

    reg [7:0] ram [0:15];

    wire [7:0] instr;
    wire [3:0] opcode = instr[7:4];
    wire [3:0] operand = instr[3:0];
    wire [3:0] pc_plus_one = pc + 4'd1;

    assign uo_out = out_reg;
    assign uio_out = io_reg;
    assign uio_oe = {8{io_drive}};

    // Replace this ROM contents with your own 16-instruction program.
    // Default demo:
    //   repeatedly read ui_in, mirror it to uo_out, pulse it onto uio_out.
    function [7:0] program_rom;
        input [3:0] addr;
        begin
            case (addr)
                4'h0: program_rom = {OP_INP,   4'h0}; // acc = ui_in
                4'h1: program_rom = {OP_OUT,   4'h0}; // uo_out = acc
                4'h2: program_rom = {OP_OUTIO, 4'h0}; // pulse uio_out = acc
                4'h3: program_rom = {OP_JMP,   4'h0}; // loop
                default: program_rom = {OP_NOP, 4'h0};
            endcase
        end
    endfunction

    assign instr = program_rom(pc);

    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pc <= 4'd0;
            acc <= 8'd0;
            out_reg <= 8'd0;
            io_reg <= 8'd0;
            io_drive <= 1'b0;

            for (i = 0; i < 16; i = i + 1) begin
                ram[i] <= 8'd0;
            end
        end else if (ena) begin
            pc <= pc_plus_one;
            io_drive <= 1'b0;

            case (opcode)
                OP_NOP: begin
                    acc <= acc;
                end

                OP_LDI: begin
                    acc <= {4'd0, operand};
                end

                OP_ADD: begin
                    acc <= acc + ram[operand];
                end

                OP_SUB: begin
                    acc <= acc - ram[operand];
                end

                OP_AND: begin
                    acc <= acc & ram[operand];
                end

                OP_OR: begin
                    acc <= acc | ram[operand];
                end

                OP_XOR: begin
                    acc <= acc ^ ram[operand];
                end

                OP_LD: begin
                    acc <= ram[operand];
                end

                OP_ST: begin
                    ram[operand] <= acc;
                end

                OP_JMP: begin
                    pc <= operand;
                end

                OP_JZ: begin
                    if (acc == 8'd0) begin
                        pc <= operand;
                    end
                end

                OP_JN: begin
                    if (acc[7]) begin
                        pc <= operand;
                    end
                end

                OP_INP: begin
                    acc <= ui_in;
                end

                OP_INIO: begin
                    acc <= uio_in;
                end

                OP_OUT: begin
                    out_reg <= acc;
                end

                OP_OUTIO: begin
                    io_reg <= acc;
                    io_drive <= 1'b1;
                end

                default: begin
                    acc <= acc;
                end
            endcase
        end
    end

endmodule

`default_nettype wire
