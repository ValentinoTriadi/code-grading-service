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
