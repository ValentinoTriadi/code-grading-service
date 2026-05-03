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
