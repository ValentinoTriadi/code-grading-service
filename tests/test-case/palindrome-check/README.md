# Palindrome Check — Test Cases

**Language:** Java
**Difficulty:** Easy

## Problem

Write a method `isPalindrome(String s)` that returns `true` if the input string reads the same forwards and backwards, **ignoring case and non-alphanumeric characters**, and `false` otherwise.

Examples:
- `"A man, a plan, a canal: Panama"` → `true`
- `"race a car"` → `false`
- `""` → `true`

Each group represents a different implementation approach. Within a group, files numbered 1–3 follow the convention:

- **1** = poor (bad style, shadowing, ignores requirements)
- **2** = acceptable (correct, some style issues)
- **3** = good (clean, idiomatic)

---

## Group A — Two pointers

Manually walks two indices from both ends, skipping non-alphanumerics.

| File | Quality | Notes |
|------|---------|-------|
| `PalindromeA1.java` | Poor | Doesn't ignore case — fails on the canonical test |
| `PalindromeA2.java` | Acceptable | Correct, but uses `Character.toString` instead of `==` |
| `PalindromeA3.java` | Good | Clean two-pointer loop, handles all requirements |

## Group B — Reverse and compare

Cleans the string, reverses it, compares with `equals`.

| File | Quality | Notes |
|------|---------|-------|
| `PalindromeB1.java` | Poor | Uses `==` instead of `.equals` — wrong on long strings |
| `PalindromeB2.java` | Acceptable | Correct logic, manual reverse loop |
| `PalindromeB3.java` | Good | Uses `StringBuilder.reverse()` cleanly |

## Group C — StringBuilder

Uses `StringBuilder` to build a normalized form and reverse.

| File | Quality | Notes |
|------|---------|-------|
| `PalindromeC1.java` | Poor | Doesn't strip non-alphanumeric — fails on punctuation |
| `PalindromeC2.java` | Acceptable | Correct, but builds normalized string in two passes |
| `PalindromeC3.java` | Good | Single-pass filter, idiomatic chain |

## Group D — Recursion

Strips non-alphanumerics, then recursively compares ends.

| File | Quality | Notes |
|------|---------|-------|
| `PalindromeD1.java` | Poor | Recurses on substring — quadratic memory |
| `PalindromeD2.java` | Acceptable | Helper method with indices, correct |
| `PalindromeD3.java` | Good | Tail-style recursion, clean base case |

## Group E — Stream API

Uses Java 8 streams for a one-shot expression.

| File | Quality | Notes |
|------|---------|-------|
| `PalindromeE1.java` | Acceptable | Correct stream pipeline, somewhat opaque |
| `PalindromeE2.java` | Good | Concise IntStream comparison |

## Group F — Wrong logic

Compiles and runs, but gives wrong answers.

| File | Bug |
|------|-----|
| `PalindromeF1.java` | Only checks the first half against itself — always returns `true` |
| `PalindromeF2.java` | Compares whole string to itself reversed *without* normalizing — fails on `"Aa"` |
| `PalindromeF3.java` | Off-by-one in two-pointer — fails on odd-length strings |

## Group G — Compile errors

Won't compile.

| File | Bug |
|------|-----|
| `PalindromeG1.java` | Missing semicolon after return statement |
| `PalindromeG2.java` | Method declared `void` but tries to return `boolean` |
| `PalindromeG3.java` | Mismatched braces — extra `}` at end |
