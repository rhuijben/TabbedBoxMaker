#!/usr/bin/env python3

print("This is a test file")

def test_main():
    print("Test main called")

if __name__ == '__main__':
    print("About to call test main...")
    test_main()
    print("Test main completed.")
else:
    print("Module imported, not executed directly.")
