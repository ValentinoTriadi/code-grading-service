# P2 — Palindrome Check
_easy · java · 20 submissions_

## Description

Implement `boolean isPalindrome(String s)` that returns `true` if the input reads the same forwards and backwards, ignoring case and non-alphanumeric characters, and `false` otherwise. The empty string is a palindrome. Examples: `"A man, a plan, a canal: Panama"` → `true`; `"race a car"` → `false`; `""` → `true`.

## Rubric

- **Correctness (60)** — Returns `true` exactly when the input reads the same forward and backward after lower-casing and stripping non-alphanumeric characters. Handles the empty string, mixed-case inputs, and inputs containing punctuation. No off-by-one errors on odd-length strings, no silent always-true logic. Compiles without errors.
- **Code Quality (25)** — Idiomatic Java. Uses `.equals` rather than `==` for string comparison. The chosen approach (two pointers, reverse-and-compare, StringBuilder, Stream API, or recursion) is implemented cleanly with descriptive names.
- **Efficiency (15)** — Avoids quadratic substring recursion and stack-blowing implementations on long inputs. Does not allocate more strings than the chosen approach requires.

## Score sheet

| Submission | Correctness (60) | Code Quality (25) | Efficiency (15) | **Total** | Notes |
|---|---|---|---|---|---|
| PalindromeA1 |      |      |      |        |       |
| PalindromeA2 |      |      |      |        |       |
| PalindromeA3 |      |      |      |        |       |
| PalindromeB1 |      |      |      |        |       |
| PalindromeB2 |      |      |      |        |       |
| PalindromeB3 |      |      |      |        |       |
| PalindromeC1 |      |      |      |        |       |
| PalindromeC2 |      |      |      |        |       |
| PalindromeC3 |      |      |      |        |       |
| PalindromeD1 |      |      |      |        |       |
| PalindromeD2 |      |      |      |        |       |
| PalindromeD3 |      |      |      |        |       |
| PalindromeE1 |      |      |      |        |       |
| PalindromeE2 |      |      |      |        |       |
| PalindromeF1 |      |      |      |        |       |
| PalindromeF2 |      |      |      |        |       |
| PalindromeF3 |      |      |      |        |       |
| PalindromeG1 |      |      |      |        |       |
| PalindromeG2 |      |      |      |        |       |
| PalindromeG3 |      |      |      |        |       |

## Submissions

### 1. `PalindromeA1`

```java
public class PalindromeA1 {
    public boolean isPalindrome(String s) {
        int i = 0;
        int j = s.length() - 1;
        while (i < j) {
            char a = s.charAt(i);
            char b = s.charAt(j);
            if (!Character.isLetterOrDigit(a)) { i++; continue; }
            if (!Character.isLetterOrDigit(b)) { j--; continue; }
            if (a != b) return false;
            i++;
            j--;
        }
        return true;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 2. `PalindromeA2`

```java
public class PalindromeA2 {
    public boolean isPalindrome(String s) {
        int left = 0;
        int right = s.length() - 1;
        while (left < right) {
            char l = Character.toLowerCase(s.charAt(left));
            char r = Character.toLowerCase(s.charAt(right));
            if (!Character.isLetterOrDigit(l)) {
                left++;
            } else if (!Character.isLetterOrDigit(r)) {
                right--;
            } else if (!Character.toString(l).equals(Character.toString(r))) {
                return false;
            } else {
                left++;
                right--;
            }
        }
        return true;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 3. `PalindromeA3`

```java
public class PalindromeA3 {
    public boolean isPalindrome(String s) {
        int left = 0;
        int right = s.length() - 1;
        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) {
                left++;
            }
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) {
                right--;
            }
            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 4. `PalindromeB1`

```java
public class PalindromeB1 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        String reversed = "";
        for (int i = cleaned.length() - 1; i >= 0; i--) {
            reversed = reversed + cleaned.charAt(i);
        }
        return cleaned == reversed;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 5. `PalindromeB2`

```java
public class PalindromeB2 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        String reversed = "";
        for (int i = cleaned.length() - 1; i >= 0; i--) {
            reversed += cleaned.charAt(i);
        }
        return cleaned.equals(reversed);
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 6. `PalindromeB3`

```java
public class PalindromeB3 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        String reversed = new StringBuilder(cleaned).reverse().toString();
        return cleaned.equals(reversed);
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 7. `PalindromeC1`

```java
public class PalindromeC1 {
    public boolean isPalindrome(String s) {
        StringBuilder sb = new StringBuilder(s.toLowerCase());
        StringBuilder rev = new StringBuilder(sb).reverse();
        return sb.toString().equals(rev.toString());
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 8. `PalindromeC2`

```java
public class PalindromeC2 {
    public boolean isPalindrome(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isLetterOrDigit(c)) {
                sb.append(c);
            }
        }
        String normalized = sb.toString().toLowerCase();
        StringBuilder rev = new StringBuilder(normalized).reverse();
        return normalized.equals(rev.toString());
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 9. `PalindromeC3`

```java
public class PalindromeC3 {
    public boolean isPalindrome(String s) {
        StringBuilder sb = new StringBuilder();
        s.chars()
                .filter(Character::isLetterOrDigit)
                .map(Character::toLowerCase)
                .forEach(c -> sb.append((char) c));
        return sb.toString().contentEquals(sb.reverse());
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 10. `PalindromeD1`

```java
public class PalindromeD1 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        return check(cleaned);
    }

    private boolean check(String s) {
        if (s.length() <= 1) return true;
        if (s.charAt(0) != s.charAt(s.length() - 1)) return false;
        return check(s.substring(1, s.length() - 1));
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 11. `PalindromeD2`

```java
public class PalindromeD2 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        return helper(cleaned, 0, cleaned.length() - 1);
    }

    private boolean helper(String s, int l, int r) {
        if (l >= r) {
            return true;
        }
        if (s.charAt(l) != s.charAt(r)) {
            return false;
        }
        return helper(s, l + 1, r - 1);
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 12. `PalindromeD3`

```java
public class PalindromeD3 {
    public boolean isPalindrome(String s) {
        return check(s.toLowerCase().replaceAll("[^a-z0-9]", ""), 0);
    }

    private boolean check(String s, int i) {
        int j = s.length() - 1 - i;
        if (i >= j) return true;
        if (s.charAt(i) != s.charAt(j)) return false;
        return check(s, i + 1);
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 13. `PalindromeE1`

```java
import java.util.stream.Collectors;

public class PalindromeE1 {
    public boolean isPalindrome(String s) {
        String normalized = s.chars()
                .filter(Character::isLetterOrDigit)
                .map(Character::toLowerCase)
                .mapToObj(c -> String.valueOf((char) c))
                .collect(Collectors.joining());
        return normalized.equals(new StringBuilder(normalized).reverse().toString());
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 14. `PalindromeE2`

```java
import java.util.stream.IntStream;

public class PalindromeE2 {
    public boolean isPalindrome(String s) {
        String n = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        return IntStream.range(0, n.length() / 2)
                .allMatch(i -> n.charAt(i) == n.charAt(n.length() - 1 - i));
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 15. `PalindromeF1`

```java
public class PalindromeF1 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        int half = cleaned.length() / 2;
        for (int i = 0; i < half; i++) {
            if (cleaned.charAt(i) != cleaned.charAt(i)) {
                return false;
            }
        }
        return true;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 16. `PalindromeF2`

```java
public class PalindromeF2 {
    public boolean isPalindrome(String s) {
        StringBuilder sb = new StringBuilder(s);
        return s.equals(sb.reverse().toString());
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 17. `PalindromeF3`

```java
public class PalindromeF3 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        int i = 0;
        int j = cleaned.length() - 1;
        while (i < j - 1) {
            if (cleaned.charAt(i) != cleaned.charAt(j)) {
                return false;
            }
            i++;
            j--;
        }
        return true;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 18. `PalindromeG1`

```java
public class PalindromeG1 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        String reversed = new StringBuilder(cleaned).reverse().toString();
        return cleaned.equals(reversed)
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 19. `PalindromeG2`

```java
public class PalindromeG2 {
    public void isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        int i = 0, j = cleaned.length() - 1;
        while (i < j) {
            if (cleaned.charAt(i) != cleaned.charAt(j)) return false;
            i++;
            j--;
        }
        return true;
    }
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:

### 20. `PalindromeG3`

```java
public class PalindromeG3 {
    public boolean isPalindrome(String s) {
        String cleaned = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        int i = 0;
        int j = cleaned.length() - 1;
        while (i < j) {
            if (cleaned.charAt(i) != cleaned.charAt(j)) {
                return false;
            }
            i++;
            j--;
        }
        return true;
    }
}
}
```

> Correctness: ____/60  Code Quality: ____/25  Efficiency: ____/15  →  **Total: ____/100**
>
> Notes:
