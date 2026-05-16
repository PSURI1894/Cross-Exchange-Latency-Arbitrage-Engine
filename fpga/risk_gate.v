// risk_gate.v
module risk_gate (
    input wire clk,
    input wire rst_n,
    input wire trigger_trade_in,
    input wire trade_side_in,
    input wire [31:0] stock_id_in,
    input wire [31:0] qty_in,
    input wire [31:0] cfg_max_pos,
    input wire [31:0] cfg_max_loss,
    input wire hardware_kill_switch,
    output reg trigger_trade_out,
    output reg trade_side_out,
    output reg risk_breached
);
    reg [31:0] current_position;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_position <= 0;
            trigger_trade_out <= 0;
            trade_side_out <= 0;
            risk_breached <= 0;
        end else begin
            trigger_trade_out <= 0;
            trade_side_out <= 0;
            if (hardware_kill_switch) begin
                risk_breached <= 1'b1;
            end else if (trigger_trade_in) begin
                if (current_position + qty_in > cfg_max_pos) begin
                    risk_breached <= 1'b1;
                end else begin
                    trigger_trade_out <= 1'b1;
                    trade_side_out <= trade_side_in;
                    current_position <= trade_side_in ? (current_position + qty_in) : (current_position - qty_in);
                end
            end
        end
    end
endmodule
