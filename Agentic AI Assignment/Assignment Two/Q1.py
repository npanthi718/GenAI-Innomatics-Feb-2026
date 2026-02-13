"""
Problem 1: Unique Words in a Sentence
"""

def main():
    # 1. Input - Taking the sentence from the user
    sentence = input("Enter sentence: ")

    # 2. Preprocessing - Convert to lowercase and split into words
    # This ensures "Python" and "python" are treated as the same word
    words = sentence.lower().split()

    # 3. Logic - Convert list to set to remove duplicates
    unique_words = set(words)

    # 4. Output - Display the unique words and the count
    print(f"\nUnique words: {unique_words}")
    print(f"The count of unique words: {len(unique_words)}")

if __name__ == "__main__":
    main()