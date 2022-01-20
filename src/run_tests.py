# pylint: disable=exec-used
# pylint: disable=protected-access
# pylint: disable=deprecated-method

TEST_ALL = True

from pydoc import plain
import pycoder
import io

################################################################################
#
#           UNIT TEST LIBRARY
#
#           Developed using class free and functional style OOP.
#
################################################################################

# TestSuit = type('TestSuit', (), {})

class TestSuit:
    def __init__(self):
        self.failed_count = 0
        self.succ_count = 0
    #:
    def assert_(self, test_code: str):
        try:
            exec(f'assert {test_code}', None)
        except AssertionError:
            print(f'{test_code:50} --> FAILED!')
            self.failed_count += 1
        else:
            print(f'{test_code:50} OK')
            self.succ_count += 1
    #:
    def setup_and_assert(self, setup_code, test_code: str):
        print(setup_code)
        exec(setup_code)
        self.assert_("    " + test_code)
    #:
    def assert_exception(self, test_code: str, exception: Exception):
        # pylint: disable=broad-except
        try:
            exec(f'assert {test_code}', None)
        except exception:
            msg = f'{test_code} raises {exception.__name__}'
            print(f'{msg:50} OK')
            self.succ_count += 1
        except Exception as ex:
            msg = f'{test_code} raises {type(ex).__name__} instead of {exception}'
            print(f'{msg:50} --> FAILED')
            self.failed_count += 1
        else:
            msg = f'{test_code} doesn\'t raise any exception'
            print(f'{msg:50} --> FAILED')
            self.failed_count += 1
    #:
    def summary(self):
        if self.failed_count == 0:
            print(f"All {self.succ_count} tests passed SUCCESSFULLY!")
        else:
            print(f"{self.failed_count + self.succ_count} TESTS:")
            print(f"        {self.failed_count:>4} FAILED")
            print(f"        {self.succ_count:>4} passed")
        #:
    #:
#:

tester = TestSuit()

if TEST_ALL:
    test1 = b'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW'
    test1_rle_b = b'WW\x0cBWW\x0cBB\x03WW\x18BWW\x0e'
    test2 = b'W' * 300 + b'A' * 255 + b'B' * 19
    test2_rle_b = b'WW\xffWW-AA\xffBB\x13'

    def encode_in_mem(encode, test_data: bytes):
        in_ = io.BytesIO(test_data)
        out = io.BytesIO()
        encode(in_, out)
        return out.getvalue()
    #:

    def decode_in_mem(decode, rle_data: bytes):
        return encode_in_mem(decode, rle_data)
    #:

    print('\n____________ ENCODING METHOD_B\n')
    rle_data1 = encode_in_mem(pycoder._encode_mB, test1)
    tester.assert_("rle_data1 == test1_rle_b")
    rle_data2 = encode_in_mem(pycoder._encode_mB, test2)
    tester.assert_("rle_data2 == test2_rle_b")

    print('\n____________ DECODING METHOD_B\n')
    plain_data = decode_in_mem(pycoder._decode_mB, test1_rle_b)
    tester.assert_("plain_data == test1")
    plain_data = decode_in_mem(pycoder._decode_mB, test2_rle_b)
    tester.assert_("plain_data == test2")

    print()
    tester.summary()

