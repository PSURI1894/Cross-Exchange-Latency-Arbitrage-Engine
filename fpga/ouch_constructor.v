// ouch_constructor.v
module ouch_constructor (
    input wire clk, input wire rst_n, input wire trigger_trade, input wire trade_side,
    input wire [31:0] target_stock_id, input wire [63:0] trade_price, input wire [31:0] trade_qty,
    output reg [63:0] tx_data, output reg tx_data_valid, output reg tx_sof, output reg tx_eof
);
    reg [2:0] state; reg [31:0] order_token_counter;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 0; tx_data <= 0; tx_data_valid <= 0; tx_sof <= 0; tx_eof <= 0; order_token_counter <= 1;
        end else begin
            tx_data_valid <= 0; tx_sof <= 0; tx_eof <= 0;
            case (state)
                0: begin if (trigger_trade) state <= 1; end
                1: begin tx_data <= {order_token_counter, 24'h0, 8'h4F}; tx_data_valid <= 1; tx_sof <= 1; state <= 2; end
                2: begin tx_data <= {trade_qty, 24'h0, (trade_side ? 8'h42 : 8'h53)}; tx_data_valid <= 1; state <= 3; end
                3: begin tx_data <= trade_price; tx_data_valid <= 1; state <= 4; end
                4: begin
                    tx_data <= {32'h0, target_stock_id};
                    tx_data_valid <= 1; tx_eof <= 1;
                    order_token_counter <= (order_token_counter == 32'hFFFFFFFF) ? 1 : (order_token_counter + 1);
                    state <= 0;
                end
            endcase
        end
    end
endmodule
