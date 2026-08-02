from solution_4sum import Solution

def test_solution():
    sol = Solution()
    
    # Test case 1
    nums1 = [1, 0, -1, 0, -2, 2]
    target1 = 0
    expected1 = [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
    result1 = sol.fourSum(nums1, target1)
    # Sort both for comparison
    result1.sort()
    expected1.sort()
    assert result1 == expected1, f'Test case 1 failed: expected {expected1}, got {result1}'
    
    # Test case 2
    nums2 = [2, 2, 2, 2, 2]
    target2 = 8
    expected2 = [[2, 2, 2, 2]]
    result2 = sol.fourSum(nums2, target2)
    result2.sort()
    expected2.sort()
    assert result2 == expected2, f'Test case 2 failed: expected {expected2}, got {result2}'

    # Test case 3
    nums3 = [0, 0, 0, 0]
    target3 = 0
    expected3 = [[0, 0, 0, 0]]
    result3 = sol.fourSum(nums3, target3)
    result3.sort()
    expected3.sort()
    assert result3 == expected3, f'Test case 3 failed: expected {expected3}, got {result3}'

    print("All test cases passed!")

if __name__ == "__main__":
    test_solution()