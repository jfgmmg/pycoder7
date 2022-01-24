"""
This module implements a RLE compressor and decompressor. Two RLE
methods are implemented here:

    A - Each ocurrence of a new byte is replaced by a counter with the 
        number of consecutive occurrences and the byte itself.
        Examples: 
            1) b'LLLLARRB' -> b'\x04L\x01A\x02R\x01B'.
            2) b'ABC'      -> b'\x01A\x01B\x01C'

    B - Only series with repetition (two or more consecutive occurrences
        of the same byte) are replaced by a double ocurrence of the
        byte and a counter. Bytes that don't repeat are passed directly
        to the output stream. 
        Examples: 
            1) b'LLLLARRB' -> b'LL\x04ARR\x02B'.
            2) b'ABC'      -> b'ABC'
        A double occurrence of the encoded byte "tells" the decoder that
        the next byte is a counter, whereas a byte that doesn't repeat 
        is copied directly to the output stream.

Please consult Wikipedia to obtain more information about RLE in general
and these specific methods.

This module is also a script and GUI application. Please see function 
'_main' for instructions on how to use 'pycoder.py' as script or GUI 
app.
"""

import io
import os
import sys
from textwrap import dedent
from typing import BinaryIO

from docopt import docopt

__all__ = [
    'encode_rle',
    'decode_rle',
]

METHOD_A = b'\x21'  # 33 or b'!'
METHOD_B = b'\x8a'  # 138

def encode_rle(
        in_file_path: str, 
        out_file_path: str,
        method: bytes,
        overwrite: bool=False,
):
    assert method in [METHOD_A, METHOD_B]
    encode_fn = {
        METHOD_A: _encode_mA,
        METHOD_B: _encode_mB,
    }[method]

    with open(in_file_path, 'rb') as in_:
        with open(out_file_path, 'wb' if overwrite else 'xb') as out:
            out.write(method)
            encode_fn(in_, out)
        #:
    #:
#:

def _encode_mA(in_: BinaryIO, out: BinaryIO):
    """
    Para cada byte em in_:
      1. Se próx byte for igual ao byte actual:
          1.1 incrementar contador
      2. Senão (ie, se próx byte terminar série de bytes consecutivos):
          2.1 gravar na stream out o contador e o byte actual
          2.2 colocar contador a 1
          2.3 byte actual = próx byte
    """
    def write_fn(curr_byte: bytes, count: int):
        out.write(_int_to_byte(count))
        out.write(curr_byte)
    #:
    _do_encode(in_, write_fn)
#:

def _encode_mB(in_: BinaryIO, out: BinaryIO):
    def write_fn(curr_byte: bytes, count: int):
        out.write(curr_byte)
        if count > 1:
            out.write(curr_byte)
            out.write(_int_to_byte(count))
        #:
    #:
    _do_encode(in_, write_fn)
#:

def _do_encode(in_: BinaryIO, write_fn):
    curr_byte = in_.read(1)
    count = 1
    for next_byte in iter(lambda: in_.read(1), b''):
        if next_byte == curr_byte:
            count += 1
            if count == 255:
                write_fn(curr_byte, count)
                count = 0
            #:
        #:
        else:
            if count != 0:
                write_fn(curr_byte, count)
            count = 1
            curr_byte = next_byte
        #:
    #:
    if curr_byte:
        write_fn(curr_byte, count)
    #:
#:

def decode_rle(
        in_file_path: str, 
        out_file_path: str,
        overwrite: bool=False,
):
    with open(in_file_path, 'rb') as in_:
        method = in_.read(1)
        decode_fn = {
            METHOD_A: _decode_mA,
            METHOD_B: _decode_mB,
        }.get(method)
        if not decode_fn:
            raise ValueError(f'Unknown value for method {method}.')
        with open(out_file_path, 'wb' if overwrite else 'xb') as out:
            decode_fn(in_, out)
        #
    #
#:

def _decode_mA(in_: BinaryIO, out: BinaryIO):
    for pair in iter(lambda: in_.read(2), b''):
        assert len(pair) == 2
        count = pair[0]
        next_byte = pair[1:]
        out.write(count * next_byte)
    #:
#:

def _decode_mB(in_: BinaryIO, out: BinaryIO):
    """
    1. Em ciclo, ler dois bytes de cada vez
        1.1 if not byte1:
              1.1.1 Fim ficheiro logo fim do ciclo
        1.2. Se byte1 == byte2 então
          1.2.1 Ler 3o byte com a contagem (count)
          1.2.2 Colocar na saída byte1 count vezes
        1.3. Senão:        
            1.3.1 Coloca na saída byte1 (uma vez)
            1.3.2 Se houver byte2, anular a leitura deste byte com 
                  in_.seek(-1, io.SEEK_CUR)
    """
    while True:
        # Note that 2 x read(1) != read(2). read(2) reads _at most_
        # 2 bytes and returns a byte string with 3 possible lengths,
        # so we can't do something like b1, b2 = in_.read(2)
        # may fail if read(2) returns 1 or 3
        b1, b2 = in_.read(1), in_.read(1)  
        if not b1:
            break
        if b1 == b2:
            b3 = in_.read(1)
            # if there are duplicates, then a third byte with the 
            # count must be present
            assert b3
            count = b3[0]
        #:
        else:
            count = 1
            if b2:
                in_.seek(-1, io.SEEK_CUR)
        #:
        out.write(count * b1)
    #:
#:

def _int_to_byte(i: int) -> bytes:
    return bytes((i,)) 
#:

def _main():
    """
    Interactive script.
    """
    # If it wasn't for dependency determination done by 3rd party
    # tools (code analysers, build tools, ), the following 
    # modules should be imported right here, since they are irrelevant
    # for the main purpose of this module (RLE encoding) and only useful
    # when the module is used as a shell/GUI tool
    #   import os
    #   import sys
    #   from textwrap import dedent
    #   from docopt import docopt

    doc = """
    Run-Lenth enconding and decoding.

    Usage:
        pycoder (-c [-t TYPE] | -d | -x) [-p PASSWD] FILE

    Options:
        -c, --encode, --compress      Compress FILE with RLE compression
        -d, --decode, --decompress    Decompress FILE compressed with RLE
        -t TYPE, --type=TYPE          Encoding method used [default: 2]
        -x, --dump                    Dumps a file as a Python's binary string
        -h, --help                    This help 
        -p PASSWORD, --password=PASSWORD  An optional password to encrypt the file
    """
    args = docopt(dedent(doc))

    def overwrite_if_needed_or_exit(dest_file_path: str):
        if os.path.exists(dest_file_path):
            answer = input(f"File {dest_file_path} exists. Overwrite (y or n)? ")
            if answer.strip().lower() != 'y':
                print("File will not be overwritten")
                sys.exit()
    #:
    def exists_or_exit(file_path, error_code=3):
        if not os.path.exists(file_path):
            print(f"File {file_path} doesn't exist", file=sys.stderr)
            sys.exit(error_code)
    #:
    pass
#:

if __name__ == '__main__':
    _main()
#:
