// threshold_logic.v
module threshold_logic (
    input wire clk,
    input wire rst_n,
    input wire signal_buy_slow,
    input wire signal_sell_slow,
    input wire [63:0] fast_price,
    input wire [63:0] slow_price,
    input wire [31:0] cfg_threshold,
    output reg trigger_trade,
    output reg trade_side
);
    reg [63:0] diff;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            trigger_trade <= 0;
            trade_side <= 0;
            diff <= 0;
        end else begin
            trigger_trade <= 0;
            if (signal_buy_slow) begin
                diff <= (fast_price > slow_price) ? (fast_price - slow_price) : 0;
                if (diff > cfg_threshold) begin
                    trigger_trade <= 1'b1;
                    trade_side <= 1'b1;
                end
            end else if (signal_sell_slow) begin
                diff <= (slow_price > fast_price) ? (slow_price - fast_price) : 0;
                if (diff > cfg_threshold) begin
                    trigger_trade <= 1'b1;
                    trade_side <= 1'b0;
                end
            end
        end
    end
endmodule
