// itch_parser.v
module itch_parser (
    input wire clk, input wire rst_n, input wire [63:0] rx_data, input wire rx_data_valid, input wire rx_sof, input wire rx_eof,
    output reg [31:0] parsed_stock_id, output reg [63:0] parsed_price,
    output reg [31:0] parsed_qty, output reg parsed_valid, output reg parsed_side
);
    reg [1:0] state; reg [63:0] buffer [0:3]; reg [1:0] cycle_cnt;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 0; cycle_cnt <= 0; parsed_valid <= 0;
        end else begin
            parsed_valid <= 0;
            case (state)
                0: begin if (rx_sof && rx_data_valid) begin buffer[0] <= rx_data; cycle_cnt <= 1; state <= 1; end end
                1: begin
                    if (rx_data_valid) begin
                        buffer[cycle_cnt] <= rx_data; cycle_cnt <= cycle_cnt + 1;
                        if (cycle_cnt == 2) state <= 2;
                    end
                end
                2: begin
                    if (buffer[0][7:0] == 8'h41) begin
                        parsed_stock_id <= buffer[1][31:0]; parsed_qty <= buffer[1][63:32];
                        parsed_price <= buffer[2]; parsed_side <= (rx_data[7:0] == 8'h42) ? 1'b1 : 1'b0;
                        parsed_valid <= 1'b1;
                    end
                    state <= 0; cycle_cnt <= 0;
                end
            endcase
        end
    end
endmodule
