// top_latency_arb.v
module top_latency_arb (
    input wire clk,
    input wire rst_n,
    input wire [63:0] rx_data,
    input wire rx_data_valid,
    input wire rx_sof,
    input wire rx_eof,
    output wire [63:0] tx_data,
    output wire tx_data_valid,
    output wire tx_sof,
    output wire tx_eof,
    input wire [31:0] pcie_cfg_stock_id,
    input wire [63:0] pcie_slow_bid,
    input wire [63:0] pcie_slow_ask,
    input wire [31:0] pcie_cfg_threshold,
    input wire [31:0] pcie_cfg_max_pos,
    input wire [31:0] pcie_cfg_max_loss,
    input wire pcie_hardware_kill_switch,
    output wire risk_breached
);
    wire [31:0] parser_stock_id;
    wire [63:0] parser_price;
    wire [31:0] parser_qty;
    wire parser_valid;
    wire parser_side;
    wire comp_buy_slow;
    wire comp_sell_slow;
    wire thresh_trigger;
    wire thresh_side;
    wire risk_trigger;
    wire risk_side;

    itch_parser parser_inst (
        .clk(clk), .rst_n(rst_n), .rx_data(rx_data), .rx_data_valid(rx_data_valid), .rx_sof(rx_sof), .rx_eof(rx_eof),
        .parsed_stock_id(parser_stock_id), .parsed_price(parser_price), .parsed_qty(parser_qty), .parsed_valid(parser_valid), .parsed_side(parser_side)
    );
    nbbo_comparator comp_inst (
        .clk(clk), .rst_n(rst_n), .fast_stock_id(parser_stock_id), .fast_price(parser_price), .fast_side(parser_side), .fast_valid(parser_valid),
        .cfg_stock_id(pcie_cfg_stock_id), .slow_venue_bid(pcie_slow_bid), .slow_venue_ask(pcie_slow_ask),
        .signal_buy_slow(comp_buy_slow), .signal_sell_slow(comp_sell_slow)
    );
    threshold_logic thresh_inst (
        .clk(clk), .rst_n(rst_n), .signal_buy_slow(comp_buy_slow), .signal_sell_slow(comp_sell_slow), .fast_price(parser_price), .slow_price(pcie_slow_ask),
        .cfg_threshold(pcie_cfg_threshold), .trigger_trade(thresh_trigger), .trade_side(thresh_side)
    );
    risk_gate risk_inst (
        .clk(clk), .rst_n(rst_n), .trigger_trade_in(thresh_trigger), .trade_side_in(thresh_side), .stock_id_in(pcie_cfg_stock_id), .qty_in(parser_qty),
        .cfg_max_pos(pcie_cfg_max_pos), .cfg_max_loss(pcie_cfg_max_loss), .hardware_kill_switch(pcie_hardware_kill_switch),
        .trigger_trade_out(risk_trigger), .trade_side_out(risk_side), .risk_breached(risk_breached)
    );
    ouch_constructor ouch_inst (
        .clk(clk), .rst_n(rst_n), .trigger_trade(risk_trigger), .trade_side(risk_side), .target_stock_id(pcie_cfg_stock_id), .trade_price(parser_price), .trade_qty(parser_qty),
        .tx_data(tx_data), .tx_data_valid(tx_data_valid), .tx_sof(tx_sof), .tx_eof(tx_eof)
    );
endmodule
