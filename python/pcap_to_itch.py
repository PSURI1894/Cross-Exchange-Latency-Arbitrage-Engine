import struct
class ITCHBinaryEncoder:
    def encode_add_order(self, stock_id, qty, price, side):
        return struct.pack("=cIIQc", b'A', qty, stock_id, price, side.encode())
