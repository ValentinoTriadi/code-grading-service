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
