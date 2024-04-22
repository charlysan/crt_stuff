# Copyright (c) 2024 charlysan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys 
import signal
import argparse

from vctlib.vcti2c import VCTi2c, bytearray_to_hex

def signal_handler(sig, frame, vct: VCTi2c):
    print('\nProcess terminated by user')
    vct.__del__()

    sys.exit(0)

def main():
    # signal.signal(signal.SIGINT, signal_handler)
    vct = None
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, vct))


    args = parse_arguments()

    if args.rbo:
        arg1, arg2 = args.rbo
        addr = parse_byte(arg1)
        offset = parse_byte(arg2)

        vct = VCTi2c()
        vct.start_transaction()
        data = vct.read_byte_from_RAM_page(addr, offset)
        vct.end_transaction()

        print(bytearray_to_hex(data))
    elif args.read_ram_block_page:
        arg1, arg2, arg3 = args.read_ram_block_page
        addr = parse_byte(arg1)
        offset_start = parse_byte(arg2)
        offset_end = parse_byte(arg3)

        vct = VCTi2c()
        vct.start_transaction()
        data = vct.read_block_from_RAM_page(addr, offset_start, offset_end)
        vct.end_transaction()
        for data_byte in data:
            sys.stdout.buffer.write(data_byte)
        
    elif args.read_ram_block:
        arg1, arg2 = args.read_ram_block
        addr_start = parse_byte(arg1)
        addr_end = parse_byte(arg2)
        vct = VCTi2c()
        vct.start_transaction()
        data = vct.read_block_from_RAM(addr_start, addr_end) 
        vct.end_transaction()
        for page in data:
            for data_byte in page:
                sys.stdout.buffer.write(data_byte)
    elif args.wbo:
        arg1, arg2, arg3 = args.wbo
        addr = parse_byte(arg1)
        offset = parse_byte(arg2)
        data_byte = parse_byte(arg3)

        vct = VCTi2c()
        vct.start_transaction()
        data = vct.write_byte_into_RAM_page(addr, offset, data_byte)
        vct.end_transaction() 

        print(bytearray_to_hex(data))

    elif args.wddp:
        arg1, arg2, arg3 = args.wddp
        sub_addr = parse_byte(arg1)
        hbyte = parse_byte(arg2)
        lbyte = parse_byte(arg3)

        vct = VCTi2c()
        vct.start_transaction()
        data = vct.write_DDP_reg(sub_addr, hbyte, lbyte)
        vct.end_transaction() 

        print(bytearray_to_hex(data))


    if vct:
        vct.__del__()


    
def parse_arguments():

        example_text = r'''Examples:

        vct_cli -rbo 0x50 0x10'''

        parser = argparse.ArgumentParser(
            description="VCT cli tool can be used to talk to VCT49xl ICs",
            epilog=example_text,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument('--version',
                            action="version",
                            version="v0.1b (Apr 18th, 2024)")

        parser.add_argument('--rbo', nargs=2, metavar=('address', 'offset'), action=MultiParamsAction, help="Read byte from address offset", default=None)
        parser.add_argument('--wbo', nargs=3, metavar=('address', 'offset', 'data'), action=MultiParamsAction, help="Write byte to address offset", default=None)
        parser.add_argument('--scl-down', nargs=1, metavar=('delay'), action=MultiParamsAction, help="Write byte to address offset", default=None)
        parser.add_argument('--wddp', nargs=3, metavar=('subaddress', 'hbyte', 'lbyte'), action=MultiParamsAction, help="Write word to DDP register", default=None)
        parser.add_argument('--read-ram-block-page', nargs=3, metavar=('address', 'offset_start', 'offset_end'), action=MultiParamsAction, help="Read RAM page block", default=None)
        parser.add_argument('--read-ram-block', nargs=2, metavar=('address_start', 'address_end'), action=MultiParamsAction, help="Read block from RAM", default=None)


        args = parser.parse_args(
            args=None if sys.argv[1:] else ['--help'])

        return args

def parse_byte(data):
    try:
        if data.startswith("0x"):
            return int(data, 16)
        else:
            return int(data, 10)
    except ValueError:
        print("Invalid input (%s). Please use integer or hex string (e.g. 0x4d)" % data)
        exit(-1)


class MultiParamsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


if __name__ == "__main__":
    main()