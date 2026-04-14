import re

def test_regex():
    tokens = [
        "t1-listening-p1-s1-q1",
        "t2-READING-p2-s3-q5",
        "t3-Writing-p1-s1-q1",
        "t4-SPEAKING-p8-s1-q1",
        "123", # numeric case
    ]

    pattern = r"-([a-zA-Z]+)-p"

    for token in tokens:
        match = re.search(pattern, token, re.IGNORECASE)
        if match:
            area = match.group(1).lower()
            print(f"Token: {token} -> Area: {area}")
        else:
            print(f"Token: {token} -> No match")

if __name__ == "__main__":
    test_regex()
