"""
Generate a markdown file with random contents for testing purposes
"""

import random
import string

POOL = string.ascii_letters + string.digits + "      "


def random_line(length, variance):
    final_length = length + random.randint(-variance, variance)
    return "".join(random.choices(POOL, k=final_length)).strip()


file = "../non_vcs/huge.md"
target_mb = 1_000
with open(file, "w") as fp:
    current_bytes = 0
    while current_bytes <= (target_mb * 1_000_000):
        heading = "#" * random.randint(1, 6) + " " + random_line(30, 15)
        current_bytes += fp.write(heading + "\n")
        for i in range(0, random.randint(10, 100)):
            current_bytes += fp.write(random_line(100, 20) + "\n")

    print(f"Wrote {current_bytes/1_000_000} MB of random markdown to {file}")
