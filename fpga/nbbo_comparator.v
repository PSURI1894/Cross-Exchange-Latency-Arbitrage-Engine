// nbbo_comparator.v
module nbbo_comparator (
    input wire clk, input wire rst_n, input wire [31:0] fast_stock_id, input wire [63:0] fast_price, input wire fast_side, input wire fast_valid,
    input wire [31:0] cfg_stock_id, input wire [63:0] slow_venue_bid, input wire [63:0] slow_venue_ask,
    output reg signal_buy_slow, output reg signal_sell_slow
);
    reg id_match; reg bid_exceeded; reg ask_undercut;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            id_match <= 0; bid_exceeded <= 0; ask_undercut <= 0;
            signal_buy_slow <= 0; signal_sell_slow <= 0;
        end else begin
            id_match <= fast_valid && (fast_stock_id == cfg_stock_id);
            bid_exceeded <= fast_price < slow_venue_bid;
            ask_undercut <= fast_price > slow_venue_ask;
            signal_buy_slow <= id_match && fast_side && ask_undercut;
            signal_sell_slow <= id_match && !fast_side && bid_exceeded;
        end
    end
endmodule
