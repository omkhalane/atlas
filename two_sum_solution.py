def two_sum(nums, target):
    num_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    return []

# Test cases
test_cases = [
    {"nums": [2, 7, 11, 15], "target": 9, "expected": [0, 1]},
    {"nums": [3, 2, 4], "target": 6, "expected": [1, 2]},
    {"nums": [3, 3], "target": 6, "expected": [0, 1]}
]

for tc in test_cases:
    result = two_sum(tc["nums"], tc["target"])
    print(f"Input: {tc['nums']}, Target: {tc['target']} | Result: {result} | Expected: {tc['expected']} | {'PASS' if result == tc['expected'] else 'FAIL'}")