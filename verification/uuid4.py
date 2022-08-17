#!/usr/bin/env python3

import uuid

def get_test_id():
    # uuid4() creates a random UUID
    # https://datatracker.ietf.org/doc/html/rfc4122.html

    return uuid.uuid4()

if __name__ == "__main__":
    ix = get_test_id()
    print(ix)
