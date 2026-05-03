import java.util.stream.IntStream;

public class PalindromeE2 {
    public boolean isPalindrome(String s) {
        String n = s.toLowerCase().replaceAll("[^a-z0-9]", "");
        return IntStream.range(0, n.length() / 2)
                .allMatch(i -> n.charAt(i) == n.charAt(n.length() - 1 - i));
    }
}
