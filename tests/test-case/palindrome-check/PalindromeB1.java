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
