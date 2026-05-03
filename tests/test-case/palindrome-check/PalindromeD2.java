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
