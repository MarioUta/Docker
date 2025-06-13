def jaccard_similarity(str1, str2):
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union) if union else 0

print(jaccard_similarity("aba","abcd"))
print(jaccard_similarity("baa","abcd"))


