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
