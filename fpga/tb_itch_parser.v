// tb_itch_parser.v
`timescale 1ns/1ps
module tb_itch_parser;
    reg clk; reg rst_n; reg [63:0] rx_data; reg rx_data_valid; reg rx_sof; reg rx_eof;
    wire [31:0] parsed_stock_id; wire [63:0] parsed_price; wire [31:0] parsed_qty; wire parsed_valid; wire parsed_side;
    itch_parser uut (.clk(clk), .rst_n(rst_n), .rx_data(rx_data), .rx_data_valid(rx_data_valid), .rx_sof(rx_sof), .rx_eof(rx_eof),
        .parsed_stock_id(parsed_stock_id), .parsed_price(parsed_price), .parsed_qty(parsed_qty), .parsed_valid(parsed_valid), .parsed_side(parsed_side));
    always #5 clk = ~clk;
    initial begin
        clk = 0; rst_n = 0; rx_data = 0; rx_data_valid = 0; rx_sof = 0; rx_eof = 0;
        #20; rst_n = 1; #20;
        rx_data = 64'h0000000000000041; rx_sof = 1; rx_data_valid = 1; #10; rx_sof = 0;
        rx_data = 64'h000000640000002A; #10;
        rx_data = 64'h000000000016E360; #10;
        rx_data = 64'h0000000000000042; rx_eof = 1; #10; rx_eof = 0; rx_data_valid = 0;
        #50; $finish;
    end
endmodule
