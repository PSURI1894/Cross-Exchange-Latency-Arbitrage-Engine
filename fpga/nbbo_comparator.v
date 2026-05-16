// nbbo_comparator.v
module nbbo_comparator (
    input wire clk,
    input wire rst_n,
    input wire [31:0] fast_stock_id,
    input wire [63:0] fast_price,
    input wire fast_side,
    input wire fast_valid,
    input wire [31:0] cfg_stock_id,
    input wire [63:0] slow_venue_bid,
    input wire [63:0] slow_venue_ask,
    output reg signal_buy_slow,
    output reg signal_sell_slow
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            signal_buy_slow <= 0;
            signal_sell_slow <= 0;
        end else begin
            signal_buy_slow <= 0;
            signal_sell_slow <= 0;
            if (fast_valid && (fast_stock_id == cfg_stock_id)) begin
                if (fast_side == 1'b1 && fast_price > slow_venue_ask) begin
                    signal_buy_slow <= 1'b1;
                end
                if (fast_side == 1'b0 && fast_price < slow_venue_bid) begin
                    signal_sell_slow <= 1'b1;
                end
            end
        end
    end
endmodule
