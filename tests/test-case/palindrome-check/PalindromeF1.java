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
